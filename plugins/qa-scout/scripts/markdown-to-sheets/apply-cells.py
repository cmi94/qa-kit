#!/usr/bin/env python3
"""qa-scout v0.3.0 — markdown-to-sheets cell payload 생성 헬퍼 (D-1·D-2).

SDD §4-3 D-1·D-2 보조 개선 정합. 인라인 JSON `\\uXXXX` escape 한글
typo 회피를 위해 UTF-8 raw 한글 payload를 로컬 JSON 파일에서 읽어
google-sheets MCP `batch_update_cells` 호출용 ranges payload를 생성.

본 스크립트는 실제 MCP 호출은 하지 않음 (Claude/호출자가 stdout JSON을
받아 mcp__google-sheets__batch_update_cells에 전달). MCP 호출 직후
verify-readback.py(D-3 게이트)로 검증.

Usage:
    # source JSON: {"rows": [["<col1>", "<col2>", ...], ...]} — 62 FR × 14(또는 15) cells
    python apply-cells.py \\
        --spreadsheet-id <ID> \\
        --sheet "03_기능정의서" \\
        --source-json section1_rows.json \\
        --sheets-option C \\
        --start-row 2 \\
        --compact

Exit code:
    0 = payload 생성 PASS
    1 = source JSON 오류·col count mismatch
    2 = 인자 오류 또는 파일 부재

호출자(Claude/스크립트)는 stdout JSON을 다음과 같이 사용:
    payload = json.load(...)
    mcp.batch_update_cells(
        spreadsheet_id=payload["spreadsheet_id"],
        sheet=payload["sheet"],
        ranges=payload["ranges"],
    )
"""
import argparse
import json
import sys

# Windows cp949 회피 — stdout/stderr UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
from pathlib import Path


def col_letter(idx: int) -> str:
    """0-indexed col → spreadsheet letter (A, B, ..., Q, R, ...)."""
    result = ""
    n = idx
    while True:
        result = chr(ord("A") + n % 26) + result
        n = n // 26 - 1
        if n < 0:
            break
    return result


def expected_col_count(sheets_option: str) -> int:
    """sheets_option ↔ src col 수 정합 — D=15, A/B/C=14 (SPEC-2026-06-25: 사전 조건·입력·상태 전이·출력 4개 컬럼 제거)."""
    return 15 if sheets_option == "D" else 14


def build_ranges(rows: list, sheets_option: str, start_row: int) -> dict:
    """UTF-8 raw rows → MCP batch_update_cells ranges dict.

    Returns: {"<range>": [[<cell>, ...], ...]} or raises ValueError.
    """
    if not rows:
        raise ValueError("source rows 비어있음")

    src_col_count = len(rows[0])
    exp = expected_col_count(sheets_option)
    if src_col_count != exp:
        raise ValueError(
            f"sheets_option={sheets_option} expected col count {exp}, "
            f"src col count {src_col_count} mismatch"
        )

    # 모든 row가 동일 col count인지 검증
    for ri, row in enumerate(rows):
        if len(row) != src_col_count:
            raise ValueError(
                f"row {ri} col count {len(row)} != src col count {src_col_count}"
            )

    last_col = col_letter(src_col_count - 1)
    end_row = start_row + len(rows) - 1
    range_str = f"A{start_row}:{last_col}{end_row}"

    return {range_str: rows}


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--spreadsheet-id", required=True)
    parser.add_argument("--sheet", required=True, help="시트 이름 (예: '03_기능정의서')")
    parser.add_argument(
        "--source-json", required=True, help="UTF-8 raw 한글 cell rows JSON 파일 경로"
    )
    parser.add_argument(
        "--sheets-option", choices=["A", "B", "C", "D"], required=True,
        help="옵션 분기 — col count 정합 검증",
    )
    parser.add_argument(
        "--start-row", type=int, default=2,
        help="header row=1 가정. 데이터 첫 row=2 (default)",
    )
    parser.add_argument("--compact", action="store_true", help="indent 없는 컴팩트 JSON 출력")
    args = parser.parse_args()

    src_path = Path(args.source_json)
    if not src_path.exists():
        print(f"ERROR: source JSON 부재 — {src_path}", file=sys.stderr)
        sys.exit(2)

    try:
        src = json.loads(src_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: source JSON parse 실패 — {e}", file=sys.stderr)
        sys.exit(2)

    rows = src.get("rows", [])
    if not isinstance(rows, list):
        print("ERROR: source JSON에 'rows' 배열 부재", file=sys.stderr)
        sys.exit(1)

    try:
        ranges = build_ranges(rows, args.sheets_option, args.start_row)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    payload = {
        "spreadsheet_id": args.spreadsheet_id,
        "sheet": args.sheet,
        "ranges": ranges,
        "sheets_option": args.sheets_option,
        "src_row_count": len(rows),
        "src_col_count": len(rows[0]),
    }

    if args.compact:
        print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))

    sys.exit(0)


if __name__ == "__main__":
    main()
