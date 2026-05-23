#!/usr/bin/env python3
"""qa-scout v0.3.0 — D-3 Readback Diff 차단 게이트 (단계 17b post-publish).

SDD §4-3 D-3 차단 게이트 정합. markdown-to-sheets 발행 직후 즉시
get_sheet_data 재조회 결과(JSON 파일)와 로컬 source JSON을 cell-by-cell
syllable-level diff (Unicode NFC 정규화 후 비교). 옵션별 col count 정합
검증 포함.

본 스크립트는 실제 MCP `get_sheet_data` 호출은 하지 않음 (Claude/호출자가
미리 sheet_data.json으로 fetch 후 본 스크립트에 전달). 분리 패턴으로
스크립트 단독 테스트 가능.

Usage:
    # 1. Claude가 mcp__google-sheets__get_sheet_data 호출해서
    #    sheet_data.json 으로 dump
    # 2. 본 스크립트로 diff:
    python verify-readback.py \\
        --source-json section1_rows.json \\
        --sheet-data-json sheet_data.json \\
        --sheets-option C

Exit code:
    0 = PASS (diff 0건)
    1 = FAIL (diff 1건 이상)
    2 = 인자 오류 또는 file 부재 또는 schema 오류

호출자 처리 룰 (SDD §4-3-2·§4-3-5 정합):
    exit 0 → published=true + share_spreadsheet + scout-log entry
    exit 1 → published=false 유지 + share_spreadsheet 금지 + 명인 diff 보고
    명인 승인 후 D-1/D-2 경로 재시도. Auto-Healing Loop 차단
    ([[bridge-wrapping-pattern]] 메모리 준수).
"""
import argparse
import json
import sys
import unicodedata
from pathlib import Path


def expected_col_count(sheets_option: str) -> int:
    """§4-3-1 sheets_option 정합 검증."""
    return 18 if sheets_option == "D" else 17


def col_letter(idx: int) -> str:
    """0-indexed col → letter (A~Z만 지원, 본 SDD 범위 충분)."""
    return chr(ord("A") + idx)


def diff_syllables(a: str, b: str) -> list:
    """한글 syllable 단위 diff — NFC 분해 후 자모별 비교 (단순 SequenceMatcher 기반).

    Returns: [{"position": int, "expected": str, "actual": str}, ...]
    """
    from difflib import SequenceMatcher
    matcher = SequenceMatcher(None, a, b)
    diffs = []
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "equal":
            continue
        diffs.append({
            "op": op,  # replace / delete / insert
            "expected_pos": [i1, i2],
            "expected_segment": a[i1:i2],
            "actual_pos": [j1, j2],
            "actual_segment": b[j1:j2],
        })
    return diffs


