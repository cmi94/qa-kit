#!/usr/bin/env python3
"""qa-scout v0.3.0 — input-manifest.yaml 마이그레이션 유틸 (v0.2.9 → v0.3.0).

SDD: ../../docs/qa-scout/spec.md §5-12 마이그레이션 4단계.

사용법:
    python plugins/qa-scout/scripts/migrate-to-v030.py <input-manifest.yaml> <mode>

mode:
    dry-run — 변경 preview 출력만, 파일 미수정 (기본 검토 시 권장)
    write   — backup 생성 + schema_version 갱신 + 누락 슬롯 4종 append (실제 파일 수정)

마이그레이션 룰:
    - 대상 manifest의 schema_version이 "0.3.0"이면 no-op (이미 마이그레이션됨)
    - schema_version "0.2.9" → "0.3.0" 갱신
    - 신규 슬롯 4종(sources / source_tier_review / fr_sources / unmapped_leaves_path) 중
      manifest top-level에 이미 존재하는 슬롯은 보존하고, 누락된 슬롯만 EOF에 append
    - 기존 downstream_enrichment / developer_deep_scope / deep_screen_targets /
      received_artifacts / final_artifacts / execution_gate / readme_discovery /
      two_doc_cross_check 등 v0.2.9 구조는 모두 보존 (텍스트 라인 그대로)
    - write 모드는 backup 파일 생성 후 원본 덮어쓰기
      backup 경로: <manifest>.v0.2.9-backup-<YYYYMMDDTHHMMSSZ>

신규 슬롯 기본값 (SDD §3·§4-1·§4-2-3·§4-5):
    sources                  = []  (단계 5에서 6 tier 분류 후 채움)
    source_tier_review       = []  (단계 5에서 tier별 검토 흔적 기록)
    fr_sources               = {}  (단계 9c에서 각 FR별 primary + secondary_sources 부착)
    unmapped_leaves_path     = "unmapped-leaves.yaml"

종료 코드:
    0 — 정상 (마이그레이션 완료, no-op 포함)
    1 — 마이그레이션 차단 (지원 외 schema_version 등)
    2 — 인자 오류 또는 파일 접근 실패

의존성: Python 표준 라이브러리만 사용 (pip install 불필요).
        YAML 파서 미사용 — 텍스트 라인 기반 패치로 기존 주석·들여쓰기·구조 보존.
"""
import re
import shutil
import sys

# Windows cp949 회피 — stdout/stderr UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
from datetime import datetime, timezone
from pathlib import Path

SUPPORTED_FROM = ["0.2.9"]
TARGET_VERSION = "0.3.0"
NEW_SLOTS = ["sources", "source_tier_review", "fr_sources", "unmapped_leaves_path"]

SLOT_BLOCKS = {
    "sources": (
        "\n# 단계 5 자료 큐레이션 6 tier 합집합 — 각 자료를 source_tier enum 6종으로 분류\n"
        "sources: []\n"
        "# 예: [{tier: F-catalog, path: docs/reference/function-spec.md, entries: [...], absorbed_into: F-catalog}, ...]\n"
    ),
    "source_tier_review": (
        "\n# 단계 5 tier별 검토 흔적 — 각 tier에 대해 검토했는지/누락 없는지 기록\n"
        "source_tier_review: []\n"
        "# 예: [{tier: F-catalog, reviewed: true, gaps: []}, ...]\n"
    ),
    "fr_sources": (
        "\n# 단계 9c FR별 인풋 출처 객체 (primary + secondary_sources)\n"
        "fr_sources: {}\n"
        '# 예: {FR-<PROJECT>-001: {primary: "F-catalog F-001", secondary_sources: ["FS_X §3.5.1"]}}\n'
    ),
    "unmapped_leaves_path": (
        "\n# 단계 9c.5 UI surface 감지 — mindmap leaf ↔ §1 매핑 안 되는 후보 등록 경로\n"
        "unmapped_leaves_path: unmapped-leaves.yaml\n"
    ),
}

