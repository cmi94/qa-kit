#!/usr/bin/env python3
"""GxP 기능 정의서 표준 디자인 적용 payload 생성기.

본 스크립트는 google-sheets API batch_update payload(JSON)를 stdout 출력한다.
실제 API 호출은 Claude(google-sheets MCP) 또는 gspread 등 호출자가 수행한다.

두 stage 분리:
  - stage=add    : addSheet payload만 생성 (기존 시트에 없는 신규 시트 추가)
  - stage=design : design payload만 생성 (existing-sheets-json으로 sheetId 매핑 전달 필요)

이렇게 분리해야 신규 시트 생성 → sheetId 확보 → 디자인 적용 순서로 결정론적 처리 가능.

Usage:
    # Stage 1 — 누락 시트 addSheet payload
    python tools/feature-spec-design/apply.py --spreadsheet-id <ID> --stage add \
        --existing-sheets-json '{"01_표지":0}'

    # Stage 2 — design payload (sheetId 매핑 확보 후)
    python tools/feature-spec-design/apply.py --spreadsheet-id <ID> --stage design \
        --existing-sheets-json '{"01_표지":0,"02_변경이력":12,"03_기능정의서":34,...}'

    # Optional 06 시트 포함
    python tools/feature-spec-design/apply.py ... --include-optional
"""
import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
TOKENS_PATH = ROOT / "templates" / "feature-spec-design" / "design-tokens.json"
LAYOUT_PATH = ROOT / "templates" / "feature-spec-design" / "sheets-layout.json"


def resolve_color(tokens, ref):
    return tokens["colors"][ref]


def resolve_border(tokens, border_name):
    bs = tokens["border_styles"][border_name]
    return {
        "style": bs["style"],
        "width": bs["width"],
        "colorStyle": {"rgbColor": resolve_color(tokens, bs["color_ref"])},
    }


def make_header_format(tokens, border_pattern):
    borders = {}
    for side in ("top", "bottom", "left", "right"):
        name = border_pattern.get(side)
        if name:
            borders[side] = resolve_border(tokens, name)
    return {
        "backgroundColor": tokens["colors"]["header_bg"],
        "horizontalAlignment": tokens["alignment"]["header_horizontal"],
        "verticalAlignment": tokens["alignment"]["header_vertical"],
        "wrapStrategy": tokens["wrap_strategy"],
        "textFormat": {
            "foregroundColor": tokens["colors"]["header_fg"],
            "fontFamily": tokens["text"]["font_family"],
            "fontSize": tokens["text"]["header_font_size"],
            "bold": tokens["text"]["header_bold"],
        },
        "borders": borders,
    }


def border_pattern_for(col_idx, n_cols, patterns):
    if col_idx == 0:
        return patterns["first_column"]
    if col_idx == n_cols - 1:
        return patterns["last_column"]
    return patterns["middle_column"]


def requests_for_sheet(sheet_id, sheet_def, tokens):
    headers = sheet_def["headers"]
    n = len(headers)
    patterns = tokens["border_patterns"]
    reqs = []

    # 1. 헤더 셀: 텍스트 + 포맷 + 보더 (각 컬럼 위치별 border pattern)
    cells = []
    for col_idx, text in enumerate(headers):
        bp = border_pattern_for(col_idx, n, patterns)
        cells.append({
            "userEnteredValue": {"stringValue": text},
            "userEnteredFormat": make_header_format(tokens, bp),
        })
    reqs.append({
        "updateCells": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": 0,
                "endRowIndex": 1,
                "startColumnIndex": 0,
                "endColumnIndex": n,
            },
            "rows": [{"values": cells}],
            "fields": (
                "userEnteredValue,"
                "userEnteredFormat(backgroundColor,horizontalAlignment,verticalAlignment,"
                "wrapStrategy,textFormat,borders)"
            ),
        }
    })

    # 2. 헤더 행 높이
    reqs.append({
        "updateDimensionProperties": {
            "range": {
                "sheetId": sheet_id,
                "dimension": "ROWS",
                "startIndex": 0,
                "endIndex": 1,
            },
            "properties": {"pixelSize": tokens["dimensions"]["header_row_height_px"]},
            "fields": "pixelSize",
        }
    })

    # 3. 컬럼 너비 — 동일 텍스트 통일 룰
    widths = tokens["column_widths_by_name"]
    default_w = tokens["dimensions"]["default_column_width_px"]
    for col_idx, text in enumerate(headers):
        w = widths.get(text, default_w)
        reqs.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": col_idx,
                    "endIndex": col_idx + 1,
                },
                "properties": {"pixelSize": w},
                "fields": "pixelSize",
            }
        })

    # 4. frozenRowCount
    reqs.append({
        "updateSheetProperties": {
            "properties": {
                "sheetId": sheet_id,
                "gridProperties": {"frozenRowCount": tokens["structure"]["frozen_row_count"]},
            },
            "fields": "gridProperties.frozenRowCount",
        }
    })

    return reqs


def build_add_requests(layout, include_optional, existing):
    out = []
    for sd in layout["sheets"]:
        if sd.get("optional", False) and not include_optional:
            continue
        if sd["title"] in existing:
            continue
        out.append({
            "addSheet": {
                "properties": {
                    "title": sd["title"],
                    "index": sd["index"],
                }
            }
        })
    return out


def build_design_requests(layout, tokens, include_optional, existing, sheet_title=None):
    out = []
    missing = []
    for sd in layout["sheets"]:
        if not sd.get("design_managed", False):
            continue
        if sd.get("optional", False) and not include_optional:
            continue
        title = sd["title"]
        if sheet_title and title != sheet_title:
            continue
        sheet_id = existing.get(title)
        if sheet_id is None:
            missing.append(title)
            continue
        out.extend(requests_for_sheet(sheet_id, sd, tokens))
    return out, missing


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--spreadsheet-id", required=True, help="대상 Sheets ID (참고용 — 실제 API 호출은 호출자가)")
    parser.add_argument("--stage", choices=["add", "design"], required=True)
    parser.add_argument("--existing-sheets-json", default="{}", help='기존 시트 {title:sheetId} JSON')
    parser.add_argument("--include-optional", action="store_true", help="optional 시트(06_18c) 포함")
    parser.add_argument("--sheet-title", default=None, help="design stage: 단일 시트만 필터링 (payload 분할용)")
    parser.add_argument("--compact", action="store_true", help="indent 없는 컴팩트 JSON 출력")
    args = parser.parse_args()

    tokens = json.loads(TOKENS_PATH.read_text(encoding="utf-8"))
    layout = json.loads(LAYOUT_PATH.read_text(encoding="utf-8"))
    existing = json.loads(args.existing_sheets_json)

    if args.stage == "add":
        requests = build_add_requests(layout, args.include_optional, existing)
        out = {"spreadsheet_id": args.spreadsheet_id, "stage": "add", "requests": requests}
    else:
        requests, missing = build_design_requests(layout, tokens, args.include_optional, existing, args.sheet_title)
        if missing:
            print(
                f"WARNING: design_managed 시트 {missing}의 sheetId 미지정 — "
                "existing-sheets-json에 추가 후 재실행 필요",
                file=sys.stderr,
            )
        out = {"spreadsheet_id": args.spreadsheet_id, "stage": "design", "requests": requests}

    if args.compact:
        print(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
    else:
        print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