def readback_diff_gate(source_json_path: Path, sheet_data_json_path: Path, sheets_option: str) -> dict:
    """D-3 Readback Diff 게이트 핵심 로직.

    Args:
        source_json_path: 로컬 source rows JSON ({"rows": [[<cells>], ...]})
        sheet_data_json_path: MCP get_sheet_data dump JSON ({"values": [[<header>], [<row1>], ...]})
        sheets_option: A | B | C | D

    Returns: {"pass": bool, "diff_list": [...], "src_meta": {...}, "sheet_meta": {...}}
    """
    # 1. source JSON load
    try:
        src = json.loads(source_json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {"error": f"source JSON parse 실패: {e}"}

    src_rows = src.get("rows", [])
    if not isinstance(src_rows, list) or not src_rows:
        return {"error": "source JSON에 'rows' 배열 부재 또는 빈 배열"}

    src_row_count = len(src_rows)
    src_col_count = len(src_rows[0])

    # 1-b. source rows 일관성 검증 (v0.2 audit F-002 정정) — 모든 row col count == src_col_count
    src_row_inconsistencies = []
    for ri, r in enumerate(src_rows):
        if len(r) != src_col_count:
            src_row_inconsistencies.append({
                "row_index": ri,
                "expected_col_count": src_col_count,
                "actual_col_count": len(r),
            })
    if src_row_inconsistencies:
        return {
            "pass": False,
            "diff_list": [{
                "type": "source_row_col_count_inconsistent",
                "remediation": "source JSON rows 일관성 깨짐 — 모든 row가 동일 col count 필요",
                "inconsistencies": src_row_inconsistencies,
            }],
        }

    # 2. sheets_option ↔ src_col_count 정합 검증 (§4-3-1 1-a 단계)
    exp_col = expected_col_count(sheets_option)
    if src_col_count != exp_col:
        return {
            "pass": False,
            "diff_list": [{
                "type": "option_col_count_mismatch",
                "sheets_option": sheets_option,
                "expected_col_count": exp_col,
                "actual_col_count": src_col_count,
                "remediation": (
                    f"sheets_option={sheets_option} 발행은 src col {exp_col}개 필요. "
                    "source JSON 양식 확인 필요."
                ),
            }],
        }

    # 3. sheet data JSON load (MCP get_sheet_data dump)
    try:
        sheet = json.loads(sheet_data_json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {"error": f"sheet data JSON parse 실패: {e}"}

    sheet_values = sheet.get("values", [])
    if not isinstance(sheet_values, list):
        return {"error": "sheet data JSON에 'values' 배열 부재"}

    # 4. row·col bounds — exact cardinality 강제 (v0.2 audit F-001 정정)
    last_row_index = src_row_count + 1  # header 1 + data rows
    bounds_issues = []

    # 4-a. row count exact match — 짧으면 미발행 / 길면 stale row 잔존
    if len(sheet_values) != last_row_index:
        bounds_issues.append({
            "type": "row_count_mismatch",
            "expected": last_row_index,
            "actual": len(sheet_values),
            "remediation": (
                "시트 row 수가 source와 정확히 일치 안 함 — "
                f"{'발행 미완료' if len(sheet_values) < last_row_index else 'stale row 잔존 (이전 발행분 미정리)'}"
            ),
        })

    # 4-b. 각 data row col count exact match — 짧으면 부족 / 길면 옵션 불일치 (예: 옵션 C 시트에 18 컬럼 잔존)
    for ri, sheet_row in enumerate(sheet_values[1:1 + src_row_count]):
        if len(sheet_row) != src_col_count:
            bounds_issues.append({
                "type": "col_count_mismatch",
                "row": ri + 2,
                "expected_col_count": src_col_count,
                "actual_col_count": len(sheet_row),
                "remediation": (
                    "row col 수가 source와 정확히 일치 안 함 — "
                    f"{'cell 부족 (발행 누락)' if len(sheet_row) < src_col_count else 'extra column 잔존 (옵션 불일치 또는 stale)'}"
                ),
            })

    if bounds_issues:
        return {"pass": False, "diff_list": bounds_issues}

    # 5. cell 단위 syllable-level diff (NFC 정규화)
    diff_list = []
    for ri in range(src_row_count):
        sheet_row = sheet_values[ri + 1]
        src_row = src_rows[ri]
        for ci in range(src_col_count):
            sheet_val = unicodedata.normalize("NFC", str(sheet_row[ci]))
            src_val = unicodedata.normalize("NFC", str(src_row[ci]))
            if sheet_val != src_val:
                diff_list.append({
                    "row": ri + 2,  # header 1 + 0-index → 2부터
                    "col": col_letter(ci),
                    "fr_id": src_row[0] if src_row else "(unknown)",
                    "expected": src_val,
                    "actual": sheet_val,
                    "syllable_diff": diff_syllables(src_val, sheet_val),
                })

    return {
        "pass": len(diff_list) == 0,
        "diff_list": diff_list,
        "src_meta": {"row_count": src_row_count, "col_count": src_col_count},
        "sheet_meta": {"row_count": len(sheet_values)},
    }


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--source-json", required=True, help="로컬 source rows JSON 경로")
    parser.add_argument(
        "--sheet-data-json", required=True,
        help="MCP get_sheet_data dump JSON 경로 (Claude가 미리 fetch)",
    )
    parser.add_argument(
        "--sheets-option", choices=["A", "B", "C", "D"], required=True,
        help="옵션 분기 — col count 정합 검증",
    )
    parser.add_argument(
        "--report-json", default=None,
        help="diff report JSON 저장 경로 (선택). 미지정 시 stdout 출력만.",
    )
    args = parser.parse_args()

    src_path = Path(args.source_json)
    sheet_path = Path(args.sheet_data_json)
    for p, name in [(src_path, "source JSON"), (sheet_path, "sheet data JSON")]:
        if not p.exists():
            print(f"ERROR: {name} 부재 — {p}", file=sys.stderr)
            sys.exit(2)

    result = readback_diff_gate(src_path, sheet_path, args.sheets_option)

    if "error" in result:
        print(f"ERROR: {result['error']}", file=sys.stderr)
        sys.exit(2)

    if args.report_json:
        Path(args.report_json).write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    if result["pass"]:
        meta = result["src_meta"]
        print(f"PASS — diff 0건 ({meta['row_count']} rows × {meta['col_count']} cols, NFC 정규화 후)")
        sys.exit(0)
    else:
        print(f"FAIL — diff {len(result['diff_list'])}건 발견", file=sys.stderr)
        for d in result["diff_list"][:20]:
            if d.get("type"):
                print(f"  - {d['type']}: {d.get('remediation', '')}", file=sys.stderr)
            else:
                print(
                    f"  - {d['fr_id']} cell {d['col']}{d['row']}: "
                    f"expected={d['expected'][:60]!r}, actual={d['actual'][:60]!r}",
                    file=sys.stderr,
                )
        if len(result["diff_list"]) > 20:
            print(f"  ... + {len(result['diff_list']) - 20}건 추가", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
