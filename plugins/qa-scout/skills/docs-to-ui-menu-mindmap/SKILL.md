---
name: docs-to-ui-menu-mindmap
description: scout v0.2.9 에이전트가 단계 9b (정형화 — 마인드맵) 진입 시 호출하는 신규 스킬. 화면 전개도(받기 03-screen-layout) + ui-crawl-manifest + input-manifest의 deep_screen_targets[]·developer_deep_scope를 흡수하여 최종 읽기 산출물 2/2인 `ui-menu-mindmap.md` 단일 markdown(§0~§6 7섹션)을 작성한다. Mermaid mindmap은 시각 보조, §2 노드 상세 표가 SoT. 노드 enum 14종 고정·깊이 최대 6단계·★·★상세·⚠ 마커·README 출처 단정 금지·자동 보정 X.
---

# docs-to-ui-menu-mindmap (v0.1.0 — v0.2.9 신규)

scout v0.2.9의 단계 9b (정형화 — 마인드맵) 진입 시 호출. 최종 읽기 산출물 2/2인 `ui-menu-mindmap.md` 단일 markdown 작성 전용 (§0~§6 7섹션).

v0.2.9 신규 스킬. v0.2.8까지는 받기 5종 중 `domain-knowledge/03-screen-layout.{ext}`이 화면 전개도 SoT였으나, 검수자가 화면 위치·연결을 한눈에 보기 어려웠다. v0.2.9는 본 스킬로 마인드맵 markdown을 자동 도출하고 `feature-spec.md` §1 화면 ID와 cross-check(단계 9d.5)로 양방향 정합 검증한다. SDD `../../docs/qa-scout/spec.md` §5-1-2 · §5-3 · §5-6 · §5-9 참조.

## 사용 시점
- scout v0.2.9 단계 9b에서 호출 (단계 9 정형화 분기 시작 직후, 단계 9c `docs-to-function-spec`와 병행 가능).
- 단계 1c execution gate 결정·단계 1b deep-scope 답변·단계 4a README discovery 결과가 `input-manifest.yaml`에 기록된 상태여야 frontmatter·★·⚠ 마커 결정 가능.
- 단계 9d.5 cross-check는 본 스킬과 `docs-to-function-spec` 산출물이 모두 완성된 뒤 별도로 실행 (§6 채움).

## 입력
- `domain-knowledge/03-screen-layout.{ext}` (화면 전개도 — 1차 인풋, 단계 6 큐레이션에서 확정)
- `knowledge/{project}/shared/pages/ui-crawl-manifest.yaml` (단계 12b crawl 증거 — observed/partially-observed/missing 분류)
- `knowledge/{project}/shared/pages/*.yaml` (개별 화면 capture)
- `input-manifest.yaml` 슬롯:
  - `downstream_enrichment.developer_deep_scope.questions_round[0].answers.must_open_targets[]` → ★ 마커
  - `downstream_enrichment.developer_deep_scope.questions_round[0].answers.deep_screens[]` → ★ 마커 + §2 deep_target=yes
  - `downstream_enrichment.developer_deep_scope.questions_round[0].answers.risky_actions[]` → ⚠ 마커 후보
  - `downstream_enrichment.developer_deep_scope.confirmation_rounds[N].confirmed[]` → §4 매핑 표 + ★상세
  - `downstream_enrichment.developer_deep_scope.confirmation_rounds[N].additional.deep_screens[]` → 신규 노드 추가 + ★상세
  - `downstream_enrichment.developer_deep_scope.confirmation_rounds[N].additional.risky_actions[]` → ⚠ 마커
  - `downstream_enrichment.developer_deep_scope.rejected_deep_scope_candidates[]` → §5 통계 카운트 (노드 추가 X)
  - `downstream_enrichment.deep_screen_targets[]` → §2 deep_target 컬럼 + §4 매핑 표 1:1
  - `execution_gate:` → frontmatter `execution_policy:` 동기 + ⚠ 마커 활성 여부 결정
  - `readme_discovery:` → README 출처 노드 마커
- `feature-spec.md` §1 17컬럼 (SCR-ID·FR-ID 매핑 참조 — cross-check 준비)
- (선택) 화면 와이어프레임 PNG/PDF (원본은 `_source/` 보존)

## 출력
- `ui-menu-mindmap.md` 단일 markdown (qa-handoff/{project}/ui-menu-mindmap.md). frontmatter + §0~§6 7섹션 작성.
- 변경 항목 entry는 `scout-log.md`에 append (timestamp + 노드 수·deep_target 수·★/⚠ 카운트·gap 분포).

