# -*- coding: utf-8 -*-
"""
qa-report — 이전 차수 결과 .xlsx의 자기기술 메타 블록(_meta 시트)을 읽어 JSON 출력.
회차 자동 감지·누적 이음에 사용. 메타가 없으면 {"round":0} 반환(=다음은 1차).
사용: python read_meta.py <prev_report.xlsx>
"""
import sys, json

try:
    import openpyxl
except ImportError:
    sys.stderr.write("openpyxl 필요: pip install openpyxl\n")
    sys.exit(2)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("usage: python read_meta.py <prev_report.xlsx>\n")
        sys.exit(1)
    path = sys.argv[1]
    try:
        wb = openpyxl.load_workbook(path, data_only=True)
    except Exception as e:
        print(json.dumps({"round": 0, "error": f"열기 실패: {e}"}, ensure_ascii=False))
        return
    if "_meta" not in wb.sheetnames:
        # 빈 템플릿이거나 메타 없는 파일 → 1차로 간주
        print(json.dumps({"round": 0, "warning": "_meta 시트 없음 — 1차로 처리"}, ensure_ascii=False))
        return
    raw = wb["_meta"]["A2"].value
    try:
        meta = json.loads(raw)
    except Exception:
        print(json.dumps({"round": 0, "error": "메타 파싱 실패"}, ensure_ascii=False))
        return
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == "__main__":
    main()
