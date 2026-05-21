# qa-scout (v0.2.9)

> 개발자가 보유한 5종 도메인 지식을 인계받고 PRD + 자료를 v0.2.9에서 **단일 markdown 2종**(`feature-spec.md` + `ui-menu-mindmap.md`)으로 압축 정형화하는 Claude Code 플러그인. 단계 1c execution gate · 단계 4a README discovery · 단계 9d.5 cross-check 게이트 포함.

**spec**: [../../docs/qa-scout/spec.md](../../docs/qa-scout/spec.md)

**최신 publish 버전**: v0.2.9 (2026-05-21) — 최종 산출 문서 2종 압축 + 단계 1c/4a/9d.5 게이트 신설. [CHANGELOG](CHANGELOG.md) 참조.

**최초 실행 가이드**: [`docs/developer-first-run-guide.md`](docs/developer-first-run-guide.md) — 개발자가 처음 받았을 때 단계별로 따라할 변수형 가이드.

---

## 무엇을 해결하나?

기존 (v0.1):
```
개발팀 산출물 zip → QA 인사팀 → 6종 markdown 정형화 (30~60분, QA 부담)
```

v0.2.9 구조:
```
개발자 (Claude Code + 본 플러그인)
   ↓ scout 호출
   ├── 단계 1c execution gate (환경·금지 액션·진행 승인 3문 1회)
   ├── 단계 4a README discovery (repo root/docs README 탐색 힌트)
   ├── 단계 5~8c 자료 큐레이션·빠진 카테고리 보강
   ├── 단계 9c → feature-spec.md (§0~§8 9섹션 단일 markdown — "무엇을 해야 하는가")
   ├── 단계 9b → ui-menu-mindmap.md (§0~§6 7섹션 단일 markdown — "어디에 있고 어떻게 연결되는가")
   └── 단계 9d.5 cross-check (feature-spec.md §8 ↔ ui-menu-mindmap.md §6 양방향 검증)
   ↓ qa-handoff/<project>/ 폴더에 저장 (markdown 2종 + 메타·재현 자산)
   ↓ zip / git / 클라우드로 QA에게 인계
   ↓
QA 측 (별도 후공정)
   ├── 단계 17a markdown-to-sheets (옵션 A/B/C 분기 — feature-spec.md → Sheets)
   └── tc-writer · script-generator · spec-analyzer 등 후공정
```

**v0.2.9 핵심 표현 변경**: v0.2.8 표현 layer → **"승인 범위 밖 상태 변경 액션 금지"**. execution_gate.decision(`full-execute` / `partial-execute` / `observe-only` / `context-insufficient`) 기반 실행 범위 결정. 운영 환경·운영 데이터 환경 상태 변경 액션은 항상 금지 (운영 보호 유지).

## v0.2 → v0.2.9 누적 변경 (v0.1 대비)

- **v0.2.0** — 6종 markdown → Google Sheets 5시트 + 받기 5종, 17컬럼 평면 양식, qa-handoff/{project}/ 표준 폴더, 단계 -1~20 양방향 인계, ID 체계, 신규 스킬 `curate-input`·`docs-to-function-spec`·`markdown-to-sheets`, 모델 라우팅 (Sonnet/Opus/Haiku 분담)
- **v0.2.6** — 단계 12a 커버리지 자가 검증, 자료부족 마커 self-check, operations-guide 카테고리, 다중 매핑, archive 정책
- **v0.2.7** — 개발자 환경 하네스 엔지니어링, engagement 단계 1 게이트, 분류 카테고리 8개, sub-agent 4종(curator·supplementer·analyzer·verifier), 2단계 hash 무결성, 마이그레이션 4단계, 옵션 C 단순화
- **v0.2.8** — deep screen coverage 게이트, 단계 1b deep-scope 5문 + 단계 12b post-crawl 재확인, `downstream_enrichment` optional 블록, research-seed·ui-crawl-manifest 신규
- **v0.2.9** (현재) — **최종 읽기 산출물 2종 압축** (`feature-spec.md` + `ui-menu-mindmap.md`), **단계 1c execution gate** (decision 4종 × reviewer_status 4종 1:1 매핑), **단계 4a README discovery gate**, **단계 9 5분기** (9a/9b/9c/9d/9d.5 cross-check), **단계 17a Sheets 옵션 A/B/C 분기**, **신규 스킬 `docs-to-ui-menu-mindmap`**, **`migrate-to-v029.mjs` 마이그레이션 유틸**, 핵심 규약 7번 표현 변경

