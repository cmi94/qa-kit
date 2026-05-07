# qa-scout Changelog

## [0.2.6] — 2026-05-07

### Added
- **단계 12a 신규 (커버리지 자가 검증)** — `agents/scout.md` 절차 + 완료 보고 양식. operations-guide 카테고리 자료(USER_MANUAL·*_GUIDE.md 등)에서 heading 자동 추출 → F-NNN 분해와 매핑 시도 → 미매핑 heading은 사용자에 인터뷰 (포함/통합/제외). 결과를 `input-manifest.yaml > coverage_check` 섹션에 기록
- **자료 부족 마커 self-check** — `agents/scout-analyzer.md` 절차 단계 4-1 + `skills/docs-to-function-spec/SKILL.md` 단계 4-4. 마커 부여 전 키워드 자동 추출 + 모든 인풋 자료 grep 검증 강제 → hit 0건일 때만 마커 확정. hit ≥ 1건 시 마커 X + 본문에 §섹션 인용 추가. 결과를 `input-manifest.yaml > self_check_results` 섹션에 기록
- **8번째 카테고리 operations-guide** — `skills/curate-input/SKILL.md`. 운영 가이드·매뉴얼·정책 docs(`*GUIDE*`·`*MANUAL*`·`*POLICY*`·`*WORKFLOW*`·`*STANDARDS*` + docs 루트) 인식
- **다중 카테고리 매핑** — `categories: [<list>]` 배열 + `primary_category`. 한 파일이 N 카테고리에 기여 가능 (예: USER_MANUAL → user-scenario·screen-layout·permission-matrix·glossary·operations-guide)
- **archive 폴더 정책** — `skills/curate-input/SKILL.md`. archive·legacy 폴더 default 무시 X — 사용자 (a) 전체 무시 / (b) 일부 포함 / (c) 전체 포함 인터뷰 강제. 결정 자료 누락 차단
- **input-manifest.yaml 신규 슬롯** — `coverage_check`·`self_check_results`·`excluded_locations` 섹션
- **다중 카테고리 통합 매뉴얼 휴리스틱** — 파일 첫 30줄 Read해서 `## 목차` 또는 `## TOC` 감지 시 다중 카테고리 의심

### Why
plugin v0.2.5까지의 4개 구조적 갭 해소:
- **RC1**: curate-input 카테고리 모델이 7개 closed-set — 운영 가이드 docs 미매핑
- **RC2**: 단일 카테고리 매핑 가정 — 다중 카테고리 통합 매뉴얼 처리 불가
- **RC3**: 자료 부족 마커 부여 시 self-check 부재 — Opus 정독 1패스 누락 케이스 발생
- **RC4**: 기능 누락 자가 검증 단계 부재 — 산출물에서 38% 누락 신호 X

실측 산출물 검증에서 (40 FR 산출물 기준) 커버리지 ~62% / 자료 부족 마커 정확도 ~30% 발견. v0.2.6 적용 시 ~95%+ / ~90%+ 목표.

## [0.2.5] — 2026-05-07

### Docs
- README에 **흐름 한눈에 보기 (도식)** 섹션 신규 추가
  - 도식 1 — 개발자 관점 흐름 (Mermaid flowchart, 5문답 + 자동/수동 색구분)
  - 도식 2 — 전체 흐름 Swim Lane (개발자 + scout + 서브 에이전트 + QA, sequenceDiagram)
  - 도식 3 — 트리거 5종 + 엔드포인트 3종 (flowchart)
  - 1분 설명 스크립트 + 1줄 요약 elevator pitch (다른 개발자 인계용)
- 모든 본문에서 작성자 이름(`명인`) → 역할 표기(`QA`)로 변경. `최명인`은 author·문의 정보로만 잔존
- Korean 조사 일관성 정정 (QA가/QA는/QA를/QA와/QA로)

### Why
다른 개발자에게 트리거·엔드포인트를 짧게 설명할 도식·스크립트 부재. README는 spec-driven 상세 위주라 1분 인계용 자료 필요. 또한 작성자 실명이 본문에 노출되는 점이 외부 사용자 관점에서 어색 — 역할 표기로 일반화.

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
사용자 검수 결과 — v0.2.2까지 단계 17a `share_spreadsheet`에 필요한 `developer_email`을 단계 0~12 어디에서도 수집하지 않는 갭 발견. QA가 단계 -1 사전 합의로 알고 있다는 운영 외 가정에 의존. 본 v0.2.3에서 scout 흐름 안에서 명시 수집으로 fix. 테스트 URL·어드민 계정도 같은 단계에서 함께 수집해 단계 18 사람 검수 가속화.

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
