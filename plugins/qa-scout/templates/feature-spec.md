---
template: feature-spec
schema_version: "0.3.0"
spec: ../../docs/qa-scout/spec.md
upstream:
  - ../../docs/qa-scout/spec.md
purpose: |
  scout v0.3.0 최종 읽기 산출물 1/2. "무엇을 해야 하는가"를 단일 markdown으로 정형화한다.
  v0.3.0 Coverage Completeness Gate — F-카탈로그 단일 SoT 폐기, 6 인풋 합집합 변환
  (F-catalog + FS-derived + PRD-derived + domain-derived + user-manual-derived + mindmap-leaf-derived).
  §1 9번 컬럼(상세 정책)은 8 카테고리 정형 강제 (핵심 룰·경계 조건·상태 전이·권한 게이트·
  데이터 무결성·화면 동작·부수 효과·참조). §1 각 FR에 input-manifest.yaml fr_sources 객체 부착.
  단계 9c.5 UI surface 감지 (unmapped-leaves.yaml candidate 분리). 단계 9c.6 자가 검증 9항
  (verify-8-categories.py). 단계 17a Sheets 옵션 A/B/C/D 분기 (D=18컬럼 인풋 출처 매핑).
  단계 17b D-3 readback diff 차단 게이트 (verify-readback.py).
location_hint: qa-handoff/{project}/feature-spec.md
project: <project>
domain: <중분류 코드>
ai_author: scout v0.3.0 (<model>)
created: <YYYY-MM-DD>
last_updated: <YYYY-MM-DD>
linked_artifacts:
  ui_menu_mindmap: ui-menu-mindmap.md
  input_manifest: input-manifest.yaml
  scout_log: scout-log.md
  research_seed: research-seed.md
  source_dir: _source/
  sheets_url: <Sheets URL 또는 null>     # 단계 17a markdown-to-sheets 결과
sheets_mapping:
  primary_sheet: 03_기능정의서            # 옵션 A/B/C=17컬럼, D=18컬럼 (인풋 출처 17번 매핑)
  side_sheets: [01_표지, 02_변경이력, 04_비기능요구, 05_사용자스토리]
  sheets_option: <A | B | C | D>          # 단계 17a 인터뷰에서 선택. D=GxP 추적성 강화
  input_source_column_published: <true | false>  # 옵션 D 발행 시 true
  excluded_from_sheets: [§4_권한매트릭스, §5_상태전이, §6_용어집, §8_마인드맵대조결과]   # markdown 본문에만, Sheets 미이행
execution_policy:                         # v0.3.0 신규 — SDD §5-10
  decision: <full-execute | partial-execute | observe-only | context-insufficient>
  reviewer_status: <EXECUTED-TEST-ENV | PARTIAL-OBSERVED | NOT-TESTED-PROD-RISK | CONTEXT-INSUFFICIENT>
  environment_class: <local | dev | qa | staging | prod | unknown>
  forbidden_actions: []
  gate_decided_at: <ISO 8601>
related_specs:
  - ../../docs/qa-scout/spec.md
  - ../../docs/qa-scout/spec.md
---

# {project} 기능정의서

> v0.3.0 최종 읽기 산출물. 표지·기능 정의·비기능·사용자 스토리·권한·상태 전이·용어집·변경 이력·마인드맵 대조 결과 9개 섹션을 단일 markdown에 통합. 시트 분리는 §1 본체(17컬럼)에만 적용(단계 17a markdown-to-sheets), 나머지 섹션은 markdown 본문 SoT.

## §0 표지 (메타)

| 항목 | 값 |
|---|---|
| 프로젝트명 (Project Name) | {project_name} |
| 솔루션/제품 종류 (Product Type) | {product_type} |
| 핵심 가치 제안 (Value Proposition) | {value_proposition} |
| 대상 사용자 (Target Users) | {target_users} |
| 배포 지역 (Deploy Region) | [현업 확인 필요] |
| 플랫폼 (Platforms) | {platforms} |
| 문서 버전 (Document Version) | 0.1 |
| 문서 상태 (Status) | Draft |
| AI 작성자 (AI Author) | scout v0.3.0 (`<model>`) |
| 사람 검수자 (Human Reviewer) | [현업 확인 필요] |
| 최초 작성일 (Created) | {YYYY-MM-DD} |
| 최종 수정일 (Last Updated) | {YYYY-MM-DD} |
| 관련 문서 (Related Docs) | {input_sources} |
| execution gate decision | `<full-execute | partial-execute | observe-only | context-insufficient>` |
| reviewer status | `<EXECUTED-TEST-ENV | PARTIAL-OBSERVED | NOT-TESTED-PROD-RISK | CONTEXT-INSUFFICIENT>` |
| 환경 (environment_class) | `<local | dev | qa | staging | prod | unknown>` |