## 효과

- **개발자 자체 정형화** — QA 인계 시 GxP 양식 통일, 검수자가 산출물 2개만 열어 확인 가능
- **모호점 즉시 발견** — scout이 작성 중 5개 패턴 자동 탐지·질의
- **환각 방지** — 자료 없는 영역에 `[자료 부족]` 마커, 추정 금지, 자동 보정 X (Auto-Healing Loop 차단)
- **출처 표기 강제** — 행 단위 GxP 추적 (16번 "인풋 출처" 컬럼)
- **최신본 검증** — 단일 후보여도 사용자 확인
- **운영 환경 보호** — execution_gate `observe-only`로 prod/운영 데이터 상태 변경 차단

---

## 1. 설치

### 옵션 A — Claude Code marketplace

```bash
/plugin marketplace add cmi94/qa-kit
/plugin install qa-scout@qa-kit
```

### 옵션 B — 수동 install

```bash
# 1. 에이전트 배치 (v0.2.9 — 5종 agent)
cp plugins/qa-scout/agents/scout.md ~/.claude/agents/             # 메인 (Sonnet)
cp plugins/qa-scout/agents/scout-curator.md ~/.claude/agents/     # 단계 5 (Haiku)
cp plugins/qa-scout/agents/scout-supplementer.md ~/.claude/agents/ # 단계 8b (Sonnet)
cp plugins/qa-scout/agents/scout-analyzer.md ~/.claude/agents/    # 단계 9c (Opus)
cp plugins/qa-scout/agents/scout-verifier.md ~/.claude/agents/    # 단계 9e (Sonnet, 조건부 Playwright MCP)

# 2. 스킬 배치 (v0.2.9 — 4종 skill)
cp -r plugins/qa-scout/skills/curate-input ~/.claude/skills/                # 단계 5
cp -r plugins/qa-scout/skills/docs-to-function-spec ~/.claude/skills/       # 단계 9c → feature-spec.md
cp -r plugins/qa-scout/skills/docs-to-ui-menu-mindmap ~/.claude/skills/     # 단계 9b → ui-menu-mindmap.md (v0.2.9 신규)
cp -r plugins/qa-scout/skills/markdown-to-sheets ~/.claude/skills/          # 단계 17a QA 측 Sheets 이행

# 3. 양식 템플릿 (선택 — scout이 자동 카피)
cp -r plugins/qa-scout/templates ~/.claude/templates/qa-scout/
```

### 필수 의존성

- **Claude Code 본체**만 필수
- **Google Sheets MCP**: QA 측 단계 17a `markdown-to-sheets` 호출 시만 필요 (개발자 본체 사용 X)
- **Playwright MCP**: 단계 9e verifier가 라이브 URL 제공 + execution_gate가 허용 시 조건부, 미등록 시 graceful skip
- **Gemini CLI**: 연구팀(선택형 ai-research 발주) 사용 시만 필요
- **Codex exec**: 감사팀(선택형 ai-audit 발주) 사용 시만 필요

Scouter 본체는 위 외부 도구를 필수 의존성으로 요구하지 않는다.

---

## 2. 사용법 — 단계 -1 ~ 20

### 단계 -1: QA → 개발자 사전 인계

QA가 개발자에게 1회 발송:
- 플러그인 install 가이드 (위 §1)
- 사전 안내서 1쪽 (별도 자료)
- 인계 약속 합의 (zip / git / 클라우드 — 단계 14에서 선택, 일정)

### 단계 -1a (마이그레이션 게이트, v0.2.7 산출물 보유 시)

