# qa-scout Changelog

## [0.2.8] — 2026-05-20

### Added — deep screen coverage 게이트
- **scout 본체 단계 1b** 신설 — crawl/research 진입 전 개발자 deep-scope 5문 인터뷰(pre-crawl 1회).
  - 5문: 핵심 기능 / 깊은 뎁스 화면 / 복잡 동작(변수·Step/Parameter·에디터·PDF 치환·상태별 편집·승인·전자서명·감사추적) / 반드시 열어볼 탭·모달·패널·row action / 위험 액션(저장·삭제·승인·제출·신규 버전 생성·전자서명)
  - 답변은 `input-manifest.yaml > downstream_enrichment.developer_deep_scope.questions_round[]`에 기록. schema_version "0.2.7" 하위호환 유지(옵션 블록).
- **scout 본체 단계 12b** 신설 — 1차 가공 후 발견 후보를 개발자에게 재확인(post-crawl 1회). 결과는 `confirmation_rounds[]`에 append.
- **핵심 규약 7번** 신설 — 위험 액션 자동 클릭 금지. scout 본체·sub-agent·후공정 reviewer 모두 적용.
- **sub-agent 4종 보강** — `scout-curator`/`scout-supplementer`/`scout-analyzer`/`scout-verifier`가 `deep_screen_targets[]`·`developer_deep_scope` 입력을 받아 분류 우선순위·발굴 boost·정독 우선순위·라이브 우선 경로로 연결.
  - `scout-analyzer`에 단계 4-2 deep_screen_targets coverage check + Step/Parameter/Variable/State/Role/Risky 6 차원 별도 gap 후보 분류 추가.
  - `scout-verifier`에 위험 액션 자동 클릭 금지(=`browser_click`·`browser_fill_form` 호출 금지) + `risky_actions_observed[]` 적재 채널.
- **신규 템플릿 2종** — `templates/research-seed.md`(8섹션), `templates/ui-crawl-manifest.yaml`(9블록 — observed UI vs requirement source 분리).
- **`03_기능정의서.md` 보강** — 16번 인풋 출처 다중 evidence 인용 룰 + 17번 비고 deep marker 7종 + reviewer 1차 enum 매핑 표.
- **`docs/developer-first-run-guide.md` 신규** — 개발자가 처음 받았을 때 단계별로 따라할 변수형 가이드.

### Changed — Scouter 2.0 품질율 정정
- 릴리즈 노트의 Scouter 2.0 품질율을 **약 95%+ → 약 80%**로 정정. 마커 정확도 실측은 약 78%였고, 깊은 화면 뎁스는 surface crawl만으로 누락되는 사례가 남아 95%+ 표기는 목표값/추정값에 가까웠다는 점 명시.
- README §7 변경 이력 v0.2.7 sub-agent 누락 보강(supplementer·verifier가 publish 측에 추가됨).

### Why
v0.2.6/v0.2.7까지의 구조는 route/screen 단위 surface crawl에 의존해 "상세 화면이 있다"는 사실은 잡지만 "그 화면 안의 에디터·변수·Step/Parameter·상태별 동작이 기능정의서에 반영됐는지"는 놓칠 위험이 있었다. v0.2.8은 시작 시점 + post-crawl 2회 게이트로 개발자에게 직접 핵심·깊은 기능·위험 액션을 묻고 reviewer가 BEHAVIOR-MISSING / VARIABLE-MISMATCH / STATE-MISMATCH 같은 행위 단위 판정 enum으로 매핑하도록 한다.

### Compatibility
- `input-manifest.yaml` 의 `schema_version`은 `"0.2.7"` 그대로. `downstream_enrichment`는 옵션 블록이며 부재해도 v0.2.7 manifest는 그대로 유효.
- Gemini CLI / Codex / Playwright MCP / Google Sheets MCP는 본 플러그인의 필수 의존성이 아니다. 미설치 환경에서도 Scouter 본체는 정상 동작한다.

## [0.2.7] — 2026-05-13

### Added
- **GxP 표준 디자인 결정론적 적용 시스템** — `markdown-to-sheets` 스킬에 디자인 적용 단계 2개(Stage 1 addSheet · Stage 2 design) 신설. JSON token + Python 스크립트 자산으로 시트 간 동일 헤더 동일 너비·폰트·행 높이 강제.
  - `templates/feature-spec-design/design-tokens.json` — 색·폰트·행 높이·보더·표준 컬럼명별 너비 매핑 (동일 텍스트 통일 룰)
  - `templates/feature-spec-design/sheets-layout.json` — 6시트 구조·헤더 텍스트
  - `scripts/feature-spec-design/apply.py` — google-sheets API batch_update payload(JSON) 생성기. stage=add/design 분리·`--sheet-title` 시트별 분할·`--compact` 모드
  - `scripts/feature-spec-design/verify.py` — 적용 후 token 일치성 검증 (stdin JSON 비교, PASS/FAIL 리포트)

### Changed
- **시트 번호 체계 통일** — 5시트 → 6시트, 번호 연속화:
  - `04_변경이력` → `02_변경이력`
  - `06_기능정의서` → `03_기능정의서`
  - `07_비기능요구` → `04_비기능요구`
  - `08_사용자스토리` → `05_사용자스토리`
  - `06_18c_개발팀_질의` 신규 (optional, `--include-optional` 플래그)
- `templates/feature-spec/*.md` markdown 5개 파일명·frontmatter `sheet:` 필드·본문 내 시트 참조 동기화
- `skills/markdown-to-sheets/SKILL.md` 절차 5단계 → 6단계 (디자인 적용 2단계 신설). markdown 파싱 표 갱신.

### Why
qa-scout가 만들어내는 Google Sheets의 디자인이 매번 일관되지 않는 문제. AI 해석 변동성으로 색·너비·정렬이 미세하게 달라짐. JSON token으로 정형화 + Python 스크립트로 batch_update payload 생성 → 사람·AI·신규 프로젝트 모두 동일 결과 보장. 시트 번호도 정합 (이전 점프 패턴 `01·04·06·07·08` → 연속 `01·02·03·04·05·06`).

### 사용법
```bash
# 외부 사용자가 install 후 markdown-to-sheets 스킬 호출 시 자동 수행
# 또는 직접 호출:
python ${PLUGIN_ROOT}/scripts/feature-spec-design/apply.py \
    --spreadsheet-id <ID> \
    --stage add \
    --existing-sheets-json '<{title:sheetId} JSON>' \
    [--include-optional]
```

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