본 스킬은 `ui-menu-mindmap.md`만 작성한다. `feature-spec.md`는 `docs-to-function-spec` 스킬이 작성한다 (SDD §7 단일 writer 원칙).

## 절차 (8단계)

### 1) 입력 흡수
- `domain-knowledge/03-screen-layout.{ext}` 우선 정독 — 메뉴 트리·화면 라우트·tab/modal 구조 추출
- `ui-crawl-manifest.yaml` 읽기 — observed/partially-observed/missing 분류, 화면별 capture yaml 경로 식별
- `input-manifest.yaml > downstream_enrichment` 전체 흡수 (deep_screen_targets[]·developer_deep_scope·confirmation_rounds[])
- 다중 파일이면 Glob/Grep으로 동일 화면 키워드 교차 검증
- `feature-spec.md` §1 17컬럼 SCR-ID 인덱스 추출 (cross-check 준비)

### 2) frontmatter 채움
templates/ui-menu-mindmap.md의 frontmatter 슬롯을 다음 SoT에서 채운다.

| frontmatter 필드 | SoT |
|---|---|
| `project` | `input-manifest.yaml > project` |
| `crawler` | `playwright-mcp | chrome-mcp | python-playwright | manual | doc-only` (단계 12b 실제 사용 도구) |
| `crawl_evidence` | `knowledge/{project}/shared/pages/ui-crawl-manifest.yaml` 고정 |
| `linked_feature_spec` | `feature-spec.md` 고정 |
| `execution_policy.decision` 등 5필드 | `input-manifest.yaml > execution_gate:` 1:1 복사 (`feature-spec.md`와 동일 값. `decision`·`reviewer_status`·`environment_class`·`forbidden_actions`·manifest `confirmed_at` → frontmatter `gate_decided_at`) |
| `last_updated` | ISO 8601 (오늘) |
| `related_specs` | SDD 경로 고정 |

`execution_policy:`는 `feature-spec.md`와 정확히 동일 값. 단계 1c에서 확정된 값만 사용.

#### 2-1. execution_policy.decision ↔ reviewer_status 1:1 매핑 (SDD §5-10-2)

본 매핑은 frontmatter `execution_policy.decision`·`execution_policy.reviewer_status` 두 필드를 채울 때 강제 기준이다. `feature-spec.md`와 동일 — enum 외 값 금지.

| execution_gate.decision | reviewer_status | 의미 |
|---|---|---|
| `full-execute` | `EXECUTED-TEST-ENV` | 개발/QA/테스트 환경이며 금지 액션이 없어 승인 범위 안에서 상태 변경 액션까지 실행 가능 |
| `partial-execute` | `PARTIAL-OBSERVED` | 일부 상태 변경 액션은 금지되어 허용된 범위만 실행하고 나머지는 관찰/기록 |
| `observe-only` | `NOT-TESTED-PROD-RISK` | 운영/운영성 데이터/금지 액션 위험 때문에 상태 변경 액션은 실행하지 않고 관찰만 수행 |
| `context-insufficient` | `CONTEXT-INSUFFICIENT` | 환경·접근 조건·금지 액션 정보가 부족해 실행 판단 불가 |

frontmatter `gate_decided_at`은 manifest `execution_gate.confirmed_at`과 의미 동일 (Step 1 templates 호환 layer — SDD §9 v4 entry).

**중단 룰**: 다음 위반 1건이라도 발견 시 본 스킬 작성 중단 + scout-log.md에 사유 기록, 자동 보정 X (`feedback_bridge_wrapping_pattern`).
- decision↔reviewer_status 4쌍 외 조합 (예: `full-execute` + `NOT-TESTED-PROD-RISK`)
- `execution_gate:` 슬롯의 11개 필드 중 누락
- enum 외 값 (`unknown` decision 등)
- manifest `execution_gate:`와 frontmatter `execution_policy:` 5필드 불일치
- `feature-spec.md` frontmatter `execution_policy:`와 `ui-menu-mindmap.md` frontmatter `execution_policy:` 5필드 불일치 (단계 9b·9c가 동일 manifest를 참조했는지 검증)

### 3) §0 범례 + decision↔reviewer_status 1:1 매핑
템플릿 골격 그대로 유지. ★·★상세·⚠·[자료부족]·[README 출처] 5종 마커 정의는 SDD §5-10·§5-11과 동기. §0 범례 본문의 decision↔reviewer_status 매핑표는 위 §2-1과 동일 값.

### 4) §1 트리 시각화 (Mermaid mindmap) 작성