기존 `qa-handoff/<project>/input-manifest.yaml`이 v0.2.7 또는 v0.2.8 schema면 본 단계에서 마이그레이션 4단계 진입.

```bash
# 1. dry-run preview (파일 미수정)
node plugins/qa-scout/scripts/migrate-to-v029.mjs qa-handoff/<project>/input-manifest.yaml dry-run

# 2. 사용자 확인 — 변경될 schema_version + 추가될 슬롯 검토 후 Y/N

# 3. write 적용 (backup 생성 후 원본 갱신)
node plugins/qa-scout/scripts/migrate-to-v029.mjs qa-handoff/<project>/input-manifest.yaml write
```

`write` 모드는 다음을 수행:
- backup 생성: `<manifest>.v<현재버전>-backup-<YYYYMMDDTHHMMSSZ>`
- schema_version 갱신 (`0.2.7` 또는 `0.2.8` → `0.2.9`)
- 누락된 v0.2.9 신규 슬롯 4종을 EOF에 append (이미 존재 시 보존):
  - `final_artifacts` (feature-spec.md + ui-menu-mindmap.md 경로·hash)
  - `execution_gate` (decision 4종, 마이그레이션 시 안전 기본값 `context-insufficient`)
  - `readme_discovery` (마이그레이션 시 `scanned: false`)
  - `two_doc_cross_check` (마이그레이션 시 `result: NOT_RUN`)
- 이미 v0.2.9 manifest면 no-op (멱등성)
- 기존 `downstream_enrichment` · `developer_deep_scope` · `deep_screen_targets[]` 구조는 모두 보존

**마이그레이션은 게이트 결과를 추정하지 않는다.** 안전 기본값만 채운 뒤 단계 1c/4a/9d.5 재실행으로 실제 결과를 채워야 한다 (Auto-Healing Loop 차단 패턴).

신규 프로젝트는 본 단계 skip.

### 단계 0~1: 개발자 환경 셋업

```bash
cd <자기 개발 폴더>     # 예: D:/work/<project>-dev/
claude                  # Claude Code 세션 시작
```

### 단계 2: 트리거 (PROJECT 헤더 포함)

```
> [PROJECT: <project>] scout 호출. <project> <중분류 코드> 도메인 산출물 정형화 필요
```

### 단계 1 → 1b → 1c → 4a → 5 진입 흐름

scout이 다음 순서로 사용자 입력을 받음:

1. **단계 1**: engagement context 5항목 (개발자 gmail·테스트 URL·테스트 계정·관리자 계정·인계 매체)
2. **단계 1b**: deep-scope 5문 (핵심 기능·깊은 뎁스 화면·복잡 동작·must_open_targets·forbidden_actions 후보)
3. **단계 1c (v0.2.9 신규 — execution gate)**: 환경·금지 액션·진행 승인 3문
4. **단계 4**: 자료 폴더 경로 입력
5. **단계 4a (v0.2.9 신규 — README discovery gate)**: README 후보 4 패턴 탐색 + 개발자 확인
6. **단계 5**: 자료 큐레이션 진입

### 단계 1c (v0.2.9 신규 — execution gate)

단계 1b 직후·단계 2 직전 1회 실시. **액션별 재확인 폐기 — 시작 1회 게이트로 환경·금지 액션·진행 승인을 한 번에 결정**.

scout이 묻는 3문:

```
1. 현재 URL/접근 조건은 local/dev/QA/staging 중 어느 환경입니까?
   운영 또는 운영 데이터가 섞인 환경입니까?
2. 이 환경에서 Scouter가 실행하면 안 되는 작업이 있습니까?
3. 금지 항목이 없다면 테스트 데이터 기준으로 상태 변경 액션까지 끝까지 실행 검증하겠습니다. 진행해도 됩니까?
```

decision 4종 × reviewer_status 4종 1:1 매핑:

