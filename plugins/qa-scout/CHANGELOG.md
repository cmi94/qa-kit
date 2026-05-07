# qa-scout Changelog

## [0.2.0] — 2026-05-06

### 변경
- 골격 재설계 — 5종 도메인 지식 인계 + 기능 정의서 GxP 정형화 (Google Sheets 5시트, 17컬럼)
- `qa-handoff/{프로젝트명}/` 표준 폴더 구조
- 단계 -1 ~ 20 양방향 인계 흐름
- ID 체계 1차안 (FR/SCR/NFR/US/TC `<MOD>-NNN`)

### 추가
- 신규 스킬 `curate-input` — 자료 큐레이션 V1 8단계
- 신규 스킬 `markdown-to-sheets` — 단계 17a Sheets 이행
- 신규 sub-agent `scout-curator` (Haiku) — 단계 5 자료 큐레이션
- 신규 sub-agent `scout-analyzer` (Opus) — 단계 9 PRD 분석
- FAQ Q8 — sub-agent spawn 미검증 영역 주의

### 가드레일
- 추정 금지·`[자료 부족]` 마커·출처 표기 강제·최신본 확인 우선·받기 5종 본문 변환 금지·이모티콘 금지

## [0.1.0] — 2026-05-04

- 초기 출시 — 6종 markdown 양식 (deprecated)