#### 4-1. 깊이·노드 종류 enum (14종 고정 — SDD §5-3)
다음 14종 외 사용 금지:
`root` · `menu-l1` (대메뉴) · `menu-l2` (중메뉴) · `menu-l3` (소메뉴 — 옵션) · `screen` (라우트 단위) · `tab` · `panel` · `modal` · `table` · `row-action` · `form` · `button` · `field` · `link`

#### 4-2. 깊이 6단계 고정 (SDD §5-3-1)
1. `root` (메인 화면)
2. `menu-l1` (대메뉴)
3. `menu-l2` (중메뉴)
4. `screen` (라우트 단위)
5. `tab` / `panel` / `modal` / `table` (화면 내 1차 구조)
6. leaf — `row-action` / `button` / `field` / `link` / `form`

- 노드 종류는 위 enum 14종 외 사용 금지 (SDD §5-3 enum 정합). 동적 영역 변화·state lifecycle·변수 marker insert/delete/serialize 등은 **노드 종류가 아니다** — 마인드맵에 그리지 않고 §2 표 비고 또는 deep_screen_targets[] 인용으로만 기록한다.
- `menu-l3` 옵션 사용 시 leaf(`row-action`/`button`/`field`/`link`/`form`)와 상태는 Mermaid 트리에 그리지 않고 §2 표에만 기록 (6단계 한도 보호)
- 깊이 초과(변수 marker insert/delete/serialize, state lifecycle, 동적 영역 변화 등)는 Mermaid에 그리지 않고 §2 표 비고·deep_screen_targets[] 인용으로만 표현

#### 4-3. Mermaid syntax 안전성
- 노드 텍스트에 `(`, `)`, `[`, `]`, `:`, `;` 등 Mermaid syntax 특수문자 사용 금지
- escape 필요 시 §2 표에서 별도 표기 (마인드맵 노드는 단순 이름만)
- `screen` 노드는 SCR-{PROJECT}-NNN ID를 노드 텍스트 옆에 인용 (예: `화면 X SCR-PROJECT-001`)
- `tab/panel/modal/table/form/row-action/button/field/link` 노드는 ID 부여 안 함 (인스턴스 수 폭증 방지)

#### 4-4. 마커 부착
- developer_deep_scope.must_open_targets[]에 등장 → ★
- deep_screen_targets[]에 등장 → ★상세 + §2 deep_target=yes
- execution_gate.forbidden_actions[]에 등장 + decision이 `partial-execute`/`observe-only` → ⚠ (`full-execute` decision일 때 부착 X — SDD §5-10-4)
- README discovery에서 1차 발견된 경로 → `[README 출처 — 본문 확인 필요]` 마커

### 5) §2 노드 상세 표 (SoT) 작성

§1 트리의 모든 노드에 대해 1행씩 작성. 본 표가 마인드맵 메타의 SoT — Mermaid는 시각 보조.

11컬럼 양식 (SDD §5-1-2):

| 컬럼 | 채움 가이드 |
|---|---|
| 경로 | `/main → 대메뉴 → 중메뉴 → 화면 → tab` 형식 (sluggify X — 사람이 읽기) |
| 노드 종류 | enum 14종 중 하나 |
| 부모 경로 | 한 단계 위 경로 (root는 `(root)`) |
| SCR-ID | `screen` 노드만 채움 (`SCR-<PROJECT>-NNN`), 나머지 `—` |
| deep_target | `yes (id=<deep_screen_targets[].id>)` 또는 `—` |
| 마커 | ★ / ★상세 / [자료부족] / [상세 화면 구조 부족] / [변수 동작 자료 부족] / [상태별 UI 확인 필요] / [권한별 UI 확인 필요] / [문서-화면 충돌] / [README 출처 — 본문 확인 필요] |
| risky | ⚠ 또는 `—` |
| role 노출 | role enum (프로젝트별) 또는 `all-roles` / `unknown` / `[권한별 UI 확인 필요]` |
| gap | gap_marker enum 7종 (structure-depth-gap · behavior-depth-gap · variable-behavior-gap · state-visibility-gap · role-visibility-gap · risky-action-gap · doc-screen-conflict) 또는 `—` |
| FR-ID 인용 | `feature-spec.md` §1의 FR-{PROJECT}-NNN 인용 (leaf 노드는 ≥1건 필수 — 단계 9d.5 cross-check 검증) |
| evidence | 인용 출처 (`capture:<file>.yaml` / `UC §x.x` / `<README 출처>` / `[화면 확인 필요]`) |