| 입력 조건 | decision | reviewer_status | 실행 범위 |
|---|---|---|---|
| local/dev/qa/staging + 진행 승인 + 금지 항목 없음 | `full-execute` | `EXECUTED-TEST-ENV` | 상태 변경 액션까지 테스트 데이터로 실행 검증 |
| local/dev/qa/staging + 진행 승인 + 일부 금지 항목 있음 | `partial-execute` | `PARTIAL-OBSERVED` | 허용 액션만 실행, forbidden_actions[]는 관찰만 |
| prod 또는 운영 데이터 포함 | `observe-only` | `NOT-TESTED-PROD-RISK` | 상태 변경 액션 실행 금지, 관찰만 (운영 보호 — 항상 금지) |
| 환경 불명확 (답변 부재·"모름") | `context-insufficient` | `CONTEXT-INSUFFICIENT` | 실행 금지, scout-log.md에 사유 기록 |

결과는 3곳 동기 기록:
- `input-manifest.yaml > execution_gate:` (11필드 메타 SoT)
- `feature-spec.md` frontmatter `execution_policy:` (5필드)
- `ui-menu-mindmap.md` frontmatter `execution_policy:` (5필드, feature-spec.md와 1:1 일치 강제)

### 단계 4a (v0.2.9 신규 — README discovery gate)

단계 4 자료 폴더 경로 수신 직후·단계 5 자동 스캔 직전 1회 실시.

scout이 4 후보 패턴 탐색:
- `README.md` (repo root)
- `README.*` (repo root — README.txt·README.rst·README.adoc 등)
- `docs/README.md`
- `docs/**/README.md`

발견 README는 **요구사항 SoT가 아니라 탐색 힌트**. 발견 경로는 즉시 자료 폴더에 포함하지 않고 개발자 확인 후 승격.

`AGENTS.md` / `CLAUDE.md` / `.cursorrules`는 발견 시 `readme_discovery.agent_guidance_files[]` (top-level 배열)에 운영 지침으로 별도 기록. **제품 요구사항으로 취급하지 않음**.

### 단계 5~6: 자동 스캔 + 매핑 + 최신본 식별 (★ 핵심)

scout이 `Skill: curate-input` 호출 → 단일 보고서 출력 (8 카테고리 매핑 결과, 최신본 후보 질의, 빠진 카테고리 가이드).

개발자 텍스트 답변:
```
> PRD는 v2.md, 유스케이스 디렉토리 맞음, 와이어프레임 라이브 URL: <test-url> 계정: <test-account-id>/<test-password>
```

### 단계 7~8c: 빠진 카테고리 가이드 + 보충자

scout-supplementer가 미매칭 문서를 정독하고 PRD 연관 후보 markdown 반환.

### 단계 9 (v0.2.9 5분기 — ★ 최종 읽기 산출물 2종 생성)

scout이 다음 순서로 산출물 생성 — `qa-handoff/<project>/` 안:

- **9a**: 받기 5종 → `domain-knowledge/` 사본 (양식 변환 X) + `_source/` 원본 + `input-manifest.yaml` 생성
- **9b (v0.2.9 신규)**: `Skill: docs-to-ui-menu-mindmap` 호출 → `ui-menu-mindmap.md` §0~§6 7섹션 자동 도출
- **9c (기존 단계 9 통합)**: `Skill: docs-to-function-spec` 호출 → `feature-spec.md` §0~§8 9섹션 작성
- **9d**: `input-manifest.yaml > final_artifacts:` 슬롯에 두 산출물 경로 + SHA-256 hash 기록
- **9d.5 (v0.2.9 신규 — cross-check)**: feature-spec.md ↔ ui-menu-mindmap.md 양방향 검증
  - 방향 A: FR → 화면/상태/권한/위험 액션 매핑 (누락 시 §8에 marker)
  - 방향 B: leaf 노드 → FR 인용 (누락 시 §6에 marker)
  - 판정 4종: `PASS | PASS_WITH_NOTES | FAIL | NOT_RUN`
  - 결과 3곳 동기: feature-spec.md §8 + ui-menu-mindmap.md §6 + manifest `two_doc_cross_check:`
  - **자동 보정 X** — marker만 남기고 명인 검토 후 반영

