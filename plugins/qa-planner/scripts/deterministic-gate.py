#!/usr/bin/env python3
"""qa-planner — 결정론 게이트.

품질 루프 축 중 **결정론으로 판정 가능한 축**만 본다.
서술 판정(정합성 뉘앙스·명료성 이해도·코드정합성)은 planner-critic + rubric이 별도로 맡는다.

입력: gate-input.json (계약 = knowledge/planner-loop-audit-log.schema.md §1)
판정 축:
    - 완전성      : 모든 요구 id가 delta 항목에 1건 이상 매핑
    - 추적성      : 모든 delta 항목에 source 링크 존재
    - iso_coverage: 모든 delta 항목의 iso_triage가 8특성을 모두 포함 + applicable 이 진짜 bool
    - na_reason   : applicable:false 특성마다 na_reason 존재
    - 정합성_결정론: cross_doc_claims의 값이 문서 간 일치
                    + screens[] 존재 시 화면 연결성(schema §1-3)
                    + frs[] 존재 시 FR 연결성(POST — schema §1-4)

추가로 markers(3종 세트 필수)를 집계해 clean 자격을 판정한다.
clean_eligible = 5축 전부 pass AND 미해소 마커([추정]·[미확정]·[충돌]) 0건.
(크리틱 pass 와의 AND 결합은 오케스트레이터 몫 — schema §2-4)

출력: 판정 결과 JSON을 stdout에 (loop-audit-log iteration 레코드의
      deterministic_gate 필드에 그대로 넣을 수 있는 형태 — overall·marker_counts·clean_eligible 포함).

Usage:
    python deterministic-gate.py <gate-input.json 경로>

Exit code:
    0 = clean 자격 (5축 pass AND 마커 0)
    1 = 미달 (1축 이상 fail) 또는 미해소 마커 잔존
    2 = 인자 오류 · 파일 부재 · 스키마 필수 필드 누락(markers 3종 세트 포함)
"""
import json
import sys
from pathlib import Path

# Windows cp949 회피 — stdout/stderr UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ISO_8 = [
    "functional_suitability",
    "performance_efficiency",
    "compatibility",
    "usability",
    "reliability",
    "security",
    "maintainability",
    "portability",
]

MARKER_KEYS = {"[추정]", "[미확정]", "[충돌]"}


