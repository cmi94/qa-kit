#!/usr/bin/env python3
"""docs-to-policy-spec v1.0 — 정책정의서 draft 결정론 검증.

스킬 자가 검증(발행 전) 항목.

기능정의서에서 파생한 정책 draft(11컬럼 delta 양식)를 프로젝트 무관하게 검증한다.
프로젝트 상수(id_prefix·fr_prefix·대역)는 전부 config에서 읽는다 — 스크립트에 하드코딩 없음.

Usage:
    python validate-policy-spec.py --draft <draft.md> --config <band-config.yaml> \
        --funcspec <feature-spec.md 또는 기능정의서_master.csv>

Exit code:
    0 = PASS (전 항목 통과)
    1 = FAIL (1건 이상 위반)
    2 = 인자 오류 / 파일 부재 / config 파손
"""
import argparse
import re
import sys
from pathlib import Path

# Windows cp949 회피 — stdout/stderr UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# 마스터 8 핵심 컬럼 (정책정의서_master.csv 헤더와 1:1)
MASTER_COLS = [
    "정책 ID", "정책 구분", "정책명", "정책 목표",
    "정책 내용 및 기준", "적용 범위", "관련 FR", "비고",
]
# draft 11컬럼 delta 양식 (앞 변경 유형 + 8 핵심 + 뒤 근거·마커)
DRAFT_COLS = ["변경 유형"] + MASTER_COLS + ["근거", "마커"]

THREE_ELEMENTS = ["정책 목표", "적용 범위", "정책 내용 및 기준"]
FR_NUM = re.compile(r"FR-(?:[A-Za-z]+-)?(\d+)")


def die(msg, code=2):
    print(f"[ERROR] {msg}")
    sys.exit(code)


def load_config(path):
    """band config yaml 로드. pyyaml 있으면 사용, 없으면 최소 파서."""
    text = Path(path).read_text(encoding="utf-8")
    try:
        import yaml
        return yaml.safe_load(text)
    except ImportError:
        die("pyyaml 필요 — pip install pyyaml (config 파싱)")


def parse_md_table(path):
    """md 파일에서 정책 draft 표를 찾아 (헤더, 데이터행 dict 리스트) 반환."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    header = None
    rows = []
    for ln in lines:
        s = ln.strip()
        if not s.startswith("|"):
            if header and rows:
                break  # 표 끝
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        # 구분선(---) 건너뛰기
        if all(set(c) <= {"-", ":", " "} and c for c in cells):
            continue
        if header is None:
            if "정책 ID" in cells and "정책명" in cells:
                header = cells
            continue
        if len(cells) == len(header):
            rows.append(dict(zip(header, cells)))
    if header is None:
        die("정책 draft 표를 찾지 못함 (헤더에 '정책 ID'·'정책명' 필요)")
    return header, rows


def fr_numbers(text):
    return {int(n) for n in FR_NUM.findall(text or "")}


def band_for_category(bands, category):
    for b in bands:
        if b.get("policy_category") == category:
            return b
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--funcspec", required=True)
    args = ap.parse_args()

    for p in (args.draft, args.config, args.funcspec):
        if not Path(p).exists():
            die(f"파일 부재: {p}")

    cfg = load_config(args.config)
    bands = cfg.get("bands") or []
    id_prefix = cfg.get("id_prefix", "")
    if not bands or not id_prefix:
        die("config에 id_prefix·bands 필수")

    funcspec_fr = fr_numbers(Path(args.funcspec).read_text(encoding="utf-8"))
    if not funcspec_fr:
        die("기능정의서에서 FR id를 찾지 못함 (파생 소스 확인)")

    header, rows = parse_md_table(args.draft)
    fails = []

    # 1. 8 핵심 컬럼 헤더 1:1 일치
    core = [c for c in header if c in MASTER_COLS]
    if core != MASTER_COLS:
        fails.append(f"[1] 핵심 컬럼 헤더 불일치: {core} != {MASTER_COLS}")

    seen_ids = {}
    id_pat = re.compile(rf"^{re.escape(id_prefix)}(\d+)$")
    body_count = 0

    for i, r in enumerate(rows, 1):
        marker = r.get("마커", "")
        # 5. [원본필요] 행은 본문 정책 행이 될 수 없음
        if "원본필요" in marker:
            fails.append(f"[5] 행{i}: [원본필요]는 비고 후보만 허용 — 본문 정책 행 금지 ({r.get('정책 ID','?')})")
            continue
        body_count += 1

        pid = r.get("정책 ID", "").strip()
        m = id_pat.match(pid)
        # 3. 정책 ID 형식·대역·중복
        if not m:
            fails.append(f"[3] 행{i}: 정책 ID 형식 위반 '{pid}' (기대 {id_prefix}NNN)")
        else:
            num = int(m.group(1))
            if pid in seen_ids:
                fails.append(f"[3] 행{i}: 정책 ID 중복 '{pid}' (행{seen_ids[pid]})")
            seen_ids[pid] = i
            band = band_for_category(bands, r.get("정책 구분", ""))
            if band is None:
                fails.append(f"[3] 행{i}: 정책 구분 '{r.get('정책 구분')}' 이 config 대역에 없음")
            else:
                lo, hi = band["id_range"]
                if not (lo <= num <= hi):
                    fails.append(f"[3] 행{i}: {pid} 이 '{band['policy_category']}' 대역 {lo}~{hi} 밖")

        # 2. 관련 FR 실재 (유령 0) / 빈 값이면 비고 사유 필수
        fr_cell = r.get("관련 FR", "").strip()
        note = r.get("비고", "").strip()
        if not fr_cell or fr_cell == "—":
            if not note or note == "—":
                fails.append(f"[2] 행{i}: {pid} 관련 FR 비었는데 비고 사유 없음")
        else:
            for n in fr_numbers(fr_cell):
                if n not in funcspec_fr:
                    fails.append(f"[2] 행{i}: {pid} 관련 FR 유령 (기능정의서에 FR-{n:03d} 없음)")

        # 4. 3요소 빈 셀 0 (또는 [자료 부족])
        for col in THREE_ELEMENTS:
            v = r.get(col, "").strip()
            if not v or v == "—":
                fails.append(f"[4] 행{i}: {pid} '{col}' 빈 셀 (3요소 필수, 없으면 [자료 부족] 마커)")

    print(f"검사 대상: draft {args.draft}")
    print(f"본문 정책 행: {body_count} · 기능정의서 FR: {len(funcspec_fr)}개 · 대역: {len(bands)}")
    if fails:
        print(f"\nFAIL — 위반 {len(fails)}건:")
        for f in fails:
            print(f"  {f}")
        sys.exit(1)
    print("\nPASS — 전 항목 통과")
    sys.exit(0)


if __name__ == "__main__":
    main()