### 산출물 폴더 구조 (v0.2.9)

```
qa-handoff/<project>/
├── feature-spec.md                      ← v0.2.9 최종 읽기 산출물 1/2 (§0~§8 9섹션 단일 markdown)
├── ui-menu-mindmap.md                   ← v0.2.9 최종 읽기 산출물 2/2 (§0~§6 7섹션 단일 markdown)
├── domain-knowledge/                    ← 받기 5종 (양식 변환 X, feature-spec.md/ui-menu-mindmap.md 본문에서 인용·요약 흡수)
│   ├── 01-user-scenario.<원본 확장자>   ← _source/ 보존 + feature-spec.md §1·§3 인용
│   ├── 02-state-transition.<원본 확장자> ← _source/ 보존 + feature-spec.md §5 요약 흡수
│   ├── 03-screen-layout.<원본 확장자>   ← _source/ 보존 + ui-menu-mindmap.md로 대체
│   ├── 04-permission-matrix.<원본 확장자> ← _source/ 보존 + feature-spec.md §4 요약 흡수
│   └── 05-glossary.<원본 확장자>        ← _source/ 보존 + feature-spec.md §6 요약 흡수
├── _source/                             ← 모든 입력 자료 원본 사본 (read-only)
├── input-manifest.yaml                  ← 메타·재현 자산 (schema_version "0.2.9" + 신규 슬롯 4종)
├── scout-log.md                         ← 질의·결정·게이트 이력 (append-only)
└── research-seed.md                     ← 연구팀 입력 자산 (후공정용, 옵션)
```

**기존 v0.2.8까지의 분산 산출물(`feature-spec/` 폴더 5 md + `domain-knowledge/` 5종)은 v0.2.9에서 최종 읽기 산출물이 아닌 내부 이행·호환·후공정 자산으로 위계가 분리됐다.**

### 단계 10~11: 모호점 추가 인터뷰

scout이 5개 패턴 발견 시 질의: 같은 용어 2가지 의미 / 행위자 불분명 / 입출력 필드 타입 불명 / 동일 기능 정의 충돌 / 단위 불명.

### 단계 12: 완료 보고

```
[scout v0.2.9 정제 완료]
PROJECT: <project>
입력: 자료 <N>건 (확정 <N>·생략 <N>·분류 불가 <N>)
출력 위치: qa-handoff/<project>/

v0.2.9 최종 산출 문서 (2종):
- feature-spec.md (§0~§8)
- ui-menu-mindmap.md (§0~§6)

상호 검증 게이트 (단계 9d.5): PASS | PASS_WITH_NOTES | FAIL | NOT_RUN
execution gate (단계 1c): decision <decision> / reviewer_status <status>
README discovery gate (단계 4a): scanned <true|false> / readme_files <N>건

질의 이력: <카테고리·이슈 목록>
다음: QA에게 인계 (단계 14)
```

### 단계 13~16: 개발자 → QA 인계

```bash
# 옵션 A: zip
Compress-Archive qa-handoff/<project> qa-handoff-<project>-<YYYYMMDD>.zip

# 옵션 B: git
git add qa-handoff/
git commit -m "qa-scout handoff: <project> <중분류 코드>"
git push

# 옵션 C: 클라우드 (Google Drive 등) + 공유 링크
```

### 단계 17~20: QA 측 후속

- **17a** (`Skill: markdown-to-sheets`): 단일 `feature-spec.md` → Google Sheets 자동 이행. 옵션 분기:
  - **옵션 A (기본, 권장)**: 5시트 — 01_표지·02_변경이력·03_기능정의서·04_비기능요구·05_사용자스토리
  - **옵션 B**: 8시트 — 옵션 A + 06_권한매트릭스·07_상태전이·08_용어집
  - **옵션 C**: 1시트 — 03_기능정의서만
