# Scouter (qa-scout) v0.2.9 — 개발자 최초 실행 가이드

> 본 가이드는 처음 Scouter를 받는 개발자가 자기 개발 폴더에서 1회차 실행을 완료하기 위한 단계별 안내다. 변수형(`<project>`, `<도메인>` 등)으로 작성됐으며 특정 프로젝트 도메인을 가정하지 않는다.

- **버전**: v0.2.9 (최종 읽기 산출물 2종 압축 + 단계 1c execution gate + 단계 4a README discovery + 단계 9d.5 cross-check)
- **대상**: 개발자(자기 개발 환경에서 Scouter 1회차 호출)
- **선행 안내서**: [qa-kit README (public)](https://github.com/cmi94/qa-kit/blob/main/plugins/qa-scout/README.md)
- **SDD (v0.2.9 최신)**: `../../docs/qa-scout/spec.md`
- **이전 SDD (역사적 참조)**: `../../docs/qa-scout/spec.md` (v0.2.8) · `../../docs/qa-scout/spec.md` (v0.2.7)

---

## 1. Scouter v0.2.9 목적

Scouter는 개발자가 보유한 다음 자료를 받아 QA용 **단일 markdown 2종**(`feature-spec.md` + `ui-menu-mindmap.md`)으로 압축 정형화하는 Claude Code 플러그인이다.

- PRD (요구사항 정의서)
- 사용자 시나리오 (유스케이스 / Process Flow)
- 상태 전이 / 시퀀스 다이어그램
- 화면 전개도 또는 접근 가능한 테스트 화면
- 권한 매트릭스 (RBAC)
- 도메인 용어집 (Ubiquitous Language)
- ERD / 아키텍처
- 운영가이드 / 매뉴얼 / 상세 설계 문서

### v0.2.9 핵심 변화 — 최종 읽기 산출물 2종 압축

v0.2.8까지 검수자가 읽는 산출물은 `feature-spec/` 폴더의 markdown 5개(표지·변경이력·기능정의서·비기능·사용자스토리) + `domain-knowledge/` 5종(사용자시나리오·상태전이·화면전개도·권한·용어집)로 분산되어 한 행의 근거를 보려면 5~6개 파일을 동시에 열어야 했다.

v0.2.9는 다음 2개 markdown으로 압축한다.

1. **`feature-spec.md`** — "무엇을 해야 하는가" §0~§8 9섹션 단일 markdown. 기존 5 md(01~05) + 받기 5종 중 02/04/05(상태·권한·용어집)를 본문 흡수 + §8에 cross-check 결과.
2. **`ui-menu-mindmap.md`** — "어디에 있고 어떻게 연결되는가" §0~§6 7섹션 단일 markdown. 메인 화면 → 대메뉴 → 중메뉴 → 화면 → 탭/패널/모달 → 버튼/폼/테이블/row action 트리. Mermaid mindmap 시각 + 노드 상세 표(SoT) + deep_screen_targets[] 매핑 + cross-check 결과.

**기존 5시트·분산 문서는 v0.2.9에서 최종 읽기 산출물이 아닌 내부 이행·호환·후공정 자산으로 위계가 정리됐다.** feature-spec/ 5 md는 단일 `feature-spec.md` 9섹션으로 흡수 통합되고, domain-knowledge/ 5종은 `_source/`에 보존 + 본문 인용·요약 흡수.

### v0.2.9 신규 게이트 3종

- **단계 1c execution gate** — 환경·금지 액션·진행 승인 3문 1회. decision 4종 × reviewer_status 4종 1:1 매핑. 액션별 재확인 폐기.
- **단계 4a README discovery gate** — repo root + 자료 폴더의 README 4 후보 패턴 탐색. README는 요구사항 SoT가 아닌 탐색 힌트.
- **단계 9d.5 cross-check 게이트** — feature-spec.md ↔ ui-menu-mindmap.md 양방향 정합 검증. 판정 4종(`PASS | PASS_WITH_NOTES | FAIL | NOT_RUN`). 자동 보정 X.

### v0.2.9 표현 변경

v0.2.8 표현 layer → **"승인 범위 밖 상태 변경 액션 금지"**. execution_gate.decision 기반 실행 범위 결정 — 개발/QA/테스트 환경 + 금지 항목 없음 + 진행 승인 시 상태 변경 액션까지 실행 검증 가능. 운영 환경(prod)·운영 데이터 환경 상태 변경 액션은 항상 금지 (운영 보호 유지).

### Scouter의 책임 범위

개발자 자료를 받아 `qa-handoff/<project>/` 폴더에 markdown 2종 + 메타 자산을 생성하는 것까지다. **Google Sheets 생성·라이브 환경 데이터 변경·baseline 자동 머지 등은 본 플러그인의 책임이 아니다** (§7 QA 후공정 안내 참조).

### 필수 의존성 추가 없음

본 Scouter plugin의 필수 의존성은 **Claude Code 본체뿐**이다. Google Sheets MCP·Playwright MCP·Codex exec·Gemini CLI는 모두 후공정 또는 조건부 도구로, Scouter 본체는 이들을 필수 의존성으로 요구하지 않는다 (§8 Q3 참조).

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

폴더 구조가 다르더라도 Scouter의 큐레이터(scout-curator)가 자동 스캔하여 8 카테고리로 매핑한다. **단계 4a README discovery gate**가 repo root/docs 하위 README도 함께 탐색하여 누락된 자료 경로 힌트를 제안한다 (개발자 확인 후 자료 폴더에 승격).

---

## 3. v0.2.7/v0.2.8 산출물 보유 시 — 마이그레이션 안내 (단계 -1a)

기존 `qa-handoff/<project>/input-manifest.yaml`이 v0.2.7 또는 v0.2.8 schema면 본 단계에서 v0.2.9로 마이그레이션한다.

```bash
# 1. dry-run preview — 변경될 schema_version + 추가될 슬롯 검토 (파일 미수정)
node plugins/qa-scout/scripts/migrate-to-v029.mjs qa-handoff/<project>/input-manifest.yaml dry-run

# 2. 사용자 확인 — 출력 JSON의 schema_version_change + slots_to_append 검토 후 Y/N

# 3. write 적용 — backup 생성 후 원본 갱신
node plugins/qa-scout/scripts/migrate-to-v029.mjs qa-handoff/<project>/input-manifest.yaml write
```

`write` 모드 동작:
- backup 생성: `<manifest>.v<현재버전>-backup-<YYYYMMDDTHHMMSSZ>`
- schema_version 갱신 (`0.2.7` 또는 `0.2.8` → `0.2.9`)
- 누락된 v0.2.9 신규 슬롯 4종을 EOF에 append (이미 존재 시 보존):
  - `final_artifacts` (feature-spec.md + ui-menu-mindmap.md 경로·hash)
  - `execution_gate` (decision 4종, 마이그레이션 시 안전 기본값 `context-insufficient`)
  - `readme_discovery` (마이그레이션 시 `scanned: false`)
  - `two_doc_cross_check` (마이그레이션 시 `result: NOT_RUN`)
- 이미 v0.2.9 manifest면 no-op (멱등성)
- 기존 `downstream_enrichment` · `developer_deep_scope` · `deep_screen_targets[]` · `received_artifacts` 구조는 모두 보존

**마이그레이션은 게이트 결과를 추정하지 않는다.** 안전 기본값만 채운 뒤 단계 1c/4a/9d.5 재실행으로 실제 결과를 채워야 한다 (Auto-Healing Loop 차단 패턴 — memory `feedback_bridge_wrapping_pattern`).

신규 프로젝트는 본 단계 skip.

---

## 4. 최초 실행 프롬프트 예시

자기 개발 폴더에서 Claude Code 세션을 시작한 뒤 다음 형태로 호출한다.

```
[PROJECT: <project>] scout 호출. <project> 도메인 산출물을 qa-handoff/<project>/로 정형화해줘.
자료 폴더: <자료 폴더 절대 또는 상대 경로>
```

운영 예시(변수 치환만 다름):
```
[PROJECT: <sample-project>] scout 호출. <sample-project> 도메인 산출물을 qa-handoff/<sample-project>/로 정형화해줘.
자료 폴더: ./docs
```

호출 후 Scouter가 다음 순서로 사용자 입력을 받는다.

1. **단계 1**: engagement context 5항목 (개발자 gmail·테스트 URL·테스트 계정·어드민 계정·인계 매체)
2. **단계 1b**: deep-scope 5문 (§5)
3. **단계 1c (v0.2.9 신규)**: execution gate 3문 (§6)
4. **단계 2~4**: 자료 폴더 경로 입력
5. **단계 4a (v0.2.9 신규)**: README discovery gate (§7)
6. **단계 5~12**: 자료 큐레이션 → 정형화 → 완료 보고

---

## 5. Scouter가 묻는 deep-scope 질문 5개 (단계 1b)

engagement context 5항목 답변 직후·단계 1c execution gate 직전에 Scouter가 다음 5개 질문을 **한 번에 묶어서** 묻는다. 답변은 자유 텍스트 가능.

1. 이 프로젝트에서 **기능정의서 누락이 절대 나면 안 되는 핵심 기능**은 무엇입니까?
2. 화면 depth가 깊거나 내부 구조가 복잡해 반드시 **상세 확인해야 하는 화면/기능**은 무엇입니까?
3. **변수, 계산식, Step/Parameter, 에디터, PDF 치환, 상태별 편집 제한, 승인·전자서명·감사추적**처럼 동작 규칙이 복잡한 부분이 있습니까?
4. crawl 시 **반드시 열어봐야 하는 상세 화면, 탭, 모달, 패널, 목록 row action**은 무엇입니까?
5. **저장, 삭제, 승인, 제출, 신규 버전 생성**처럼 **금지하거나 관찰만 해야 하는 상태 변경 액션**은 무엇입니까?

본 5 질문은 시작 1회만 묻는다. 1차 가공 후(단계 12b)에서 추가 후보가 있는지 한 번 더 확인하는 재확인 게이트가 있고, 그 외에는 흩어진 추가 질의를 만들지 않는다.

답변은 자동으로 `qa-handoff/<project>/input-manifest.yaml > downstream_enrichment.developer_deep_scope.questions_round[]`에 기록된다. 5번 답변(forbidden_actions 후보)은 단계 1c `execution_gate.forbidden_actions[]`의 1차 입력으로 받아 확정된다.

---

## 6. 단계 1c — execution gate 3문 (v0.2.9 신규)

deep-scope 5문 직후·자료 폴더 경로 입력 직전에 Scouter가 다음 3문을 묻는다. **액션별 재확인 폐기 — 시작 1회 게이트로 환경·금지 액션·진행 승인을 한 번에 결정**한다.

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

결과는 3곳에 동기 기록:
- `input-manifest.yaml > execution_gate:` (11필드 메타 SoT)
- `feature-spec.md` frontmatter `execution_policy:` (5필드)
- `ui-menu-mindmap.md` frontmatter `execution_policy:` (5필드, feature-spec.md와 1:1 일치 강제)

**v0.2.9 표현 변경**: v0.2.8 표현 layer → "**승인 범위 밖 상태 변경 액션 금지**". 본 게이트의 decision이 결정한 실행 범위 안의 액션만 수행하고, 범위 밖은 관찰만 또는 금지. 운영 환경·운영 데이터 환경 상태 변경 액션은 decision 무관 항상 금지.

본 게이트는 시작 1회만 묻는다. 단계 9e verifier·후공정 reviewer는 본 게이트 결정만 참조하고 액션별 재확인 안 함.

---

## 7. 단계 4a — README discovery gate (v0.2.9 신규)

자료 폴더 경로 수신 직후·단계 5 자동 스캔 직전에 Scouter가 다음 4 후보 패턴으로 README를 탐색한다.

- `README.md` (repo root)
- `README.*` (repo root — README.txt·README.rst·README.adoc 등)
- `docs/README.md`
- `docs/**/README.md`

발견 시 다음을 추출:
- 문서 경로 후보 (PRD·UC·spec·design·docs 상대 경로)
- 기능/모듈명·도메인 용어 후보
- 실행/테스트 환경 설명 (단계 1c execution_gate의 1차 입력 힌트로만, 직접 단정 X)
- API/docs 링크 (Swagger·OpenAPI·외부 문서 URL)

**README는 요구사항 SoT가 아니라 탐색 힌트.** 발견한 경로는 **즉시 자료 폴더에 포함하지 않고 개발자 확인 후 승격**한다. Scouter가 묻는 발화 예시:

```
README에서 다음 경로를 찾았습니다.
- <발견 경로 1> (kind: prd)
- <발견 경로 2> (kind: docs)

이 경로들을 Scouter 입력 자료로 포함해도 됩니까?
- 포함할 항목 / 제외할 항목 / 최신본 여부 / 다른 경로 추가 필요 여부를 알려주세요.
```

개발자 답변 후:
- 확인된 경로 → `found_files[]` (categories 매핑은 단계 5 큐레이터 진입 후) + `readme_discovery.developer_confirmed_paths[]` 기록
- 제외된 경로 또는 stale로 분류된 경로 → `readme_discovery.rejected_paths[]` + 사유 명시
- 새로 추가된 경로 → 자료 폴더 경로 추가 (단계 4 재진입)

`AGENTS.md` / `CLAUDE.md` / `.cursorrules`는 발견 시 `readme_discovery.agent_guidance_files[]` (top-level 배열)에 운영 지침으로 별도 기록. **제품 요구사항으로 취급하지 않음** — feature-spec.md §1 행으로 직접 변환 X.

README가 인용한 secret·운영 URL·배포 정보는 산출물에 복사 X. 단계 1c execution_gate의 environment_class 결정 시 힌트로만 사용 가능 (개발자 확정 필요).

README 부재 시 본 게이트 skip + `readme_discovery.scanned: false` 기록.

---

## 8. 개발자 답변 방식

### 8-1. 자유 텍스트 OK

질문에 대한 답변은 자연어 텍스트로 한 번에 답해도 되고, 항목별로 나눠 답해도 된다. Scouter 본체(Sonnet)가 답변을 자동 분류한다.

예시 답변 (단계 1b deep-scope 5문):
```
1. 핵심 기능: <기능 A>·<기능 B>·<기능 C>
2. 깊은 뎁스 화면: <화면 A>(/path 또는 화면명) — Step·Parameter·변수 marker가 있음
3. 복잡 동작: <기능>의 변수 lifecycle, <기능>의 상태별 편집 제한, <기능>의 전자서명·감사추적
4. 반드시 열어봐야 할 항목: <화면> 안의 <탭/모달/패널/row action>
5. 금지·관찰만 해야 하는 상태 변경 액션: 저장·삭제·승인·신규 버전 생성·전자서명
```

예시 답변 (단계 1c execution gate 3문):
```
1. 현재 환경은 dev. 운영 데이터 섞이지 않은 dev DB 사용.
2. 금지 액션 없음.
3. 진행 OK — 테스트 데이터로 상태 변경 액션까지 실행 검증.
```

이 경우 decision = `full-execute`, reviewer_status = `EXECUTED-TEST-ENV`로 기록된다.

### 8-2. 모르면 "모름"으로 답변

특정 질문에 대해 자료가 없거나 정책이 확정되지 않은 경우 "모름" 또는 "현재 미정"으로 답변하면 된다. Scouter는 해당 항목을 `[자료 부족]` 또는 `[상세 화면 구조 부족]` 마커로 남기고 추정하지 않는다.

단계 1c execution gate 3문 중 답변이 부재하거나 환경이 불명확하면 decision = `context-insufficient`로 결정되어 **실행 금지** 상태가 된다. 답변 갱신은 명인 명시 재실행 시만 가능.

### 8-3. 민감 접근 정보는 본 문서에 직접 적지 말 것

답변 중 다음 정보는 **자료 폴더·답변 텍스트에 직접 기입하지 말 것**:

- 운영 계정 ID / PW
- API key / Token / 인증 토큰
- 고객 데이터 / PHI / 개인정보

대신:
- 테스트 전용 계정 ID는 답변에 적어도 좋다 (운영 계정은 절대 금지).
- 비밀번호·토큰은 zip 암호화 + 별도 채널(1password / 메신저 DM / 사전 합의된 민감 정보 저장소) 전달.
- Scouter는 민감 접근 정보 검출 시 답변 본문 placeholder로 대체하고 별도 채널 안내를 출력한다.

### 8-4. 상태 변경 액션 표시 — execution_gate.decision 기반 자동 처리

단계 1c execution gate가 결정한 decision에 따라 단계 1b 5번 답변(forbidden_actions 후보)이 자동 처리된다.

- `full-execute`: 금지 항목 0건 — 모든 상태 변경 액션이 테스트 환경에서 실행 가능
- `partial-execute`: forbidden_actions[] 항목은 관찰만, 나머지는 실행 가능
- `observe-only`: 모든 상태 변경 액션 실행 금지, 관찰만
- `context-insufficient`: 실행 금지 (환경 불명확)

명시하지 않은 액션은 단계 1c 게이트의 decision을 따른다. 명시한 액션 + decision 둘 다 보존되어 후공정에서 참조 가능.

---

## 9. 산출물 기대값 (v0.2.9 최종 읽기 산출물 2종)

Scouter 실행이 완료되면 자기 개발 폴더의 `qa-handoff/<project>/`에 다음 산출물이 생성된다.

```
qa-handoff/<project>/
├── feature-spec.md                      ← v0.2.9 최종 읽기 산출물 1/2 (단일 markdown, §0~§8 9섹션)
│   * §0 표지 (메타 14항목 + execution_gate 3행)
│   * §1 기능 행 17컬럼 (FR-<PROJECT>-NNN)
│   * §2 비기능 요구 9컬럼 (NFR-<PROJECT>-NNN)
│   * §3 사용자 스토리 9컬럼 (US-<PROJECT>-NNN)
│   * §4 권한 매트릭스 (받기 04 흡수)
│   * §5 상태 전이 요약 (받기 02 흡수)
│   * §6 용어집 (받기 05 흡수)
│   * §7 변경 이력 (append-only 7컬럼)
│   * §8 마인드맵 대조 결과 (단계 9d.5 cross-check 결과 — 방향 A 검증 1~4 marker)
├── ui-menu-mindmap.md                   ← v0.2.9 최종 읽기 산출물 2/2 (단일 markdown, §0~§6 7섹션)
│   * §0 범례 (★·★상세·⚠·marker 5종)
│   * §1 Mermaid mindmap (시각 보조 — 최대 6단계 깊이)
│   * §2 노드 상세 표 (SoT — 11컬럼, 노드 enum 14종)
│   * §3 노드 종류 enum
│   * §4 deep_screen_targets[] 매핑
│   * §5 도출 근거 (pre_crawl·post_crawl·crawl 결과 통계)
│   * §6 기능정의서 대조 결과 (단계 9d.5 cross-check 결과 — 방향 B 검증 1~3 marker)
├── domain-knowledge/                    ← 받기 5종 (양식 변환 X, feature-spec.md/ui-menu-mindmap.md 본문에서 인용·요약 흡수)
│   ├── 01-user-scenario.<원본 확장자>   ← _source/ 보존 + feature-spec.md §1·§3 인용
│   ├── 02-state-transition.<원본 확장자> ← _source/ 보존 + feature-spec.md §5 요약 흡수
│   ├── 03-screen-layout.<원본 확장자>   ← _source/ 보존 + ui-menu-mindmap.md로 대체
│   ├── 04-permission-matrix.<원본 확장자> ← _source/ 보존 + feature-spec.md §4 요약 흡수
│   └── 05-glossary.<원본 확장자>        ← _source/ 보존 + feature-spec.md §6 요약 흡수
├── _source/                             ← 모든 입력 자료 원본 사본 (read-only, GxP 추적 + 재현 자산)
├── input-manifest.yaml                  ← 메타·재현 자산 (schema_version "0.2.9" + 신규 슬롯 4종)
├── scout-log.md                         ← 질의·결정·게이트 이력 (append-only)
└── research-seed.md                     ← 연구팀 입력 자산 (후공정용, deep_screen_targets[] 있을 때만 생성)

knowledge/<project>/shared/pages/         ← crawl 증거 자산 (ui-menu-mindmap.md §2 evidence 컬럼에서 인용)
├── ui-crawl-manifest.yaml
└── *.yaml                                ← 화면별 capture (Playwright/Chrome MCP 등록 시 옵션)
```

### 9-1. ui-menu-mindmap.md 구조 — 메인 화면 대메뉴 트리 기준

`ui-menu-mindmap.md`는 메인 화면(로그인 직후 진입 화면)을 root로 두고 6단계 깊이까지 트리를 그린다.

```
root (메인 화면)
└── menu-l1 (대메뉴)
    └── menu-l2 (중메뉴)
        └── screen (라우트 단위 화면)
            └── tab / panel / modal / table (화면 내 1차 구조)
                └── row-action / button / field / link / form (leaf)
```

각 노드는 §2 노드 상세 표 11컬럼 1행으로 기록: 경로·노드 종류·부모 경로·SCR-ID·deep_target·marker·risky·role 노출·gap·FR-ID 인용·evidence.

execution_gate.forbidden_actions[]에 등재된 상태 변경 액션 노드는 ⚠ 마커 부착 (`partial-execute`/`observe-only` decision 시). developer_deep_scope의 must_open_targets[]·deep_screen_targets[]는 ★·★상세 마커.

### 9-2. cross-check 결과 위치 — feature-spec.md §8 + ui-menu-mindmap.md §6

단계 9d.5 cross-check 게이트는 두 산출물의 양방향 정합을 검증하고 결과를 다음 3곳에 동기 기록한다:

| 위치 | 기록 내용 |
|---|---|
| `feature-spec.md` §8 마인드맵 대조 결과 | 방향 A 검증 1~4 결과 — FR → 화면/상태/권한/위험 액션 매핑 누락 marker |
| `ui-menu-mindmap.md` §6 기능정의서 대조 결과 | 방향 B 검증 1~3 결과 — leaf 노드 → FR 인용 / 위험 액션 비고 / deep target FR 분해 marker |
| `input-manifest.yaml > two_doc_cross_check:` | 요약 메타 — result·fr_mapping_rate·leaf_mapping_rate·risky_action_dual_marked·notes |

판정 enum 4종:
- `PASS`: 방향 A·B 모두 매핑률 100% + 위험 액션 양쪽 표시
- `PASS_WITH_NOTES`: 매핑률 < 100%이지만 모든 미매핑 항목이 marker로 빠짐없이 부착됨
- `FAIL`: marker 부착 누락 또는 위험 액션 한쪽만 표시
- `NOT_RUN`: cross-check 미실행 초기 상태 (마이그레이션 직후 또는 단계 9d.5 진입 전)

**자동 보정 X — marker만 남기고 명인 검토 후 결정** (Auto-Healing Loop 차단 패턴).

### 9-3. 본 단계에서 만들어지지 않는 것

- **Google Sheets 기능정의서 시트** — QA 후공정 책임 (§10 참조). Scouter는 markdown까지만 생성하고 Sheets 신규 생성·갱신·공유는 수행하지 않는다.
- **TC (테스트 케이스)** — QA 측 `tc-writer`·`launch-tc-writer` 책임.
- **Playwright 스크립트** — QA 측 `script-generator`·`launch-script-generator` 책임.
- **baseline 머지 / 정식 발행 / 라이브 데이터 변경** — 모두 명시 승인 + 후공정 단계.

---

## 10. QA 후공정 안내 (Scouter 산출물 인계 이후)

개발자가 산출물을 QA에 인계하면 QA가 다음을 수행한다. **본 단계는 Scouter 본체의 책임 영역이 아니며**, QA 메인 + Codex 외부감사(선택) + 연구팀(선택)의 조합으로 진행된다.

### 10-1. 진행 순서

1. **수령** — QA가 `qa-handoff/<project>/` 패키지를 `knowledge/<project>/scout-handoff/`로 흡수.
2. **baseline 비교** — 기존 baseline(있는 경우)과 candidate 산출물을 대조해 누락·신규·conflict를 정리. baseline이 없는 신규 프로젝트는 이 단계 건너뜀.
3. **candidate 보정** — QA 메인이 1차 검토 후 명백한 typo·incompleteness만 수정하고 정책 단정·기능 확정은 보류. 보정 결과는 별도 candidate 파일로 보관(baseline 자동 머지 금지).
4. **Google Sheets 신규 생성** — QA 측 스킬 `qa-scout:markdown-to-sheets` 호출로 단일 `feature-spec.md`를 QA 본인 계정의 Google Sheets로 이행. **★ 이 단계는 Scouter 본체가 아니라 QA 후공정 책임이다** — Google Sheets MCP는 Scouter plugin의 필수 의존성이 아니다.
   - **옵션 A (기본, 권장)**: 5시트 — 01_표지·02_변경이력·03_기능정의서·04_비기능요구·05_사용자스토리. feature-spec.md §4·§5·§6·§8은 markdown SoT 유지.
   - **옵션 B**: 8시트 — 옵션 A + 06_권한매트릭스·07_상태전이·08_용어집. §8 cross-check는 markdown SoT.
   - **옵션 C**: 1시트 — 03_기능정의서만 (최소 발행).
   - **`ui-menu-mindmap.md`는 Sheets 이행 X** — markdown 보조 산출물로 유지 (Mermaid 트리는 Sheets 친화도 낮음).
5. **reviewer 검증** — 새 Sheets를 기준으로 Codex Playwright reviewer 또는 명인 직접 검수를 진행. 10 enum 판정(PASS · FAIL · SCREEN-MISSING · SPEC-MISSING · PERMISSION-MISMATCH · BEHAVIOR-MISSING · VARIABLE-MISMATCH · STATE-MISMATCH · NOT-TESTED-RISKY-ACTION · CONTEXT-INSUFFICIENT) 중 하나로 모든 행을 분류.
6. **반영 결정** — 명인 보고 + 개발팀 후속 확인(자료 요청·확정 요청 분리 패키지) 후 baseline에 머지.

### 10-2. 책임 경계 요약

| 영역 | 책임 | 산출물 종착점 |
|---|---|---|
| **Scouter (qa-scout 플러그인, 본 가이드 범위)** | 개발자 자료 → markdown 2종 정형화 + execution_gate + README discovery + cross-check 수집 | `qa-handoff/<project>/` |
| **QA 후공정 (메인 QA 파트너)** | baseline 비교 · candidate 보정 · **Google Sheets 신규 생성 (옵션 A/B/C)** · reviewer 발주 · 명인 보고 | `knowledge/<project>/scout-handoff/` + Google Sheets |
| **연구팀 (`ai-research/`, Gemini CLI, 선택형)** | candidate research-pack 검증 + evidence-matrix 보강 | `ai-research/results/<date>-<project>-feature-spec-enrichment/` |
| **감사팀 (`ai-audit/`, Codex, 선택형)** | Sheets 기준 reviewer 발주 | `ai-audit/results/<date>-<project>-feature-spec-playwright-review/` |

### 10-3. 라이브 검증 진입 조건 (QA 후공정 단계)

라이브 검증이 필요한 경우, QA 후공정에서 다음 4 조건을 모두 충족해야 진입한다.

1. 운영 환경과 분리된 스테이징/테스트 환경 정보 확보
2. 테스트 전용 ID + PW 계정 확보 (운영 계정 사용 금지)
3. 외부 메일/알림 차단 환경 확인
4. 명인 명시 승인 + execution_gate.decision 준수 (`observe-only`·`context-insufficient` 시 read-only 진입 강제)

위 4 조건 중 하나라도 미충족 시 reviewer 결과는 `CONTEXT-INSUFFICIENT`로 남는다. Scouter 본체에서는 라이브 환경에 단계 1c execution gate decision 외 자율로 접속하지 않는다.

---

## 11. 자주 묻는 질문

### Q1. 본 가이드 따라했더니 Scouter가 상태 변경 액션을 실행하지 않는데, 라이브에서 정말 동작하는지 어떻게 확인합니까?

단계 1c execution gate의 decision에 따라 다릅니다.

- `full-execute`: 테스트 환경에서 상태 변경 액션까지 실행 검증을 수행합니다.
- `partial-execute`: 허용된 액션은 실행, forbidden_actions[]는 관찰만.
- `observe-only` / `context-insufficient`: 상태 변경 액션 실행 금지. 라이브 동작 확인은 QA 후공정의 reviewer 단계에서 §10-3 4 조건을 충족한 후 read-only 진입 또는 명시 승인 테스트 환경에서 실행됩니다.

### Q2. 답변 5개 중 일부를 모른다고 했는데 Scouter가 다시 물어봅니까?

단계 12b post-crawl 재확인 게이트에서 1회 다시 묻습니다. 큐레이션·정형화 1차 결과를 본 후 추가 후보(예: "이 화면도 깊은 뎁스로 보이는데 맞습니까?") + 빠진 상태 변경 액션 후보를 묻습니다. 이 1회로 종결되며 무한 질의 루프를 만들지 않습니다.

단계 1c execution gate 3문은 시작 1회만 묻고, 액션별 재확인은 폐기됐습니다. 환경이 바뀐 경우 명인 명시 재실행으로만 갱신합니다.

### Q3. Google Sheets MCP / Playwright MCP / Codex / Gemini CLI가 설치되어 있어야 합니까?

**아니오**. 본 Scouter plugin의 필수 의존성은 Claude Code 본체뿐입니다.

- **Google Sheets MCP**: QA 측 단계 17a `markdown-to-sheets` 호출 시만 필요 (개발자 본체 사용 X).
- **Playwright MCP**: 단계 9e verifier가 라이브 URL 제공 + execution_gate가 허용 시 조건부 사용, 미등록 시 graceful skip(에러 X)으로 정상 종료.
- **Gemini CLI**: 연구팀(선택형 ai-research 발주) 사용 시만 필요.
- **Codex exec**: 감사팀(선택형 ai-audit 발주) 사용 시만 필요.

### Q4. v0.2.7/v0.2.8 산출물을 v0.2.9로 어떻게 옮깁니까?

`plugins/qa-scout/scripts/migrate-to-v029.mjs` 사용 (§3 참조). dry-run → 사용자 확인 → write 순서.

- write 모드는 backup 생성 후 schema_version 갱신 + 누락된 신규 슬롯 4종 append.
- 기존 `downstream_enrichment` · `developer_deep_scope` · `deep_screen_targets[]` 구조는 모두 보존.
- 이미 v0.2.9면 no-op (멱등성).
- 마이그레이션은 게이트 결과를 추정하지 않고 안전 기본값만 채움. 실제 결과는 단계 1c/4a/9d.5 재실행으로 채워야 함.

### Q5. README가 발견됐는데 그 내용을 그대로 기능정의서에 옮겨도 되나요?

안 됩니다. README는 요구사항 SoT가 아닌 **탐색 힌트**. README에서 추출한 값은 `feature-spec.md` §1 16번 인풋 출처에 `README §x.x` 인용 + 17번 비고에 `[README 출처 — 본문 확인 필요]` 마커를 부착합니다. 최신성·정합성은 단계 6 큐레이션에서 확인합니다.

`AGENTS.md` / `CLAUDE.md` / `.cursorrules`는 `readme_discovery.agent_guidance_files[]`에 운영 지침으로 별도 기록하되 제품 요구사항으로 변환하지 않습니다.

### Q6. `feature-spec.md`와 `ui-menu-mindmap.md`가 서로 어긋나면 어떻게 됩니까?

단계 9d.5 cross-check 게이트가 양방향(FR → 노드 / 노드 → FR) 검증을 1회 실행합니다. 누락은 marker(`[화면 위치 확인 필요]` / `SPEC-MISSING` 등)로 양쪽에 남깁니다. 자동 보정 X — 명인 검토 후 결정합니다.

### Q7. 본 가이드 산출물을 QA에 어떻게 인계합니까?

3 옵션 중 합의된 방식으로:
- **(a) zip + 메신저**: `Compress-Archive qa-handoff/<project>/ qa-handoff-<project>-<YYYYMMDD>.zip` 후 첨부
- **(b) git push**: `qa-handoff/`를 git 추적하고 commit + push (단, 민감 접근 정보가 본문에 들어가지 않도록 사전 점검)
- **(c) 클라우드 공유 링크**: Google Drive·OneDrive 등 공유 링크 (인증 필수)

QA 측은 수령 후 무결성 점검(input-manifest 일치 + hash 검증)을 수행합니다.

---

## 12. 참조

- 본 plugin spec (v0.2.9 최신): `../../docs/qa-scout/spec.md` (최종 산출 문서 2종 + 단계 1c/4a/9d.5)
- 이전 spec: `../../docs/qa-scout/spec.md` (v0.2.8 deep screen coverage)
- 이전 spec: `../../docs/qa-scout/spec.md` (v0.2.7 개발자 환경 하네스)
- 이전 spec: `../../docs/qa-scout/spec.md` (v0.2.6 커버리지 자가 검증)
- 이전 spec: `../../docs/qa-scout/spec.md` (v0.2 골격)
- public install 가이드: [cmi94/qa-kit](https://github.com/cmi94/qa-kit)

---

## 13. 한 줄 요약

> 본 가이드를 따라 `[PROJECT: <project>] scout 호출`로 시작하면, Scouter v0.2.9가 engagement context 5항목 + deep-scope 5문 + **execution gate 3문 (v0.2.9 신규)** + 자료 폴더 큐레이션 + **README discovery (v0.2.9 신규)**를 거쳐 `qa-handoff/<project>/`에 **단일 markdown 2종**(`feature-spec.md` + `ui-menu-mindmap.md`)을 생성하고 **단계 9d.5 cross-check**로 양방향 정합을 검증한다. **승인 범위 밖 상태 변경 액션은 금지**되고(execution_gate.decision 기반), **Google Sheets 생성은 QA 후공정 책임 (옵션 A/B/C 분기)**이며, **모르는 것은 추정 채움 없이 `[자료 부족]` 마커로 남는다**.
