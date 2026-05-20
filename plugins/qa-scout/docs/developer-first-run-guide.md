# Scouter (qa-scout) v0.2.8 — 개발자 최초 실행 가이드

> 본 가이드는 처음 Scouter를 받는 개발자가 자기 개발 폴더에서 1회차 실행을 완료하기 위한 단계별 안내다. 변수형(`<project>`, `<도메인>` 등)으로 작성됐으며 특정 프로젝트 도메인을 가정하지 않는다.

- **버전**: v0.2.8 (deep screen coverage 게이트 포함)
- **대상**: 개발자(자기 개발 환경에서 Scouter 1회차 호출)
- **선행 안내서**: [qa-kit README (public)](https://github.com/cmi94/qa-kit/blob/main/plugins/qa-scout/README.md)
- **spec**: [`../../docs/qa-scout/spec.md`](../../docs/qa-scout/spec.md) (v0.2.8 footer = deep screen coverage)

---

## 1. Scouter v0.2.8 목적

Scouter는 개발자가 보유한 다음 자료를 받아 QA용 **기능정의서 markdown**과 **handoff 패키지**로 정형화하는 Claude Code 플러그인이다.

- PRD (요구사항 정의서)
- 사용자 시나리오 (유스케이스 / Process Flow)
- 상태 전이 / 시퀀스 다이어그램
- 화면 전개도 또는 접근 가능한 테스트 화면
- 권한 매트릭스 (RBAC)
- 도메인 용어집 (Ubiquitous Language)
- ERD / 아키텍처
- 운영가이드 / 매뉴얼 / 상세 설계 문서

v0.2.8에서 추가된 **deep screen coverage 게이트**는 상세 화면·변수·Step/Parameter·상태별 동작 같은 깊은 뎁스 기능이 기능정의서에서 누락되는 것을 방지한다. 시작 시점에 개발자에게 5가지 deep-scope 질문을 묻고(단계 1b), 1차 가공 후 발견 후보를 다시 확인하는 게이트(단계 12b)를 둔다.

**Scouter의 책임 범위**: 개발자 자료를 받아 `qa-handoff/{project}/` 폴더에 markdown·yaml 산출물을 생성하는 것까지다. Google Sheets 생성, 라이브 환경 데이터 변경, baseline 자동 머지 등은 본 플러그인의 책임이 아니다(§7 QA 후공정 안내 참조).

---

## 2. 개발자가 준비할 입력

다음 8 카테고리를 가능한 만큼 모아 자료 폴더 하나로 정리한다. 모든 항목이 필수는 아니며, **없는 항목은 "없다"고 답변**하면 Scouter가 빠진 카테고리 가이드로 처리한다(추정 채움 금지).

| # | 카테고리 | 형태 예시 | 필수 |
|---|---|---|---|
| 1 | PRD (요구사항 정의서) | `*.md` / `*.pdf` / `*.docx` | **필수 확인** |
| 2 | 사용자 시나리오 / UC | 유스케이스 + Process Flow (1개 또는 2개) | **필수 확인** |
| 3 | 상태 전이 / SEQ | 시퀀스 다이어그램·상태 다이어그램 (Mermaid·PNG·`.drawio` 등) | **필수 확인** |
| 4 | 화면 전개도 또는 접근 가능한 테스트 화면 | 와이어프레임 / Figma export / 라이브 URL + 테스트 계정 | **필수 확인** |
| 5 | 권한 매트릭스 (RBAC) | role × permission 표 (markdown / excel) | **필수 확인** |
| 6 | 도메인 용어집 | Ubiquitous Language 사전 (markdown) | **필수 확인** |
| 7 | ERD / 아키텍처 | ERD 다이어그램·DB 스키마·시스템 아키텍처 | **상태 게이트** (`provided` / `generated-draft` / `explicitly-missing` 중 하나 명시) |
| 8 | 운영가이드 / 매뉴얼 / 상세 설계 문서 | 사용자 매뉴얼·정책 문서·기능 상세 설계 (markdown) | **권장** (상세 화면·변수·복잡 동작 evidence 보강) |

자료 폴더 예시:
```
<개발자 자기 폴더>/<project>-docs/
├── prd/
├── usecase/
├── seq/
├── screens/
├── permission/
├── glossary/
├── erd/
└── manuals/
```

폴더 구조가 다르더라도 Scouter의 큐레이터(scout-curator)가 자동 스캔하여 8 카테고리로 매핑한다.

---

## 3. 최초 실행 프롬프트 예시

자기 개발 폴더에서 Claude Code 세션을 시작한 뒤 다음 형태로 호출한다.

```
[PROJECT: <project>] scout 호출. <project> 도메인 산출물을 qa-handoff/<project>/로 정형화해줘.
자료 폴더: <자료 폴더 절대 또는 상대 경로>
운영 계정은 사용하지 말고 테스트 전용 계정만 사용한다.
위험 액션은 자동 클릭하지 않는다.
```

운영 예시(변수 치환만 다름):
```
[PROJECT: lims] scout 호출. lims 도메인 산출물을 qa-handoff/lims/로 정형화해줘.
자료 폴더: ./docs
운영 계정은 사용하지 말고 테스트 전용 계정만 사용한다.
위험 액션은 자동 클릭하지 않는다.
```

호출 후 Scouter가 단계 1(engagement context 5항목 — gmail·테스트 URL·테스트 계정·어드민 계정·인계 매체)을 묻고, 단계 1b deep-scope 5문(§4)으로 진입한다.

---

## 4. Scouter가 묻는 deep-scope 질문 5개 (단계 1b)

자료 폴더 경로 입력 직전에 Scouter가 다음 5개 질문을 **한 번에 묶어서** 묻는다. 답변은 자유 텍스트 가능(§5 참조).

1. 이 프로젝트에서 **기능정의서 누락이 절대 나면 안 되는 핵심 기능**은 무엇입니까?
2. 화면 depth가 깊거나 내부 구조가 복잡해 반드시 **상세 확인해야 하는 화면/기능**은 무엇입니까?
3. **변수, 계산식, Step/Parameter, 에디터, PDF 치환, 상태별 편집 제한, 승인·전자서명·감사추적**처럼 동작 규칙이 복잡한 부분이 있습니까?
4. crawl 시 **반드시 열어봐야 하는 상세 화면, 탭, 모달, 패널, 목록 row action**은 무엇입니까?
5. **저장, 삭제, 승인, 제출, 신규 버전 생성**처럼 클릭 금지 또는 관찰만 해야 하는 **위험 액션**은 무엇입니까?

본 5 질문은 시작 1회만 묻는다. 1차 가공 후(단계 12b)에서 추가 후보가 있는지 한 번 더 확인하는 재확인 게이트가 있고, 그 외에는 흩어진 추가 질의를 만들지 않는다.

답변은 자동으로 `qa-handoff/<project>/input-manifest.yaml > downstream_enrichment.developer_deep_scope.questions_round[]`에 기록된다.

---

## 5. 개발자 답변 방식

### 5-1. 자유 텍스트 OK

질문 5개에 대한 답변은 자연어 텍스트로 한 번에 답해도 되고, 항목별로 나눠 답해도 된다. Scouter 본체(Sonnet)가 답변을 5 키(`core_features` / `deep_screens` / `complex_behaviors` / `must_open_targets` / `risky_actions`)로 자동 분류한다.

예시 답변:
```
1. 핵심 기능: <기능 A>·<기능 B>·<기능 C>
2. 깊은 뎁스 화면: <화면 A>(/path 또는 화면명) — Step·Parameter·변수 marker가 있음
3. 복잡 동작: <기능>의 변수 lifecycle, <기능>의 상태별 편집 제한, <기능>의 전자서명·감사추적
4. 반드시 열어봐야 할 항목: <화면> 안의 <탭/모달/패널/row action>
5. 위험 액션: 저장·삭제·승인·신규 버전 생성·전자서명 — 모두 관찰만, 자동 클릭 금지
```

### 5-2. 모르면 "모름"으로 답변

특정 질문에 대해 자료가 없거나 정책이 확정되지 않은 경우 "모름" 또는 "현재 미정"으로 답변하면 된다. Scouter는 해당 항목을 `[자료 부족]` 또는 `[상세 화면 구조 부족]` 마커로 남기고 추정하지 않는다. 추후 자료 보강 시 다시 호출하면 해당 부분만 갱신할 수 있다.

### 5-3. secret / password는 본 문서에 직접 적지 말 것

답변 중 다음 정보는 **자료 폴더·답변 텍스트에 직접 기입하지 말 것**:

- 운영 계정 ID / PW
- API key / Token / Secret
- 고객 데이터 / PHI / 개인정보

대신:
- 테스트 전용 계정 ID는 답변에 적어도 좋다 (운영 계정은 절대 금지).
- 비밀번호는 zip 암호화 + 별도 채널(1password / Slack DM / 사전 합의된 secrets repo) 전달.
- Scouter는 secret 검출 시 답변 본문 placeholder로 대체하고 별도 채널 안내를 출력한다.

### 5-4. 위험 액션은 "관찰만" 또는 "테스트 환경에서 허용"으로 명시

5번 질문 답변 시 위험 액션 각각에 다음 중 하나를 명시한다:

- **`관찰만`** — 본 검증 사이클에서 자동 클릭 절대 금지. Scouter의 verifier(단계 9e)는 버튼 selector·xpath만 캡처하고 클릭하지 않는다.
- **`테스트 환경에서 허용 — <환경 URL> + <테스트 계정 ID>`** — 운영과 분리된 스테이징/테스트 환경에서만 허용. 운영 환경이 의심되면 verifier가 graceful skip 처리한다.

명시하지 않은 액션은 기본값으로 **`관찰만`**으로 처리된다.

---

## 6. 산출물 기대값

Scouter 실행이 완료되면 자기 개발 폴더의 `qa-handoff/<project>/`에 다음 산출물이 생성된다.

```
qa-handoff/<project>/
├── feature-spec/                     ← 기능정의서 markdown 5종 (Sheets 이행 대상)
│   ├── 01_표지.md
│   ├── 02_변경이력.md
│   ├── 03_기능정의서.md (17컬럼)
│   ├── 04_비기능요구.md (9컬럼)
│   └── 05_사용자스토리.md (9컬럼)
├── domain-knowledge/                 ← 받기 5종 (원본 형식 그대로)
│   ├── 01-user-scenario.<원본 확장자>
│   ├── 02-state-transition.<원본 확장자>
│   ├── 03-screen-layout.<원본 확장자>
│   ├── 04-permission-matrix.<원본 확장자>
│   └── 05-glossary.<원본 확장자>
├── _source/                          ← 모든 입력 자료의 read-only 사본
├── input-manifest.yaml               ← 자료 큐레이션 결과 + downstream_enrichment 옵션 블록
└── scout-log.md                      ← 질의·결정 이력 (append-only)
```

### 6-1. 옵션 산출물 (v0.2.8 deep screen coverage 시 추가 생성)

deep-scope 답변이 있고 deep_screen_targets[]가 등록되면 다음 파일이 추가로 만들어진다.

```
qa-handoff/<project>/
├── research-seed.md                  ← 연구팀(또는 QA)이 후공정 입력으로 읽는 시드 (8섹션)
└── (옵션) shared/pages/ui-crawl-manifest.yaml   ← UI crawl 산출물 (Playwright/Chrome MCP 등록 시)
```

본 두 파일은 옵션이며, 자료가 충분하거나 deep-scope 답변이 없으면 생성되지 않을 수 있다.

### 6-2. 본 단계에서 만들어지지 않는 것

- **Google Sheets 기능정의서 시트** — QA 후공정 책임(§7 참조). Scouter는 markdown까지만 생성하고 Sheets 신규 생성·갱신·공유는 수행하지 않는다.
- **TC (테스트 케이스)** — QA 측 `tc-writer`·`launch-tc-writer` 책임.
- **Playwright 스크립트** — QA 측 `script-generator`·`launch-script-generator` 책임.
- **baseline 머지 / 정식 발행 / 라이브 데이터 변경** — 모두 명시 승인 + 후공정 단계.

---

## 7. QA 후공정 안내 (Scouter 산출물 인계 이후)

개발자가 산출물을 QA에 인계하면 QA가 다음을 수행한다. **본 단계는 Scouter 본체의 책임 영역이 아니며**, QA 메인 + Codex 외부감사(선택) + 연구팀(선택)의 조합으로 진행된다.

### 7-1. 진행 순서

1. **수령** — QA가 `qa-handoff/<project>/` 패키지를 `knowledge/<project>/scout-handoff/`로 흡수.
2. **baseline 비교** — 기존 baseline(있는 경우)과 candidate 산출물을 대조해 누락·신규·conflict를 정리. baseline이 없는 신규 프로젝트는 이 단계 건너뜀.
3. **candidate 보정** — QA 메인이 1차 검토 후 명백한 typo·incompleteness만 수정하고 정책 단정·기능 확정은 보류. 보정 결과는 별도 candidate 파일로 보관(baseline 자동 머지 금지).
4. **Google Sheets 신규 생성** — QA 측 스킬 `qa-scout:markdown-to-sheets` 호출로 markdown 5종을 QA 본인 계정의 Google Sheets로 이행. **★ 이 단계는 Scouter 본체가 아니라 QA 후공정 책임이다** — Google Sheets MCP는 Scouter plugin의 필수 의존성이 아니다.
5. **reviewer 검증** — 새 Sheets를 기준으로 Codex Playwright reviewer 또는 명인 직접 검수를 진행. 10 enum 판정(PASS · FAIL · SCREEN-MISSING · SPEC-MISSING · PERMISSION-MISMATCH · BEHAVIOR-MISSING · VARIABLE-MISMATCH · STATE-MISMATCH · NOT-TESTED-RISKY-ACTION · CONTEXT-INSUFFICIENT) 중 하나로 모든 행을 분류.
6. **반영 결정** — 명인 보고 + 개발팀 후속 확인(자료 요청·확정 요청 분리 패키지) 후 baseline에 머지.

### 7-2. 책임 경계 요약

| 영역 | 책임 | 산출물 종착점 |
|---|---|---|
| **Scouter (qa-scout 플러그인, 본 가이드 범위)** | 개발자 자료 → markdown·yaml 정형화 + deep screen coverage 수집 | `qa-handoff/<project>/` |
| **QA 후공정 (메인 QA 파트너)** | baseline 비교 · candidate 보정 · **Google Sheets 신규 생성** · reviewer 발주 · 명인 보고 | `knowledge/<project>/feature-spec/` + Google Sheets |
| **연구팀 (`ai-research/`, Gemini CLI, 선택형)** | candidate research-pack 검증 + evidence-matrix 보강 | `ai-research/results/<date>-<project>-feature-spec-enrichment/` |
| **감사팀 (`ai-audit/`, Codex, 선택형)** | Sheets 기준 reviewer 발주 | `ai-audit/results/<date>-<project>-feature-spec-playwright-review/` |

### 7-3. 라이브 검증 진입 조건 (QA 후공정 단계)

위험 액션을 라이브에서 검증해야 하는 경우, QA 후공정에서 다음 4 조건을 모두 충족해야 진입한다.

1. 운영 환경과 분리된 스테이징/테스트 환경 정보 확보
2. 테스트 전용 ID + PW 계정 확보 (운영 계정 사용 금지)
3. 외부 메일/알림 차단 환경 확인
4. 명인 명시 승인 + 위험 액션 자동 클릭 차단 정책 강제 적용

위 4 조건 중 하나라도 미충족 시 reviewer 결과는 `CONTEXT-INSUFFICIENT`로 남는다. Scouter 본체에서는 라이브 환경에 절대 접속하지 않는다.

---

## 8. 자주 묻는 질문

### Q1. 본 가이드 따라했더니 Scouter가 위험 액션을 자동 클릭하지 않는데, 라이브에서 정말 동작하는지 어떻게 확인합니까?

라이브 동작 확인은 본 Scouter 단계가 아니라 §7 QA 후공정의 reviewer 단계에서 진행된다. Scouter는 read-only 관찰까지만 수행하며 `browser_click` · `browser_fill_form` 호출 자체를 하지 않는다. 라이브 검증이 필요한 항목은 reviewer 발주 시 §7-3 조건을 충족한 후 read-only 진입(모달 노출까지만) 또는 명시 승인 테스트 환경에서 실행된다.

### Q2. 답변 5개 중 일부를 모른다고 했는데 Scouter가 다시 물어봅니까?

단계 12b post-crawl 재확인 게이트에서 1회 다시 묻는다. 큐레이션·정형화 1차 결과를 본 후 추가 후보(예: "이 화면도 깊은 뎁스로 보이는데 맞습니까?") + 빠진 위험 액션을 묻는다. 이 1회로 종결되며 무한 질의 루프를 만들지 않는다.

### Q3. 자료가 부족한 카테고리가 많으면 어떻게 됩니까?

빠진 카테고리는 단계 7~8에서 가이드 출력 후 다음 4 옵션 중 선택한다: (a) 라이브 URL + 계정 제공해서 보강 / (b) 개발자 자기 AI로 생성 후 보강 / (c) PRD 등 다른 자료에서 발췌 / (d) 생략. 어느 경우든 추정으로 채우지 않으며 `input-manifest.yaml`에 결정 사유가 기록된다.

### Q4. Gemini CLI / Codex / Playwright MCP가 설치되어 있어야 합니까?

**아니오**. 본 Scouter plugin의 필수 의존성은 Claude Code 본체뿐이다. Gemini CLI는 연구팀(선택형 ai-research 발주) 때만, Codex는 감사팀(선택형 ai-audit 발주) 때만 사용된다. Playwright MCP는 단계 9e verifier가 라이브 URL이 제공됐을 때만 조건부 사용하며, 미등록 시 graceful skip(에러 X)으로 정상 종료된다.

### Q5. 본 가이드 산출물을 QA에 어떻게 인계합니까?

3 옵션 중 합의된 방식으로:
- **(a) zip + Slack/메일**: `Compress-Archive qa-handoff/<project>/ qa-handoff-<project>-<YYYYMMDD>.zip` 후 첨부
- **(b) git push**: `qa-handoff/`를 git 추적하고 commit + push (단, secret/계정이 본문에 들어가지 않도록 사전 점검)
- **(c) 클라우드 공유 링크**: Google Drive·OneDrive 등 공유 링크 (인증 필수)

QA 측은 수령 후 무결성 점검(input-manifest 일치 + hash 검증)을 수행한다.

---

## 9. 참조

- 본 plugin spec (v0.2 골격 + v0.2.6/v0.2.7/v0.2.8 footer 통합): `../../docs/qa-scout/spec.md`
- public install 가이드: [cmi94/qa-kit](https://github.com/cmi94/qa-kit)
- 변경 이력: [`CHANGELOG.md`](../CHANGELOG.md)

---

## 10. 한 줄 요약

> 본 가이드를 따라 `[PROJECT: <project>] scout 호출`로 시작하면, Scouter가 engagement context 5항목 + deep-scope 5문 + 자료 폴더 큐레이션을 거쳐 `qa-handoff/<project>/`에 정형화 산출물을 생성한다. **위험 액션은 자동 클릭하지 않고**, **Google Sheets 생성은 QA 후공정 책임**이며, **모르는 것은 추정 채움 없이 `[자료 부족]` 마커로 남는다**.
