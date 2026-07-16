#!/usr/bin/env python3
"""qa-planner — loop-audit-log.jsonl 스키마 검증.

계약 = knowledge/planner-loop-audit-log.schema.md §2.
append-only 감사로그가 스키마를 지키는지, 상태 결정 규칙이 맞는지 검사한다.

검사 항목:
    - 각 줄이 유효 JSON
    - record_type 은 iteration | terminal
    - run_id 가 전 레코드 동일
    - iteration 레코드 필수 필드(input_hash·draft_hash·critic_scores·failed_axes·
      fix_summary 포함) 존재 + iteration 번호 1부터 연속 증가
    - terminal 레코드는 정확히 1개, 마지막 줄
    - final_status ∈ {clean, flagged, blocked}, stop_reason enum
    - unresolved_markers 는 3종 키 모두 존재
    - 상태 결정 규칙 교차검증 (schema §2-4, false pass 차단):
        · blocked → iteration 0개 + stop_reason=input_insufficient
        · clean   → stop_reason=gate_pass + 미해소 마커 0 +
                    마지막 iteration clean_eligible=true +
                    크리틱 전 축 ≥4 (정합성·명료성 + rubric v2면 코드정합성 포함)
        · 그 외   → iteration 1개 이상

Usage:
    python validate-audit-log.py <loop-audit-log.jsonl 경로>

Exit code:
    0 = PASS
    1 = 스키마 위반 (위반 목록 출력)
    2 = 인자 오류 · 파일 부재
"""
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ITER_REQUIRED = [
    "record_type", "run_id", "iteration", "executor", "model",
    "rubric_version", "max_n", "input_hash", "draft_hash",
    "deterministic_gate", "critic_scores", "failed_axes",
    "fix_summary", "timestamp",
]
TERMINAL_REQUIRED = [
    "record_type", "run_id", "final_status", "stop_reason",
    "unresolved_markers", "timestamp",
]
FINAL_STATUS = {"clean", "flagged", "blocked"}
STOP_REASON = {"gate_pass", "max_n", "no_progress", "input_insufficient"}
MARKER_KEYS = {"[추정]", "[미확정]", "[충돌]"}
# clean 판정 시 크리틱 필수 축 — rubric 버전별 (schema §2-4)
CRITIC_AXES_BY_RUBRIC = {
    "v1": ["정합성", "명료성"],
    "v2": ["정합성", "명료성", "코드정합성"],
}


def die(msg):
    print(f"[validate-audit-log] ERROR: {msg}", file=sys.stderr)
    sys.exit(2)