채움 가이드:
- "[현업 확인 필요]" 슬롯은 사용자 검수자가 채움 (단계 17~).
- execution gate / reviewer status / environment_class 값은 frontmatter `execution_policy:`와 동기.
- 변경 시 §7 변경이력 행 추가.

### execution_gate.decision ↔ reviewer_status 1:1 매핑 (SDD §5-10-2)

| execution_gate.decision | reviewer_status | 의미 |
|---|---|---|
| `full-execute` | `EXECUTED-TEST-ENV` | 개발/QA/테스트 환경이며 금지 액션이 없어 승인 범위 안에서 상태 변경 액션까지 실행 가능 |
| `partial-execute` | `PARTIAL-OBSERVED` | 일부 상태 변경 액션은 금지되어 허용된 범위만 실행하고 나머지는 관찰/기록 |
| `observe-only` | `NOT-TESTED-PROD-RISK` | 운영/운영성 데이터/금지 액션 위험 때문에 상태 변경 액션은 실행하지 않고 관찰만 수행 |
| `context-insufficient` | `CONTEXT-INSUFFICIENT` | 환경·접근 조건·금지 액션 정보가 부족해 실행 판단 불가 |

본 표는 frontmatter `execution_policy.decision`·`execution_policy.reviewer_status` 두 필드를 채울 때 1:1 매핑 강제 기준이다. enum 외 값 금지.

## §1 기능 행 — 17컬럼 (단계 9c — docs-to-function-spec)

> ID 패턴은 PROJECT 헤더로부터 동적 치환. 예시는 `<PROJECT>` 변수 placeholder 사용.

### 17컬럼 정의

| # | 컬럼 | 비고 |
|---|---|---|
| 1 | 기능 ID | `FR-<PROJECT>-NNN`, 결번 허용 |
| 2 | 화면 ID | `SCR-<PROJECT>-NNN` |
| 3 | 페이지 경로 / Depth | PRD 표기 그대로 |
| 4 | 중분류 | 기능 영역 (프로젝트 정의 단위) |
| 5 | 기능명 | 명사형 15~30자 |
| 6 | 기능 목적 (Why) | "···을 위해 ···한다" |
| 7 | 기능 요약 (1줄) | 행위·결과 |
| 8 | 사전 조건 | 권한·상태·이전 단계 |
| 9 | 상세 정책 / 기능 설명 | PRD 본문 인용 + BR 코드 |
| 10 | 입력 (Input) | 필드/타입/필수/검증 규칙 |
| 11 | 처리 로직 (Process) | 1) 2) 3) 단계 |
| 12 | 상태 전이 | "X → Y" |
| 13 | 출력 (Output) | 화면 갱신·이벤트·DB |
| 14 | 예외/에러 처리 | 케이스/메시지·HTTP 코드·BR — 음성 TC 핵심 |
| 15 | TC ID | `TC-<PROJECT>-NNN` 다중 (RTM, 후공정 채움) |
| 16 | 인풋 출처 | `(<source> §x.x; <보완 문서> §y.y; BR-<도메인>-NN)` — 행 단위 GxP 추적 |
| 17 | 비고 | FR↔NFR cross-reference 등 자유 |

### 채움 양식 (도메인 중립 placeholder)

| 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `FR-<PROJECT>-NNN` | `SCR-<PROJECT>-NNN` | `<페이지 경로>` (Depth N) | `<중분류 코드>` | `<기능명 — 명사형>` | `<목적 — Why>` | `<요약 — 1줄>` | `<사전 조건>` | `<상세 정책 + BR-<도메인>-NN>` | `<입력 필드(타입, 필수, 검증)>` | `1) ... 2) ... 3) ...` | `<상태 X → 상태 Y>` 또는 `없음` | `<출력>` | `<예외 케이스>: <코드>` | `TC-<PROJECT>-NNN (TBD)` | `(<source> §x.x; <보완 문서> §y.y; BR-<도메인>-NN)` | `<자유 비고>` |