def die(msg, code=2):
    print(f"[deterministic-gate] ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def load(path):
    p = Path(path)
    if not p.is_file():
        die(f"파일 부재: {path}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        die(f"JSON 파싱 실패: {e}")


def require(data, keys):
    for k in keys:
        if k not in data:
            die(f"필수 필드 누락: {k}")


def check_completeness(data):
    """완전성 — 모든 요구 id가 1건 이상 delta에 매핑."""
    reqs = set(data["urs_requirements"])
    mapped = set()
    for item in data["delta_items"]:
        mapped.update(item.get("urs_refs", []))
    unmapped = sorted(reqs - mapped)
    return ("pass" if not unmapped else "fail", {"unmapped_urs": unmapped})


def check_traceability(data):
    """추적성 — 모든 delta 항목에 source 링크 존재."""
    missing = [
        item["id"]
        for item in data["delta_items"]
        if not item.get("source_links")
    ]
    return ("pass" if not missing else "fail", {"no_source_link": missing})


def check_iso_and_na(data):
    """iso_coverage(8특성 전수 + applicable 타입 강제) + na_reason(사유 박제)."""
    iso_fail, na_fail, notices = [], [], []
    for item in data["delta_items"]:
        triage = {t.get("characteristic"): t for t in item.get("iso_triage", [])}
        missing = [c for c in ISO_8 if c not in triage]
        if missing:
            iso_fail.append({"delta_id": item["id"], "missing": missing})
        for c, t in triage.items():
            if c not in ISO_8:
                iso_fail.append({"delta_id": item["id"], "unknown_characteristic": c})
                continue
            app = t.get("applicable")
            # applicable 은 필수 + 진짜 bool 이어야 함 (없거나 "false" 문자열 = 조용한 제외 차단)
            if not isinstance(app, bool):
                iso_fail.append({"delta_id": item["id"], "characteristic": c, "bad_applicable": app})
                continue
            if app is False and not t.get("na_reason"):
                na_fail.append({"delta_id": item["id"], "characteristic": c})
        sec = triage.get("security")
        if isinstance(sec, dict) and sec.get("applicable") is False:
            notices.append({"delta_id": item["id"], "security_na_reason": sec.get("na_reason", "")})
    iso_status = "pass" if not iso_fail else "fail"
    na_status = "pass" if not na_fail else "fail"
    detail = {"iso_gaps": iso_fail, "na_reason_missing": na_fail}
    if notices:
        detail["security_na_notice"] = notices  # 보안 N/A는 사람 검토 유도(21 CFR Part 11)
    return iso_status, na_status, detail


def check_markers(data):
    """미해소 마커 집계 → clean 자격 판정 재료.

    세 마커(`[추정]`·`[미확정]`·`[충돌]`) 중 하나라도 잔존하면 clean 아님(flagged).
    부분입력·충돌·추론값은 검토 단계가 봐야 한다.
    """
    markers = data.get("markers")
    if not isinstance(markers, dict) or set(markers.keys()) != MARKER_KEYS:
        die(f"markers 는 3종 키({sorted(MARKER_KEYS)}) 모두 필수 — 현재 {sorted(markers.keys()) if isinstance(markers, dict) else markers}")
    counts = {k: len(markers[k]) for k in MARKER_KEYS}
    unresolved = sum(counts.values())
    return counts, unresolved


def check_consistency(data):
    """정합성(결정론) — cross_doc_claims의 값이 문서 간 일치."""
    conflicts = []
    for claim in data.get("cross_doc_claims", []):
        values = claim.get("values", {})
        distinct = set(values.values())
        if len(distinct) > 1:
            conflicts.append({"key": claim.get("key"), "values": values})
    return ("pass" if not conflicts else "fail", {"conflicts": conflicts})


def _delta_matches(ref, delta_ids):
    """implements ref ↔ delta id 매칭 — 정확 일치 또는 delta id가 '{ref}-' 접두 (schema §1-3)."""
    return any(d == ref or d.startswith(ref + "-") for d in delta_ids)


def _check_entity_links(data, entities, refs_field, label):
    """연결성(결정론) 공통 — 항목 목록({id, implements[]}) 존재 시
    id 유일성 + delta↔항목 양방향 참조 해소를 검사한다.

    screens[] (화면 — schema §1-3)와 frs[] (POST 기능정의서 delta — schema §1-4)가
    같은 규칙을 공유한다. 결과는 정합성_결정론 축에 합산.
    """
    problems = []
    entity_ids = [s.get("id") for s in entities]
    dup = sorted({sid for sid in entity_ids if entity_ids.count(sid) > 1})
    if dup:
        problems.append({"type": f"duplicate_{label}_id", "ids": dup})

    entity_set = set(entity_ids)
    delta_ids = [item["id"] for item in data["delta_items"]]

    # delta → 항목: 참조한 id가 목록에 실재해야 한다
    for item in data["delta_items"]:
        for ref in item.get(refs_field, []) or []:
            if ref not in entity_set:
                problems.append({"type": f"dangling_{label}_ref", "delta_id": item["id"], "ref": ref})

    # 항목 → delta: 역참조(implements)의 id가 delta 항목에 실재해야 한다
    for s in entities:
        for ref in s.get("implements", []) or []:
            if not _delta_matches(ref, delta_ids):
                problems.append({"type": "dangling_implements", f"{label}_id": s.get("id"), "ref": ref})

    # 양방향 일치: delta가 항목을 가리키면 그 항목의 implements에도 delta가 있어야 하고, 그 반대도
    implements_by_id = {s.get("id"): (s.get("implements", []) or []) for s in entities}
    for item in data["delta_items"]:
        for ref in item.get(refs_field, []) or []:
            if ref in implements_by_id and not any(
                item["id"] == r or item["id"].startswith(r + "-")
                for r in implements_by_id[ref]
            ):
                problems.append({"type": "missing_backref", f"{label}_id": ref, "delta_id": item["id"]})
    for s in entities:
        for ref in s.get("implements", []) or []:
            matched = [item for item in data["delta_items"] if item["id"] == ref or item["id"].startswith(ref + "-")]
            for item in matched:
                if s.get("id") not in (item.get(refs_field, []) or []):
                    problems.append({"type": "missing_forward_ref", "delta_id": item["id"], f"{label}_id": s.get("id")})
    return problems


def check_screen_links(data):
    """screens[] 존재 시 화면 연결성 검사. 부재 = 화면 미산출 런 → 생략(백워드 컴팻)."""
    screens = data.get("screens")
    if screens is None:
        return "pass", {}
    problems = _check_entity_links(data, screens, "screen_refs", "screen")
    status = "pass" if not problems else "fail"
    detail = {"screen_link_conflicts": problems} if problems else {}
    return status, detail


def check_fr_links(data):
    """frs[] 존재 시 FR 연결성 검사(POST — 기능정의서 delta ↔ 정책정의서/delta 항목).
    부재 = FR 미산출 → 생략(백워드 컴팻, schema §1-4)."""
    frs = data.get("frs")
    if frs is None:
        return "pass", {}
    problems = _check_entity_links(data, frs, "fr_refs", "fr")
    status = "pass" if not problems else "fail"
    detail = {"fr_link_conflicts": problems} if problems else {}
    return status, detail


def main():
    if len(sys.argv) != 2:
        die("사용법: python deterministic-gate.py <gate-input.json>")
    data = load(sys.argv[1])
    require(data, ["urs_requirements", "delta_items", "run_id", "iteration", "markers"])
    if not data["delta_items"]:
        die("delta_items 비어 있음 — 저술 결과가 없다(빈 배열 금지)")

    comp, comp_d = check_completeness(data)
    trace, trace_d = check_traceability(data)
    iso, na, iso_d = check_iso_and_na(data)
    cons, cons_d = check_consistency(data)
    links, links_d = check_screen_links(data)
    fr_links, fr_links_d = check_fr_links(data)
    if links == "fail" or fr_links == "fail":
        cons = "fail"  # 연결성은 정합성_결정론 축에 합산 (축 세트 불변 — schema §1-3·§1-4)
    cons_d = {**cons_d, **links_d, **fr_links_d}
    marker_counts, unresolved = check_markers(data)

    axes = {
        "완전성": comp,
        "추적성": trace,
        "iso_coverage": iso,
        "na_reason": na,
        "정합성_결정론": cons,
    }
    overall = "pass" if all(v == "pass" for v in axes.values()) else "fail"
    # clean 자격 = 5축 전부 pass AND 미해소 마커 0건 (크리틱 pass 는 오케스트레이터가 AND 결합)
    clean_eligible = overall == "pass" and unresolved == 0

    result = {
        "run_id": data["run_id"],
        "iteration": data["iteration"],
        **axes,
        "overall": overall,
        "marker_counts": marker_counts,
        "unresolved_markers_total": unresolved,
        "clean_eligible": clean_eligible,
        "detail": {**comp_d, **trace_d, **iso_d, **cons_d},
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    # exit 0 = clean 자격(전축 pass + 마커 0), 1 = 미달 또는 마커 잔존
    sys.exit(0 if clean_eligible else 1)


if __name__ == "__main__":
    main()