- **`ui-menu-mindmap.md`는 Sheets 이행 X** — markdown 보조 산출물로 유지
- **17b**: `knowledge/<project>/scout-handoff/`로 흡수
- **18a~18c**: 양방향 검수 + 개발팀 검수 요청
- **19~20**: 회귀 + Sheets v1.0 정식 발행

---

## 3. 환각·운영 위반 방지 — scout v0.2.9 7가지 가드

| # | 룰 | 의미 |
|---|---|---|
| 1 | 추정 금지 | 자료에 명시 안 된 내용 만들어내지 않음. README도 요구사항 SoT 아닌 탐색 힌트 |
| 2 | 최신본 확인 우선 | 단일 후보여도 사용자 확인 |
| 3 | `[자료 부족]` 마커 | 빈 셀에 자동 부착, 추정 채움 X. grep self-check로 마커 정확도 검증 |
| 4 | 출처 표기 강제 | 16번 "인풋 출처" 컬럼 (행 단위 GxP 추적) |
| 5 | 받기 5종 본문 변환 금지 | 양식 변환 X. `_source/` 보존 + 본문에서 인용·요약 흡수만 |
| 6 | 이모티콘 금지 | 공식 문서, 양식·로그·보고에 사용 X |
| 7 | **승인 범위 밖 상태 변경 액션 금지 (v0.2.9 표현)** | 단계 1c execution_gate.decision 기반 실행 범위 결정. 운영 환경·운영 데이터 환경 상태 변경 액션은 항상 금지 |

---

## 4. 자주 묻는 질문

### Q1. v0.2.7/v0.2.8 산출물은 어떻게 v0.2.9로 마이그레이션합니까?
`plugins/qa-scout/scripts/migrate-to-v029.mjs` 사용 (§2 단계 -1a). dry-run → 사용자 확인 → write 순서. write 모드는 backup 생성 후 schema_version 갱신 + 누락된 신규 슬롯 4종 append. 이미 v0.2.9면 no-op (멱등성). 마이그레이션은 게이트 결과를 추정하지 않고 안전 기본값만 채움.

### Q2. 자료가 부족하면?
scout이 빈 셀에 `[자료 부족]` 마커 부착하고 보고. 자료 보충 후 재호출하면 해당 셀만 갱신.

### Q3. 받기 5종 양식 변환 가능한가요?
안 됩니다. "그대로 인계" 원칙. 본문 변환 없이 `_source/`에 보존 + feature-spec.md/ui-menu-mindmap.md 본문에서 인용·요약만 흡수.

### Q4. 단계 1c execution gate를 다시 묻나요?
시작 1회만 묻습니다. 단계 9e verifier·후공정 reviewer는 본 게이트 결정만 참조하고 액션별 재확인 안 합니다.

### Q5. README가 발견됐는데 그 내용을 그대로 기능정의서에 옮겨도 되나요?
안 됩니다. README는 요구사항 SoT가 아닌 **탐색 힌트**. README에서 추출한 값은 §1 16번 인풋 출처에 `README §x.x` 인용 + 17번 비고에 `[README 출처 — 본문 확인 필요]` 마커 부착.

### Q6. `ui-menu-mindmap.md`는 왜 Sheets로 안 옮기나요?
Mermaid mindmap은 트리 구조라 Sheets 친화도가 낮습니다. markdown 보조 산출물로 유지하고 GitHub markdown viewer / Notion import / VS Code preview로 봅니다.

### Q7. 두 산출물이 서로 어긋나면 어떻게 됩니까?
단계 9d.5 cross-check 게이트가 양방향 검증을 1회 실행. 누락은 marker(`[화면 위치 확인 필요]` / `SPEC-MISSING` 등)로 양쪽에 남깁니다. 자동 보정 X — 명인 검토 후 결정.

### Q8. ID 체계는 어떻게 정해지나요?
ID 패턴: `FR-<PROJECT>-NNN`·`SCR-<PROJECT>-NNN`·`NFR-<PROJECT>-NNN`·`US-<PROJECT>-NNN`·`TC-<PROJECT>-NNN` (모듈 코드는 PROJECT 헤더로 동적 치환, 결번 허용 3자리).

