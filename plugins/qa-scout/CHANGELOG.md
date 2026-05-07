# qa-scout Changelog

## [0.2.2] — 2026-05-07

### Fix
- `plugin.json`의 `compatibility`, `license` 필드 제거 — 비표준 필드가 skills 디스커버리를 막는 이슈 수정. 정상 동작 플러그인 plugin.json 패턴 준수 (name/version/description/author/homepage/keywords만).
- 라이선스는 LICENSE 파일(qa-kit 루트)로만 명시.

## [0.2.1] — 2026-05-07

### Fix (incomplete)
- `plugin.json`의 `components` 블록 제거 시도. 0.2.0에서 plugin manifest의 components 명시가 skills 자동 디스커버리를 막는 가설로 시도했으나 효과 없음. 0.2.2에서 추가 fix.

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
