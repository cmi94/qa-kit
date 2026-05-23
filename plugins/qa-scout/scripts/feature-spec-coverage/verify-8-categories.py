#!/usr/bin/env python3
"""qa-scout v0.3.0 — feature-spec.md §1 8 카테고리 강제 검증 스크립트.

SDD §4-2 + §4-2-3 정합. 단계 9c.6 자가 검증 #4 항목.

각 §1 FR의 17 컬럼 vertical table 9번 row(상세 정책 / 기능 설명)에
8단 bullet(`핵심 룰·경계 조건·상태 전이·권한 게이트·데이터 무결성·
화면 동작·부수 효과·참조`)이 모두 존재하는지 grep.

자료 부재 시 통일 마커 `[자료 부족] (카테고리명 — 확인한 입력)` 형식
허용. 자유 흐름 cell 또는 dash-only는 FAIL.

Usage:
    python verify-8-categories.py <feature-spec.md 경로>

Exit code:
    0 = PASS (모든 FR에 8 bullet 존재)
    1 = FAIL (1건 이상 미존재)
    2 = 인자 오류 또는 파일 부재
"""
import re
import sys

# Windows cp949 회피 — stdout/stderr UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
import unicodedata
from pathlib import Path

REQUIRED_CATEGORIES = [
    "핵심 룰",
    "경계 조건",
    "상태 전이",
    "권한 게이트",
    "데이터 무결성",
    "화면 동작",
    "부수 효과",
    "참조",
]

# §1 FR 헤더 패턴: `#### FR-<PROJECT>-NNN: <name>` (FR ID prefix는 프로젝트별)
FR_HEADER_RE = re.compile(r"^####\s+(FR-[A-Z_]+-\d+)\s*[:：]", re.MULTILINE)

# §1 행은 17 컬럼 vertical table — `| 9 | 상세 정책 / 기능 설명 | <8 bullet> |`
# table row cell 추출 — 9번 row의 값 컬럼 (3번째 컬럼)
DETAIL_POLICY_ROW_RE = re.compile(
    r"^\|\s*9\s*\|\s*상세\s*정책[^|]*?\|\s*(.+?)\s*\|\s*$",
    re.MULTILINE,
)


def verify(spec_path: Path) -> dict:
    """feature-spec.md §1 8 카테고리 강제 검증."""
    if not spec_path.exists():
        return {"error": f"파일 부재: {spec_path}"}

    text = spec_path.read_text(encoding="utf-8")

    # 1. FR 행 추출 — header + 17 row vertical table 블록
    fr_matches = list(FR_HEADER_RE.finditer(text))
    fr_blocks = []
    for i, m in enumerate(fr_matches):
        fr_id = m.group(1)
        start = m.start()
        end = fr_matches[i + 1].start() if i + 1 < len(fr_matches) else len(text)
        fr_blocks.append((fr_id, text[start:end]))

    if not fr_blocks:
        return {"error": "§1 FR 헤더 0건 — feature-spec.md §1 본문 확인 필요"}

    # 2. 각 FR의 상세 정책 cell 추출 + 8 카테고리 grep
    failures = []
    for fr_id, block in fr_blocks:
        policy_match = DETAIL_POLICY_ROW_RE.search(block)
        if not policy_match:
            failures.append({
                "fr_id": fr_id,
                "category": "(전체)",
                "type": "row_missing",
                "detail": "9번 row(상세 정책 / 기능 설명) 미발견",
            })
            continue

        policy_cell = unicodedata.normalize("NFC", policy_match.group(1))

        # bullet pattern: `• 카테고리명:` (NFC 정규화 후 매칭). set equality로 검증.
        BULLET_RE = re.compile(r"•\s*([^:：\n]+?)\s*[:：]")
        found_categories = {m.group(1).strip() for m in BULLET_RE.finditer(policy_cell)}
        required = set(REQUIRED_CATEGORIES)
        missing = required - found_categories
        extra = found_categories - required

        for cat in REQUIRED_CATEGORIES:
            if cat in missing:
                failures.append({
                    "fr_id": fr_id,
                    "category": cat,
                    "type": "bullet_missing",
                    "detail": f"`• {cat}:` bullet 미존재",
                })
        if extra:
            failures.append({
                "fr_id": fr_id,
                "category": "(extra)",
                "type": "bullet_extra",
                "detail": f"규정 외 카테고리 bullet 발견: {sorted(extra)}",
            })

    return {
        "total_fr": len(fr_blocks),
        "failures": failures,
        "pass": len(failures) == 0,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify-8-categories.py <feature-spec.md 경로>", file=sys.stderr)
        sys.exit(2)

    spec_path = Path(sys.argv[1])
    result = verify(spec_path)

    if "error" in result:
        print(f"ERROR: {result['error']}", file=sys.stderr)
        sys.exit(2)

    if result["pass"]:
        print(f"PASS — {result['total_fr']} FR × 8 카테고리 모두 발견")
        sys.exit(0)
    else:
        print(
            f"FAIL — {result['total_fr']} FR 중 {len(result['failures'])}건 미존재",
            file=sys.stderr,
        )
        for f in result["failures"][:30]:
            print(f"  - {f['fr_id']}: {f['detail']}", file=sys.stderr)
        if len(result["failures"]) > 30:
            print(f"  ... + {len(result['failures']) - 30}건 추가", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