### 채움 가이드

- F-NNN 단위 분해 — **6 인풋 합집합 SoT** (F-catalog + FS-derived + PRD-derived + domain-derived + user-manual-derived + mindmap-leaf-derived). input-manifest.yaml `sources[]` + `source_tier_review[]` 완료된 자료 기반
- 17컬럼 모두 채움 또는 `[자료 부족]` 마커
- **9번 컬럼 (상세 정책) — 8 카테고리 정형 강제 (v0.3.0)**: 모든 FR은 9번 컬럼에 `• 핵심 룰: …` · `• 경계 조건: …` · `• 상태 전이: …` · `• 권한 게이트: …` · `• 데이터 무결성: …` · `• 화면 동작: …` · `• 부수 효과: …` · `• 참조: …` 8단 bullet 필수. 자료 부재 시 `• <카테고리>: [자료 부족] (<확인한 입력 1>, <확인한 입력 2>)` 통일 마커. 자유 흐름 cell·dash-only는 `verify-8-categories.py` FAIL.
- **각 FR에 input-manifest.yaml `fr_sources[<FR_ID>]` 객체 부착 (v0.3.0)**: `primary: <tier·path·section>` + `secondary_sources: [...]`. fr_sources 부재 FR은 작성 금지.
- 추정 금지·모호 시 즉시 질의 (5개 패턴 — 같은 용어 2의미·행위자 불명·필드 타입 불명·정의 충돌·단위 불명)
- 16번 인풋 출처 누락 행 X. 옵션 D 발행 시 17번 sheet 컬럼으로 직접 매핑
- ID 패턴은 PROJECT 헤더로 동적 치환
- 영역 헤더 이모티콘 X (그룹 mergeCells 적용 X)
- **README 1차 발견 행**: 16번에 `README §x.x` 인용 + 17번 비고에 `[README 출처 — 본문 확인 필요]` 마커 (탐색 힌트일 뿐, 단정 금지 — SDD §5-11-5)
- **단계 9c.5 UI surface 감지 (v0.3.0)**: §1 본문 자동 진입 금지. mindmap leaf ↔ §1 매핑 안 되는 후보는 `unmapped-leaves.yaml` candidate 등록 → 명인 단독 승인 후만 §1 진입 (Auto-Healing Loop 차단)
- **단계 9c.6 자가 검증 9항 (v0.3.0)**: `verify-8-categories.py` PASS + `unmapped-leaves.yaml` status candidate 0건 + cross-check 3 방향 (A·B·C) PASS

### 16번 / 17번 — evidence·deep screen mapping hint

SDD `../../docs/qa-scout/spec.md`에 따라 deep screen target 행은 다음 양식으로 출처·비고를 채운다.

#### 16번 인풋 출처 — 다중 evidence 인용

`(<문서 근거>; <화면 근거>; <코드 근거>; BR-<도메인>-NN)` 4종 중 가능한 만큼 ;-구분으로 나열.

| evidence 종류 | 예시 표기 |
|---|---|
| 문서 (PRD/UC/매뉴얼) | `<source-doc> §x.x` |
| 화면 capture | `capture:<screen_slug>.yaml#buttons[0]` |
| design 근거 | `design:<topic> §y.y` |
| 코드 근거 | `code:<path>:<line>` (확정 단정 X — evidence로만) |
| 권한 매트릭스 | `permission-matrix §<role>` |
| 상태 전이 | `state-transition §<entity>` |
| BR 코드 | `BR-<도메인>-NN` |
| README 출처 | `README §x.x` (탐색 힌트 — 단정 X) |

확정 1건만 있고 나머지가 부족하면 `[자료 부족 — <차원>]` 함께 표기. 예: `(<source-doc> §x.x; [자료 부족 — 화면 capture 없음])`.

#### 17번 비고 — deep screen / behavior marker

해당 행이 deep screen target에 속하거나 동적 동작·변수·상태 분기를 포함하면 아래 marker 명시. reviewer가 enum 판정에 활용.