### Q9. Google Sheets / Playwright / Codex / Gemini 없이도 사용 가능합니까?
네. Claude Code 본체만 필수입니다. 나머지는 후공정·조건부·선택형 도구.

---

## 5. 양식 참조 (v0.2.9)

- 최종 산출물 #1: `templates/feature-spec.md` (단일 markdown §0~§8)
- 최종 산출물 #2: `templates/ui-menu-mindmap.md` (단일 markdown §0~§6)
- 메타·재현 자산: `templates/input-manifest.yaml` (schema_version 0.2.9)
- 연구팀 입력: `templates/research-seed.md`
- crawl 증거: `templates/ui-crawl-manifest.yaml`
- 마이그레이션: `scripts/migrate-to-v029.mjs` (dry-run | write)

---

## 6. 라이선스 / 문의

- MIT License
- 문의: 최명인 (chlauddls12@gmail.com)
- source: https://github.com/cmi94/qa-kit

## 7. 변경 이력

| 버전 | 일자 | 변경 |
|---|---|---|
| 0.1.0 | 2026-05-04 | 초기 출시 (개발팀 파일럿용 — 6종 markdown 양식) |
| 0.2.0 | 2026-05-06 | 골격 재설계 — 5종 도메인 지식 인계 + 기능 정의서 GxP 정형화 (Google Sheets 5시트, 17컬럼) + qa-handoff/ 표준 폴더 + 단계 -1~20 양방향 인계 + ID 체계 + 정정 6차(markdown→QA 이행+양방향 검수+markdown-to-sheets 신규) + 정정 7차(모델 라우팅: scout-curator Haiku + scout-analyzer Opus + scout Sonnet 오케스트레이터). |
| 0.2.6 | 2026-05-07 | 단계 12a 커버리지 자가 검증·자료부족 마커 self-check·operations-guide 카테고리·다중 매핑·archive 정책. |
| 0.2.7 | 2026-05-08 | **개발자 환경 하네스 엔지니어링** — engagement 단계 1 게이트, 분류 카테고리 8개, sub-agent 신설 2종(scout-supplementer·scout-verifier 조건부 Playwright MCP), 2단계 hash 무결성, 마이그레이션 4단계, 옵션 C 단순화, 양식 변수형 일괄 교체. |
| 0.2.8 | 2026-05-20 | **deep screen coverage 게이트** — 단계 1b deep-scope 5문 인터뷰(pre-crawl 1회) + 단계 12b post-crawl 재확인. 핵심 규약 7번 v0.2.8 표현 layer (자동 클릭 회피). `downstream_enrichment` optional 블록, 신규 템플릿 2종(research-seed·ui-crawl-manifest). |
| 0.2.9 | 2026-05-21 | **최종 산출 문서 2종 압축 + 단계 1c/4a/9d.5 게이트 신설** — feature-spec/ 5 md → `feature-spec.md` 단일 markdown(§0~§8) + `ui-menu-mindmap.md` 신규 markdown(§0~§6, Mermaid mindmap + 노드 상세 표 SoT). 받기 5종 중 02/04/05 본문 흡수, 03-screen-layout 마인드맵 대체, 01 인용만. 단계 1c execution gate(3문 + decision 4종 × reviewer_status 4종 1:1 매핑, 액션별 재확인 폐기). 단계 4a README discovery gate(4 후보 패턴 + 개발자 확인). 단계 9 5단계 분기(9a/9b/9c/9d/9d.5 cross-check). 핵심 규약 7번 표현 변경 v0.2.8 표현 layer → "승인 범위 밖 상태 변경 액션 금지" (운영 보호 유지). 단계 17a Sheets 옵션 A/B/C 분기(마인드맵 Sheets 미이행). 신규 스킬 `docs-to-ui-menu-mindmap`, 신규 마이그레이션 유틸 `migrate-to-v029.mjs`. input-manifest schema_version 0.2.9 + 신규 슬롯 4종(final_artifacts·execution_gate·readme_discovery·two_doc_cross_check). |