def main():
    if len(sys.argv) != 2:
        die("사용법: python validate-audit-log.py <loop-audit-log.jsonl>")
    p = Path(sys.argv[1])
    if not p.is_file():
        die(f"파일 부재: {sys.argv[1]}")

    errors = []
    records = []
    for lineno, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            records.append((lineno, json.loads(line)))
        except json.JSONDecodeError as e:
            errors.append(f"line {lineno}: JSON 파싱 실패 — {e}")

    if not records:
        errors.append("레코드 0건")
        _report(errors)

    run_ids = set()
    iter_records = []
    terminal_records = []
    for lineno, rec in records:
        rt = rec.get("record_type")
        run_ids.add(rec.get("run_id"))
        if rt == "iteration":
            iter_records.append((lineno, rec))
            for k in ITER_REQUIRED:
                if k not in rec:
                    errors.append(f"line {lineno}: iteration 필수 필드 누락 — {k}")
            dg = rec.get("deterministic_gate", {})
            if "overall" not in dg:
                errors.append(f"line {lineno}: deterministic_gate.overall 누락")
            # clean_eligible 내부 일관성 재계산 (조작·오기록 로그 차단 — 무결성 검증기)
            ce = dg.get("clean_eligible")
            ov = dg.get("overall")
            tot = dg.get("unresolved_markers_total")
            if ce is not None:
                if isinstance(tot, int):
                    expected = (ov == "pass") and (tot == 0)
                    if ce != expected:
                        errors.append(
                            f"line {lineno}: clean_eligible({ce}) 가 overall({ov})·미해소마커({tot})와 불일치 — 재계산값 {expected}"
                        )
                elif ce is True and ov != "pass":
                    errors.append(f"line {lineno}: clean_eligible=true 인데 overall != pass ({ov})")
        elif rt == "terminal":
            terminal_records.append((lineno, rec))
            for k in TERMINAL_REQUIRED:
                if k not in rec:
                    errors.append(f"line {lineno}: terminal 필수 필드 누락 — {k}")
            if rec.get("final_status") not in FINAL_STATUS:
                errors.append(f"line {lineno}: final_status enum 위반 — {rec.get('final_status')}")
            if rec.get("stop_reason") not in STOP_REASON:
                errors.append(f"line {lineno}: stop_reason enum 위반 — {rec.get('stop_reason')}")
            markers = rec.get("unresolved_markers", {})
            if set(markers.keys()) != MARKER_KEYS:
                errors.append(f"line {lineno}: unresolved_markers 키가 3종 세트와 불일치 — {sorted(markers.keys())}")
        else:
            errors.append(f"line {lineno}: record_type 위반 — {rt}")

    # run_id 단일
    if len(run_ids) > 1:
        errors.append(f"run_id 불일치(전 레코드 동일해야 함): {sorted(run_ids)}")

    # terminal 정확히 1개 + 마지막 줄
    if len(terminal_records) != 1:
        errors.append(f"terminal 레코드는 정확히 1개여야 함 — 현재 {len(terminal_records)}개")
    elif terminal_records[0][0] != records[-1][0]:
        errors.append("terminal 레코드는 마지막 줄이어야 함")

    # iteration 번호 1부터 연속
    nums = [rec.get("iteration") for _, rec in iter_records]
    if nums and nums != list(range(1, len(nums) + 1)):
        errors.append(f"iteration 번호가 1부터 연속 증가가 아님: {nums}")

    # 상태 결정 규칙 교차검증 (schema §2-4 — false pass 차단)
    if len(terminal_records) == 1:
        term = terminal_records[0][1]
        final = term.get("final_status")
        stop = term.get("stop_reason")
        markers = term.get("unresolved_markers", {})
        if final == "blocked":
            # blocked = 입력 불충분으로 저술 미진입 → iteration 레코드 없어야 함
            if iter_records:
                errors.append("final_status=blocked 인데 iteration 레코드 존재 — blocked 는 저술 미진입")
            if stop != "input_insufficient":
                errors.append(f"final_status=blocked 인데 stop_reason != input_insufficient — {stop}")
        else:
            if not iter_records:
                errors.append(f"final_status={final} 인데 iteration 레코드 0건")
        if final == "clean":
            if stop != "gate_pass":
                errors.append(f"final_status=clean 인데 stop_reason != gate_pass — {stop}")
            # 미해소 마커 잔존하면 clean 불가
            if isinstance(markers, dict) and any(markers.get(k) for k in MARKER_KEYS):
                errors.append("final_status=clean 인데 미해소 마커 잔존 — clean 불가(flagged 여야 함)")
            if iter_records:
                last = iter_records[-1][1]
                dg = last.get("deterministic_gate", {})
                if dg.get("clean_eligible") is not True:
                    errors.append("final_status=clean 인데 마지막 iteration deterministic_gate.clean_eligible != true")
                # 크리틱 전 축 ≥4 — rubric 버전에 따라 필수 축 결정 (v2 = 코드정합성 포함, schema §2-4)
                cs = last.get("critic_scores", {})
                rubric = last.get("rubric_version", "v1")
                required_axes = CRITIC_AXES_BY_RUBRIC.get(rubric, CRITIC_AXES_BY_RUBRIC["v1"])
                for axis in required_axes:
                    score = _score(cs.get(axis))
                    if not (score is not None and score >= 4):
                        errors.append(
                            f"final_status=clean 인데 크리틱 {axis} ≥4 아님 — {axis}={score} (rubric {rubric})"
                        )

    _report(errors)


def _score(axis):
    """critic_scores 축 객체에서 score 숫자 추출 (없으면 None)."""
    if isinstance(axis, dict) and isinstance(axis.get("score"), (int, float)):
        return axis["score"]
    return None


def _report(errors):
    if errors:
        print("FAIL — 스키마 위반:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("PASS — loop-audit-log 스키마 정합")
    sys.exit(0)


if __name__ == "__main__":
    main()