#### 5-1. 자동 도출 vs 수동 보강
- §1 트리·§2 표 초안은 본 스킬이 자동 도출 (input-manifest + ui-crawl-manifest + 03-screen-layout 인용)
- 자동 도출 노드는 §2 표 `evidence` 컬럼에 출처 인용 필수
- 수동 보강 (단계 1b·12b에서 개발자가 추가한 must_open_targets[] / deep_screen_targets[])은 자동 도출 노드에 ★·★상세 부착
- crawl 결과가 없는 노드는 `evidence`에 `[화면 확인 필요]` 또는 `[자료부족]` 마커

### 6) §3 노드 종류 enum
14종 enum 그대로 본문에 명시 (검수자 참조용). 새 종류 발견 시 본 스킬 변경이 아니라 SDD 갱신 후 enum 확장.

### 7) §4 deep_screen_targets[] 매핑 + §5 도출 근거

#### 7-1. §4 매핑 표 (SDD §5-3-3)
input-manifest `downstream_enrichment.deep_screen_targets[]`의 각 row → 1행:

| target id | 경로 노드 | gap_candidates | reason | risky_actions_not_clicked | required_observations |
|---|---|---|---|---|---|

- `target id` ↔ §2 표의 `deep_target` 컬럼 `id=<...>` 값과 일치 강제
- `required_observations`의 tabs/modals/panels/row_actions은 §1 트리·§2 표에 노드로 반드시 표현 (단계 9d.5 cross-check 방향 B 검증 3 트리거)

#### 7-2. §5 도출 근거 통계
- pre_crawl (단계 1b): must_open_targets[] N건 → ★ 마커
- post_crawl (단계 12b): confirmed N건 + additional N건 → ★상세
- crawl 결과: observed N / partially-observed N / missing N
- risky_actions: ⚠ 마커 N건
- gap 분포: 7종 × 카운트
- rejected_deep_scope_candidates[]: 카운트만 표시 (마인드맵 노드 추가 X)

### 8) §6 기능정의서 대조 결과 placeholder

§6은 단계 9d.5 cross-check 게이트(SDD §5-9)에서 채운다. 본 스킬은 다음 골격만 미리 작성한다.

```markdown
## §6 기능정의서 대조 결과 (cross-check — 단계 9d.5에서 채움)

검증 결과 메타: `PASS | PASS_WITH_NOTES | FAIL | NOT_RUN` (단계 9d.5 진입 전 초기 상태는 `NOT_RUN`)

| 노드 경로 | 노드 종류 | FR-ID 인용 | 매핑 상태 | 마커 |
|---|---|---|---|---|
| (단계 9d.5에서 채움) | | | | |
```

본 placeholder는 cross-check 미실행 상태에서도 §6 섹션 존재를 보장한다 (SDD §6 AC: §0~§6 7섹션 모두 존재).

## 무망상 가드 (위반 시 환각 위험 큼)

### 추정 금지
- 03-screen-layout에 없는 화면 추측 추가 X
- crawl 결과 없는 노드 임의 부여 X — `evidence`에 `[화면 확인 필요]` 마커
- README에서 발견한 노드는 `[README 출처 — 본문 확인 필요]` 마커 부착, 단정 X (SDD §5-11-5)
- gap_marker는 enum 7종 외 사용 금지 (구조·동작·변수·상태·권한·위험·충돌)

### 모호 시 즉시 중단
다음 신호 발견 시 작성 중단·사용자 질의 (4개 패턴):
- 화면 라우트 충돌 (동일 경로 2개 화면 정의)
- 메뉴 트리 1차 분류 vs 화면 라우트 불일치
- crawl 결과 vs 03-screen-layout 충돌 → gap `doc-screen-conflict` 마커
- deep_screen_targets[].required_observations에 없는 tab/modal 명시 → 정의 부재

질의 양식은 `docs-to-function-spec` 스킬과 동일.

### `[자료부족]` 마커 + grep self-check (v0.2.6+ 패턴 유지)
마커 부여 전 input-manifest `found_files` 전체에 강제 grep — Opus 정독 1패스 누락 방지. 결과를 `input-manifest.yaml > self_check_results` 섹션에 카운트 기록.

### 자동 보정 금지 (Auto-Healing Loop 차단)
crawl 결과와 03-screen-layout 충돌 시, 한쪽을 자동 채택하지 않는다. 양쪽 인용 + gap `doc-screen-conflict` 마커 + §2 표 비고에 충돌 사유 명시 + 단계 9f 사용자 인터뷰로 결정 위임 (memory `feedback_bridge_wrapping_pattern` 패턴 적용).

## 자가 검증 체크리스트