| marker | 의미 | reviewer 1차 enum |
|---|---|---|
| `[상세 화면 구조 부족]` | 화면 capture가 inputs:[]이거나 패널/모달 미관찰 | SCREEN-MISSING |
| `[동적 UI 확인 필요]` | 클릭·입력 후 UI 변화 또는 lifecycle 미관찰 | BEHAVIOR-MISSING |
| `[변수 동작 자료 부족]` | 변수 marker·atomic·치환 lifecycle 미확정 | VARIABLE-MISMATCH |
| `[상태별 UI 확인 필요]` | 상태별 분기 미확정 | STATE-MISMATCH |
| `[권한별 UI 확인 필요]` | role별 노출·동작 차이 미확정 | PERMISSION-MISMATCH |
| `[승인 범위 밖 상태 변경 액션]` | execution_gate.forbidden_actions[] 등재 항목 — partial-execute / observe-only decision일 때만 부착 (full-execute는 실행 완료) | PARTIAL-OBSERVED / NOT-TESTED-PROD-RISK |
| `[문서-화면 충돌]` | 문서·화면 한쪽만 있거나 둘이 충돌 | SCREEN-MISSING / SPEC-MISSING / FAIL |
| `[README 출처 — 본문 확인 필요]` | README가 1차 출처인 행, 최신성·정합성 미확정 | CONTEXT-INSUFFICIENT |

기존 마커(`[자료 부족]`, `[화면 확인 필요]`, `[문서 근거 부족]`, `[사용자 시나리오 확인 필요]`)는 그대로 유지.

#### deep screen target 행 — 도메인 중립 예시

| 9 (상세 정책) | 16 (인풋 출처) | 17 (비고) |
|---|---|---|
| `<상태 X>` 상태에서만 `<액션>` 가능 (`<source-doc> §x.x` 대안흐름) | `(<source-doc> §x.x; capture:<screen_slug>.yaml#tables[1]; state-transition §<entity>; [자료 부족 — 동적 lifecycle 미관찰])` | `[동적 UI 확인 필요]` `[상태별 UI 확인 필요]` — deep_screen_targets[].id=`<target id>` |
| `<변수/marker>`는 `<렌더링 방식>`으로 표시되며 `<삭제 방식>` (`<source-doc> §y.y`) | `(design:<variable-topic> §y.y; <source-doc> §없음 — 문서 근거 부족)` | `[변수 동작 자료 부족]` — gap=variable-behavior-gap |

## §2 비기능 요구 — 9컬럼

### 9컬럼 정의

| # | 컬럼 | 비고 |
|---|---|---|
| 1 | NFR ID | `NFR-<PROJECT>-NNN` |
| 2 | 범주 (Category) | 보안·감사·성능·접근성·가용성·신뢰성·사용성·유지보수·관측성·호환성·지속가능성 |
| 3 | 항목 (Item) | 명사형 |
| 4 | 요구 내용 (Requirement) | 자유 텍스트 |
| 5 | 측정 지표 / 임계값 (Metric & Threshold) | 정량 지표 |
| 6 | 검증 방법 (Verification) | 코드 리뷰·단위 테스트·통합 테스트·Penetration Test 등 |
| 7 | 우선순위 (Priority) | M / S / C / W (MoSCoW) |
| 8 | 관련 기능 ID (Related FR) | `FR-<PROJECT>-NNN` 다중 (콤마 구분) |
| 9 | 비고 (Notes) | 자유 |

### 채움 양식

| 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|
| `NFR-<PROJECT>-NNN` | `<범주>` | `<항목명>` | `<요구 내용>` | `<측정 지표 / 임계값>` | `<검증 방법>` | M | `FR-<PROJECT>-NNN, ...` | `<관련 규제> §x.x, BR-<도메인>-NN` |

### 채움 가이드

- PRD 비기능 섹션·정책 문서에서 추출
- 정량 지표 가능한 것은 명시 (예: `p95 < <ms>`, `Lighthouse A11y ≥ <점수>`)
- 정량 어려운 항목은 "수동 감사" 등 검증 방법 명시
- 관련 FR 누락 X (cross-reference)

## §3 사용자 스토리 — 9컬럼

### 9컬럼 정의