HEADER_BLOCK = (
    "\n# -------------------------------------------------------\n"
    "# v0.3.0 신규 — Coverage Completeness Gate (SDD §3·§4-1·§4-2-3·§4-5)\n"
    "# 4 슬롯 필수 — migrate-to-v030.py로 빈 슬롯 추가됨. scout 단계 5/9c에서 채움.\n"
    "# -------------------------------------------------------\n"
)


def detect_version(text: str) -> str | None:
    m = re.search(r'^schema_version:\s*"?([0-9.]+)"?', text, re.MULTILINE)
    return m.group(1) if m else None


def detect_existing_slots(text: str) -> set[str]:
    existing = set()
    for slot in NEW_SLOTS:
        if re.search(rf"^{slot}:", text, re.MULTILINE):
            existing.add(slot)
    return existing


def replace_schema_version(text: str) -> str:
    return re.sub(
        r'^(schema_version:\s*"?)[0-9.]+("?)',
        rf'\g<1>{TARGET_VERSION}\g<2>',
        text,
        count=1,
        flags=re.MULTILINE,
    )


def append_missing_slots(text: str, missing: set[str]) -> str:
    if not missing:
        return text
    if not text.endswith("\n"):
        text += "\n"
    # 누락된 슬롯만 개별 append (idempotency — partial-slot 시 전체 블록 중복 방지)
    text += HEADER_BLOCK
    for slot in NEW_SLOTS:
        if slot in missing:
            text += SLOT_BLOCKS[slot]
    return text


def main():
    if len(sys.argv) != 3:
        print("Usage: migrate-to-v030.py <input-manifest.yaml> <dry-run|write>", file=sys.stderr)
        sys.exit(2)

    manifest_path = Path(sys.argv[1])
    mode = sys.argv[2]
    if mode not in ("dry-run", "write"):
        print(f"ERROR: mode는 dry-run | write — got: {mode}", file=sys.stderr)
        sys.exit(2)
    if not manifest_path.exists():
        print(f"ERROR: manifest 부재 — {manifest_path}", file=sys.stderr)
        sys.exit(2)

    text = manifest_path.read_text(encoding="utf-8")
    current = detect_version(text)

    if current is None:
        print("ERROR: schema_version line 미발견", file=sys.stderr)
        sys.exit(1)
    if current == TARGET_VERSION:
        print(f"no-op — 이미 {TARGET_VERSION} (마이그레이션 불필요)")
        sys.exit(0)
    if current not in SUPPORTED_FROM:
        print(
            f"ERROR: 지원 외 schema_version — got {current}, expected {SUPPORTED_FROM} → {TARGET_VERSION}",
            file=sys.stderr,
        )
        sys.exit(1)

    existing_slots = detect_existing_slots(text)
    missing_slots = set(NEW_SLOTS) - existing_slots

    new_text = replace_schema_version(text)
    new_text = append_missing_slots(new_text, missing_slots)

    if mode == "dry-run":
        print(f"[dry-run] schema_version: {current} → {TARGET_VERSION}")
        print(f"[dry-run] 기존 슬롯: {sorted(existing_slots) or '(없음)'}")
        print(f"[dry-run] 추가될 슬롯: {sorted(missing_slots) or '(없음)'}")
        print(f"[dry-run] 변경 line 수: {new_text.count(chr(10)) - text.count(chr(10))}")
        sys.exit(0)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_path = manifest_path.with_suffix(manifest_path.suffix + f".v{current}-backup-{ts}")
    shutil.copy2(manifest_path, backup_path)
    manifest_path.write_text(new_text, encoding="utf-8")

    print(f"backup 생성: {backup_path.name}")
    print(f"schema_version: {current} → {TARGET_VERSION}")
    print(f"추가된 슬롯: {sorted(missing_slots) or '(없음 — 모두 기존 보존)'}")
    sys.exit(0)


if __name__ == "__main__":
    main()