- [ ] frontmatter 모든 필드 채움 (placeholder 잔존 X)
- [ ] `execution_policy:` 5필드가 `feature-spec.md` frontmatter와 1:1 일치 (manifest `execution_gate:` SoT)
- [ ] §0~§6 7섹션 모두 존재 (§6은 placeholder 골격이라도 존재)
- [ ] §1 Mermaid mindmap 깊이 ≤ 6단계 (`menu-l3` 옵션 사용 시도 leaf·state는 §2 표로 빠짐)
- [ ] Mermaid 노드 텍스트에 특수문자 (`(`, `)`, `[`, `]`, `:`, `;`) 사용 0건
- [ ] §2 표의 모든 행이 11컬럼 채움 또는 `—`/마커 부착
- [ ] §2 표의 노드 종류가 enum 14종 중 하나 (외 사용 0건)
- [ ] §2 표의 모든 leaf 노드(`button`/`row-action`/`field`/`form`/`table`/`modal`)에 FR-ID ≥1건 인용 또는 `SPEC-MISSING`/`[문서 근거 부족]` 마커
- [ ] §2 표 `deep_target=yes` 행이 §4 매핑 표와 1:1 일치
- [ ] §4 매핑 표가 `input-manifest.yaml > downstream_enrichment.deep_screen_targets[]` 모든 row 흡수
- [ ] ★ 마커가 `must_open_targets[]` + `confirmation_rounds[].confirmed[]` 합집합과 일치
- [ ] ⚠ 마커가 `execution_gate.forbidden_actions[]`와 일치 (decision `full-execute`일 때만 0건 허용)
- [ ] gap_marker enum 7종 외 사용 0건
- [ ] §5 도출 근거 통계가 input-manifest 슬롯 카운트와 일치
- [ ] §6 cross-check 결과 메타 enum이 4종 중 하나 (`PASS | PASS_WITH_NOTES | FAIL | NOT_RUN`) — 초기 작성 시 `NOT_RUN`
- [ ] README 출처 노드는 모두 `[README 출처 — 본문 확인 필요]` 마커 부착
- [ ] 자동 도출 노드 evidence 누락 0건 (`capture:<file>.yaml` / `UC §x.x` 등)
- [ ] **[자료 부족] 마커 self-check 통과**: 모든 마커가 grep 검증 거침. `self_check_results.candidates_total == confirmed + rejected`
- [ ] scout-log.md에 본 스킬 호출 entry append (timestamp + 노드 수·★/⚠ 카운트·gap 분포)

## 한계
- 본 스킬은 `ui-menu-mindmap.md` 단일 markdown 작성 전용. `feature-spec.md`는 `docs-to-function-spec` 스킬이 작성 (SDD §7 단일 writer 원칙).
- §6 cross-check 결과는 본 스킬에서 채우지 않음 — 단계 9d.5 cross-check 게이트가 채움.
- Sheets 이행 X — 마인드맵은 markdown 보조 산출물로 유지 (SDD §5-5). markdown-to-sheets 스킬 범위 외.
- 마이그레이션 (v0.2.7/v0.2.8 → v0.2.9)은 본 스킬 범위 외 — `scripts/migrate-to-v029.mjs`가 처리.
- crawl 결과 부재 시 fallback X — observed 화면만 자동 도출, 나머지는 `[화면 확인 필요]` 마커로 남김.

## 참조
- spec: `../../docs/qa-scout/spec.md` §5-1-2 · §5-3 · §5-6 · §5-9 cross-check · §5-10 execution gate · §5-11 README discovery
- 이전 spec: `../../docs/qa-scout/spec.md` (deep_screen_targets[]·developer_deep_scope 정책 — 본 스킬에서 변경 없음)
- scout 에이전트: `agents/scout.md` 단계 9b
- 선행 스킬: `skills/curate-input/SKILL.md` (단계 5)
- 병행 스킬: `skills/docs-to-function-spec/SKILL.md` (단계 9c)
- 양식 골격: `templates/ui-menu-mindmap.md`
- crawl 산출물: `knowledge/{project}/shared/pages/ui-crawl-manifest.yaml` + capture yaml
- manifest 슬롯: `templates/input-manifest.yaml > downstream_enrichment` / `execution_gate:` / `readme_discovery:` / `two_doc_cross_check:`

## 변경 이력 (스킬 자체)

| 버전 | 일자 | 변경 |
|---|---|---|
| 0.1.0 | 2026-05-21 | 신규 작성. v0.2.9에서 받기 5종 중 03-screen-layout을 ui-menu-mindmap.md로 분리. Mermaid mindmap §1 시각 + §2 노드 상세 표(SoT) + §3 enum 14종 + §4 deep_screen_targets[] 매핑 + §5 도출 근거 + §6 cross-check placeholder. spec: ../../docs/qa-scout/spec.md |