| # | 컬럼 | 비고 |
|---|---|---|
| 1 | Story ID | `US-<PROJECT>-NNN` |
| 2 | 에픽 (Epic) | 묶음 단위 |
| 3 | Sprint | S1·S2·S3 |
| 4 | 사용자 스토리 | "As a ___, I want ___, so that ___" |
| 5 | 인수 기준 (G/W/T) | "Given ___ / When ___ / Then ___" |
| 6 | 관련 기능 ID | `FR-<PROJECT>-NNN` 다중 |
| 7 | 포인트 (SP) | 1·2·3·5·8 (Fibonacci) |
| 8 | 우선순위 | M / S / C / W |
| 9 | 상태 | Backlog·In Progress·Done |

### 채움 양식

| 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|
| `US-<PROJECT>-NNN` | `<에픽명>` | S1 | "As a `<역할>`, I want `<목적 행위>`, so that `<비즈니스 가치>`" | "Given `<전제>` / When `<행위>` / Then `<기대 결과 + 상태 전이 + Audit>`" | `FR-<PROJECT>-NNN` | 5 | M | Backlog |

### 채움 가이드

- PRD·유스케이스·Process Flow에서 도출
- "As a / I want / so that" 형식 엄수
- 인수 기준은 Given/When/Then 명확 분리
- 관련 FR ID 다중 가능

## §4 권한 매트릭스 (받기 04 흡수 — 요약 표)

> 원본 권한 매트릭스 자료(이미지·표·매트릭스 파일)는 `_source/`에 그대로 보존. 본 섹션은 행 단위 요약. 액션 컬럼은 본 프로젝트의 권한 매트릭스 정의에 따라 가감.

| Role | FR-ID | visible | edit | delete | approve | submit | 비고 |
|---|---|---|---|---|---|---|---|
| `<role-A>` | `FR-<PROJECT>-NNN` | ✓ | ✓ | ✗ | ✗ | ✗ | `<제약 사유>` |
| `<role-B>` | `FR-<PROJECT>-MMM` | ✓ | ✗ | ✗ | ✓ | ✗ | `<상태 X>에서만 허용` |

### 채움 가이드

- role enum은 프로젝트별 정의 — placeholder만 사용 (프로젝트별 고유 명사 X)
- 액션 컬럼은 본 프로젝트 매트릭스에 맞춰 가감 (예: review·withdraw 추가 가능)
- "✗" 셀이라도 사유 비고에 짧게 (예: `<상태 X>에서만 허용`)
- 원본이 PNG/이미지/PDF면 `_source/<file>` 인용 + 본 요약 표만 채움
- 본 §4는 Sheets 이행 X — markdown 본문 SoT (단계 17a 시 `excluded_from_sheets`)

## §5 상태 전이 요약 (받기 02 흡수 — 요약 표)

> 원본 상태 전이도(Mermaid·PNG·다이어그램)는 `_source/`에 그대로 보존. 본 섹션은 상태 × 허용 행위 × 발화 조건 요약.

| 엔티티 | 현재 상태 | 다음 상태 | 발화 조건 | 허용 role | 관련 FR-ID |
|---|---|---|---|---|---|
| `<entity>` | `<상태 X>` | `<상태 Y>` | `<발화 조건 — 액션·이벤트·시간>` | `<role list>` | `FR-<PROJECT>-NNN` |

### 채움 가이드

- 상태 enum은 프로젝트별 정의 — placeholder만 사용
- 발화 조건은 사용자 행위 / 시스템 자동 / 외부 이벤트 구분
- 한 FR이 여러 상태 전이를 트리거하면 다중 행
- 본 §5는 Sheets 이행 X — markdown 본문 SoT

## §6 용어집 (받기 05 흡수 — abc 정렬)

> ubiquitous language 원본은 `_source/`에 그대로 보존. 본 섹션은 행 단위 요약.

| 용어 (한글) | 용어 (영문) | 정의 | 동의어·금지 표현 | 관련 FR-ID |
|---|---|---|---|---|
| `<용어 한글>` | `<term-en>` | `<정의 1줄>` | 동의어: `<...>` / 금지: `<...>` | `FR-<PROJECT>-NNN` |

### 채움 가이드

