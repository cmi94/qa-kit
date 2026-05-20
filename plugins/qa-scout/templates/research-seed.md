---
template: research-seed
spec: ../../docs/qa-scout/spec.md
purpose: qa-scout handoff 직후 연구팀(또는 enrichment 파이프라인)이 첫 번째로 읽는 입력. 깊은 화면 뎁스/핵심 기능 누락 방지 게이트.
location_hint: qa-handoff/{project}/research-seed.md 또는 knowledge/{project}/scout-handoff/research-seed.md
---

# research-seed — {project}

> 본 파일은 **연구 입력**이지 기능정의서가 아니다. 결정/단정은 연구팀 산출물(`feature-spec-research-pack`)과 메인 QA 파트너의 검토 단계에서 이루어진다. 본 시드를 자동 반영하지 않는다.

## 1. source inventory

`input-manifest.yaml`에 기록된 자료를 형태별로 1줄씩 인용한다.

| 형태 | 경로 | 버전·작성일 | 신뢰도 |
|---|---|---|---|
| PRD | <경로> | <YYYY-MM-DD> | high/medium/low |
| UC | <경로> | ... | ... |
| 화면 capture (UI crawl) | `knowledge/{project}/shared/pages/<screen>.yaml` | ... | medium |
| 권한 매트릭스 | ... | ... | ... |
| 상태 전이 | ... | ... | ... |
| 도메인 용어집 | ... | ... | ... |
| ERD/아키텍처 | ... | ... | ... |
| 운영 매뉴얼 | ... | ... | ... |

## 2. handoff summary

qa-scout가 산출한 기능정의서 md 초안의 골자를 1~2단락으로 요약한다.

- 분해된 FR 개수, `[자료 부족]` 마커 개수, 17컬럼 채움률 요약.
- 1차 누락이 의심되는 영역(예: detail / editor / variable / step / parameter).

## 3. known gap signals

surface crawl만으로는 못 잡는 deep gap의 1차 후보를 적는다. 본 섹션은 후속 연구팀이 "어디부터 파야 하는가"를 결정하는 입력이다.

- `[상세 화면 구조 부족]`: 화면 capture에 `inputs: []`이지만 PRD/UC에 입력·편집이 있는 경우.
- `[변수 동작 자료 부족]`: 변수 패널·단일/테이블 변수·marker·PDF 치환·atomic이 문서 또는 코드에 등장하나 기능 행 없음.
- `[상태별 UI 확인 필요]`: Draft/Approved/Pending 등 상태별 편집 가능 여부 분기.
- `[권한별 UI 확인 필요]`: role별 노출·동작 차이.
- `[동적 UI 확인 필요]`: 클릭·선택·입력 후 UI 변화, 저장·로드 lifecycle.
- `[위험 액션 미검증]`: 저장/삭제/승인/제출/신규 버전 생성 등.
- `[문서-화면 충돌]`: 문서에 있으나 화면 미관찰, 또는 반대.

각 신호별로 "어떤 자료의 어떤 줄을 보면 후보인지" 1줄 인용한다.

## 4. deep screen targets

`input-manifest.yaml > downstream_enrichment.deep_screen_targets[]`를 그대로 또는 정제하여 반영한다.

| id | route | 선정 사유 | 필수 관찰(탭/모달/패널/row action) | 위험 액션 (미클릭) | evidence |
|---|---|---|---|---|---|
| <id> | </path> | prd-keyword / capture-inputs-empty / gxp-data-integrity / developer-pinned 등 | tabs/modals/panels/row actions | 저장/승인/삭제 등 | PRD:line, UC:section, design:line, capture:yaml |

## 5. required evidence dimensions

기능정의서 행이 확정되기 전, 연구팀이 모아야 할 증거 차원.

- 문서 근거 (PRD/UC/매뉴얼/규정)
- 화면 근거 (UI crawl capture, screenshot)
- 코드 근거 (controller/route/handler, 변수 처리 함수)
- 상태 근거 (상태 전이도, status enum)
- 권한 근거 (RBAC 매트릭스, role gate)
- 동적 동작 근거 (Step/Parameter/Variable/Editor/PDF 치환 lifecycle)

각 차원에 대해 "이 프로젝트에서 어디까지 모았고 어디부터 부족한가"를 1줄 코멘트.

## 6. developer deep-scope answers

`input-manifest.yaml > downstream_enrichment.developer_deep_scope.questions_round[]` 답변을 그대로 인용한다.

- 핵심 기능: ...
- 깊은 뎁스 화면: ...
- 복잡 동작: ...
- 반드시 열어볼 항목(탭/모달/패널/row action): ...
- 위험 액션(클릭 금지): ...

post-crawl 재확인 게이트 결과가 있으면 `confirmation_rounds[]`도 인용한다.

## 7. forbidden assumptions

본 시드를 받는 모든 후공정에 적용되는 단정 금지 규칙.

- 화면에 보이지 않는 기능을 단정하지 말 것.
- 코드 한 줄로 정책을 단정하지 말 것.
- 사용자 시나리오·권한 규칙을 추정 단정하지 말 것.
- `[자료 부족]`을 회피하기 위해 억지 확정하지 말 것.

## 8. risky-action policy

본 프로젝트에서 관찰만 하고 자동 클릭 금지인 액션을 적는다. Playwright/MCP/연구팀/reviewer 공통 적용.

- <저장 / 삭제 / 승인 / 제출 / 신규 버전 생성 등>
- 위 항목은 reviewer 결과에서 `NOT-TESTED-RISKY-ACTION`으로 남긴다.
- 라이브 환경 또는 운영 데이터에 영향을 줄 수 있는 액션은 추가 사용자 승인이 있을 때만 실행한다.

---

## 산출물 사용 가이드

- 본 시드는 연구팀이 `feature-spec-research-pack`을 만들 때 1차 입력으로 사용한다.
- 본 시드를 기능정의서로 자동 변환하지 않는다.
- 본 시드는 메인 QA 파트너가 Sheets 업로드 결정 시 함께 검토한다.
- Codex Playwright reviewer는 본 시드의 `deep_screen_targets`와 `risky-action policy`를 강제 기준으로 본다.
