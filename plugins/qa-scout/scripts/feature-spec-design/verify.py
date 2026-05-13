#!/usr/bin/env python3
"""GxP 기능 정의서 표준 디자인 적용 후 token 일치성 검증.

본 스크립트는 google-sheets API get_sheet_data(include_grid_data=true) 응답들을
{title→data} dict 형식으로 stdin JSON으로 받아 design-tokens.json과 비교한다.

Usage:
    # 메인이 각 design_managed 시트에 대해 get_sheet_data fetch한 결과를 dict로 합쳐 stdin 전달
    echo '{"02_변경이력":<fetch>, "03_기능정의서":<fetch>, ...}' | python verify.py

Exit codes:
    0 — 전체 PASS
    1 — 하나 이상 FAIL
    2 — 사용법 오류
"""
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

EPS = 1e-5


def approx(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) < EPS
    return a == b


def color_eq(c1, c2):
    if c1 is None or c2 is None:
        return c1 is None and c2 is None
    return all(approx(c1.get(k, 0), c2.get(k, 0)) for k in ("red", "green", "blue"))


def extract_grid(fetched):
    """fetched: get_sheet_data 응답 (보통 result.sheets[0].data[0]). 다양한 형식 핸들링."""
    if isinstance(fetched, dict) and "rowData" in fetched:
        return fetched
    if isinstance(fetched, dict) and "result" in fetched:
        return fetched["result"]["sheets"][0]["data"][0]
    if isinstance(fetched, dict) and "sheets" in fetched:
        return fetched["sheets"][0]["data"][0]
    if isinstance(fetched, dict) and "data" in fetched:
        return fetched["data"][0]
    return fetched


def verify_sheet(grid, sheet_def, tokens):
    results = []
    title = sheet_def["title"]
    headers = sheet_def["headers"]

    # row 0 height
    rm = grid.get("rowMetadata", [])
    expected_h = tokens["dimensions"]["header_row_height_px"]
    actual_h = rm[0].get("pixelSize") if rm else None
    if approx(actual_h, expected_h):
        results.append(("PASS", f"{title}: 헤더 행 높이 {actual_h}px"))
    else:
        results.append(("FAIL", f"{title}: 헤더 행 높이 {actual_h} != {expected_h}"))

    # column widths
    cm = grid.get("columnMetadata", [])
    widths = tokens["column_widths_by_name"]
    default_w = tokens["dimensions"]["default_column_width_px"]
    for col_idx, txt in enumerate(headers):
        if col_idx >= len(cm):
            results.append(("FAIL", f"{title}: col {col_idx} '{txt}' columnMetadata 누락"))
            continue
        expected = widths.get(txt, default_w)
        actual = cm[col_idx].get("pixelSize")
        if approx(actual, expected):
            results.append(("PASS", f"{title}: col {col_idx} '{txt}' = {actual}px"))
        else:
            results.append(("FAIL", f"{title}: col {col_idx} '{txt}' = {actual}px != {expected}"))

    # header cells
    rows = grid.get("rowData", [])
    if not rows:
        results.append(("FAIL", f"{title}: rowData 없음"))
        return results

    values = rows[0].get("values", [])
    for col_idx, txt in enumerate(headers):
        if col_idx >= len(values):
            results.append(("FAIL", f"{title}: 헤더 셀 col {col_idx} '{txt}' 누락"))
            continue
        cell = values[col_idx]
        actual_text = cell.get("formattedValue") or ""
        if actual_text != txt:
            results.append(("FAIL", f"{title}: col {col_idx} 텍스트 '{actual_text}' != '{txt}'"))
            continue
        fmt = cell.get("userEnteredFormat", {})

        if not color_eq(fmt.get("backgroundColor"), tokens["colors"]["header_bg"]):
            results.append(("FAIL", f"{title}: col {col_idx} '{txt}' headerBg 불일치"))
            continue

        tf = fmt.get("textFormat", {})
        font_ok = (
            tf.get("fontFamily") == tokens["text"]["font_family"]
            and tf.get("fontSize") == tokens["text"]["header_font_size"]
            and tf.get("bold") == tokens["text"]["header_bold"]
        )
        if not font_ok:
            results.append((
                "FAIL",
                f"{title}: col {col_idx} '{txt}' textFormat 불일치 "
                f"(fontFamily={tf.get('fontFamily')}, size={tf.get('fontSize')}, bold={tf.get('bold')})"
            ))
            continue

        align_ok = (
            fmt.get("horizontalAlignment") == tokens["alignment"]["header_horizontal"]
            and fmt.get("verticalAlignment") == tokens["alignment"]["header_vertical"]
        )
        if not align_ok:
            results.append(("FAIL", f"{title}: col {col_idx} '{txt}' alignment 불일치"))
            continue

        if fmt.get("wrapStrategy") != tokens["wrap_strategy"]:
            results.append(("FAIL", f"{title}: col {col_idx} '{txt}' wrap 불일치"))
            continue

        results.append(("PASS", f"{title}: 헤더 col {col_idx} '{txt}' 포맷 OK"))

    # frozenRowCount — 메인 영역 미포함 (grid 응답엔 sheet props 따로). 호환성 위해 생략 또는 caller 책임
    return results


def main():
    if sys.stdin.isatty():
        print(__doc__, file=sys.stderr)
        sys.exit(2)

    tokens = json.loads(TOKENS_PATH.read_text(encoding="utf-8"))
    layout = json.loads(LAYOUT_PATH.read_text(encoding="utf-8"))
    fetched = json.load(sys.stdin)

    all_results = []
    for sd in layout["sheets"]:
        if not sd.get("design_managed", False):
            continue
        title = sd["title"]
        if title not in fetched:
            all_results.append(("SKIP", f"{title}: fetched 데이터 미제공 (생략)"))
            continue
        grid = extract_grid(fetched[title])
        all_results.extend(verify_sheet(grid, sd, tokens))

    pass_n = sum(1 for lv, _ in all_results if lv == "PASS")
    fail_n = sum(1 for lv, _ in all_results if lv == "FAIL")
    skip_n = sum(1 for lv, _ in all_results if lv == "SKIP")

    for lv, msg in all_results:
        print(f"[{lv}] {msg}")
    print(f"\nSummary: {pass_n} PASS / {fail_n} FAIL / {skip_n} SKIP")
    sys.exit(0 if fail_n == 0 else 1)


if __name__ == "__main__":
    main()