- 가나다 또는 알파벳 abc 정렬 (본 프로젝트 합의)
- 동의어 → 본 정의로 통일 권장
- 금지 표현 → 사용 X (영역별 의미 충돌 방지)
- 본 §6은 Sheets 이행 X — markdown 본문 SoT

## §7 변경 이력

| 버전 | 변경일 | 변경자 | 변경 유형 | 변경 내용 | 영향받는 ID | 리뷰/승인자 |
|---|---|---|---|---|---|---|
| 0.1 | `<YYYY-MM-DD>` | scout v0.3.0 (`<model>`) | 최초 작성 | `<project>` 도메인 정형화 1차 초안: FR `<N>`건, NFR `<N>`건, US `<N>`건 | FR-<PROJECT>-001~NNN, NFR-<PROJECT>-001~NNN, US-<PROJECT>-001~NNN | [현업 확인 필요] |

### 변경 유형

- 최초 작성 (Draft 0.1)
- 검수 후 수정
- 사람 검수 통과 (1.0 정식 발행)
- 고도화 (V2 신규 기능)
- 폐기 (Deprecated)
- revert (롤백)

### 채움 가이드

- 모든 변경 단계마다 행 추가 (append-only)
- 영향받는 ID 컬럼: FR/NFR/US/SCR ID 다중 (콤마 구분)
- 사람 검수 통과 후에 1.0 발행 → 검수자 ID 명시

## §8 마인드맵 대조 결과 (cross-check — v0.3.0 신규, SDD §5-9)

> `ui-menu-mindmap.md`와의 양방향 정합 검증 결과. 단계 9d.5에서 1회 실행. **자동 보정 X** — marker만 남기고 명인 검토 후 반영. 별도 제3 문서를 만들지 않는다.

### cross-check 결과 메타

| 항목 | 값 |
|---|---|
| executed_at | `<ISO 8601>` |
| result | `<PASS | PASS_WITH_NOTES | FAIL | NOT_RUN>` |
| FR 매핑률 (방향 A) | `<0.00 ~ 1.00>` |
| leaf 매핑률 (방향 B) | `<0.00 ~ 1.00>` |
| unmapped-leaves candidate (방향 C) | `<0건 — 발행 게이트 PASS 필수>` |
| forbidden_actions 양쪽 표시 | `<yes | no | n/a — full-execute decision>` |
| input-manifest 슬롯 | `two_doc_cross_check` |
| 마인드맵 대응 섹션 | `ui-menu-mindmap.md` §6 |

### 방향 A — 기능정의서 → ui-menu-mindmap 대조 결과

각 FR이 마인드맵 §2 표의 노드 경로/SCR-ID에 연결되는지 확인. 미매핑 행은 marker 부착.

| FR-ID | 화면 ID | 마인드맵 노드 경로 | 매핑 상태 | 마커 |
|---|---|---|---|---|
| `FR-<PROJECT>-NNN` | `SCR-<PROJECT>-NNN` | `/main → ... → 화면 X` | mapped | — |
| `FR-<PROJECT>-MMM` | (없음) | (마인드맵 미등장) | unmapped | `[화면 위치 확인 필요]` |
| `FR-<PROJECT>-KKK` | `SCR-<PROJECT>-KKK` | `/main → ... → 화면 Y` | partial | `[상태 표시 누락]` `[권한 표시 누락]` `[승인 범위 밖 상태 변경 액션 표시 누락]` |

### 판정 룰

- **PASS**: 방향 A·B 모든 검증 매핑률 100% + forbidden_actions 양쪽 표시 (또는 full-execute decision으로 양쪽 표시 무관)
- **PASS_WITH_NOTES**: 매핑률 < 100%이지만 모든 미매핑 항목이 marker(`[화면 위치 확인 필요]` / `[상태 표시 누락]` / `[권한 표시 누락]` / `[승인 범위 밖 상태 변경 액션 표시 누락]`)로 빠짐없이 부착됨. 자동 보정 X, 명인 검토 후 결정
- **FAIL**: marker 부착 누락 또는 forbidden_actions 한쪽 누락 (`partial-execute`/`observe-only` decision일 때만)

(자세한 검증 룰·방향 B 결과는 ui-menu-mindmap.md §6 참조. 본 §8은 방향 A 결과만 기록 — 양쪽 분리 기록 원칙)
