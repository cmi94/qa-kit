# qa-scout Changelog

## [0.2.4] — 2026-05-07

### Docs
- README 재구성 — 사용자 가이드 SoT를 public README로 통합. 이전엔 사내 별도 안내서(qa-workbench private)에 흩어져 있던 내용:
  - **§1 사전 준비** (3분, 4항목 표) — Claude Code 설치·자료 폴더 정리·인계 채널 합의·단계 11b 사전 합의 정보
  - **§5 보안 — credentials 인계** — 권장 인계 매체 표 (zip 암호화·1password·암호화 메시지·git 지양)
  - **§7 트러블슈팅** — 7개 증상별 1차 대응 (`/plugin` 미지원·자동완성 누락·0 skills misleading·PROJECT 헤더·자료 폴더·운영 계정 거부 등)
- 섹션 번호 재배치 (1→사전준비 2→설치 3→사용법 4→가드 5→보안 6→FAQ 7→트러블슈팅 8→양식 9→라이선스 10→변경이력)

### Why
v0.2.3까지 사내(private) `INTERNAL_DISTRIBUTION.md`에만 있던 사용자 가이드를 외부 사용자도 접근 가능한 public README로 통합. 정보 1곳화 + 발견성 향상. 사내 한정 둘 가치 0이라는 사용자 지적.

## [0.2.3] — 2026-05-07

### Added
- **단계 11b** 신규 — 인계·검수 환경 정보 수집 단계. scout가 단계 12 완료 보고 직전에 3개 항목 인터뷰:
  1. 개발자 Google email (단계 17a `share_spreadsheet` + 단계 18c 검수 권한 대상)
  2. 테스트 대상 도메인 URL + 환경 종류(dev/staging/UAT) — 단계 18a~b 사람 검수·자동화 회귀
  3. 어드민/테스트 계정 정보 — 권한 매트릭스 사람 검수·자동화 회귀 (테스트 전용 — 운영 계정 금지)
- `input-manifest.yaml` 양식에 `contact:` + `test_environment:` 섹션 추가 (단계 11b 답변 저장 위치)
- `markdown-to-sheets` 스킬 입력 우선순위 명시 — `input-manifest.yaml > contact.developer.email`이 1순위, engagement-brief 2순위, 인터랙티브 입력 3순위
- 보안 가이드 — credentials 포함 manifest는 zip 암호화 또는 1password/암호화 메시지 인계 권장. git 인계 시 `.gitignore` 또는 `engagement-secrets.yaml` 분리

### Why
사용자 검수 결과 — v0.2.2까지 단계 17a `share_spreadsheet`에 필요한 `developer_email`을 단계 0~12 어디에서도 수집하지 않는 갭 발견. 명인이 단계 -1 사전 합의로 알고 있다는 운영 외 가정에 의존. 본 v0.2.3에서 scout 흐름 안에서 명시 수집으로 fix. 테스트 URL·어드민 계정도 같은 단계에서 함께 수집해 단계 18 사람 검수 가속화.

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
