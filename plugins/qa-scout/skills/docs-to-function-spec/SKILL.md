---
name: docs-to-function-spec
description: scout v0.2.9 에이전트가 단계 9c (정형화) 진입 시 호출하는 스킬. PRD + 받기 5종 자료를 흡수하여 최종 읽기 산출물 1/2인 `feature-spec.md` 단일 markdown(§0~§8 9섹션)을 작성한다. §1 17컬럼은 v0.2.8까지의 03_기능정의서 본체와 동일 양식 유지, §2 NFR·§3 US·§4 권한·§5 상태·§6 용어는 받기 5종 흡수 요약, §7 변경이력 append-only, §8 cross-check은 단계 9d.5에서 채움. 추정 금지·모호 시 즉시 질의·자료 부족 시 [자료 부족] 마커·출처 표기 강제(16번 인풋 출처).
---

# docs-to-function-spec (v0.2.9)

scout v0.2.9의 단계 9c (정형화 — 기능정의서) 진입 시 호출. 최종 읽기 산출물 1/2인 `feature-spec.md` 단일 markdown 작성 전용 (§0~§8 9섹션).

v0.2.8과의 차이: v0.2.8은 `feature-spec/` 폴더 5 markdown(01_표지·02_변경이력·03_기능정의서·04_비기능요구·05_사용자스토리) + 받기 5종(domain-knowledge/) 분산 출력 → 검수자가 5~6개 파일 동시 오픈 필요. v0.2.9는 단일 `feature-spec.md`로 통합 + 받기 5종 중 02/04/05를 본문 흡수 + 03-screen-layout은 `ui-menu-mindmap.md`로 분리. SDD `../../docs/qa-scout/spec.md` §5-1-1·§5-2 참조.

## 사용 시점
- scout v0.2.9 단계 9c에서 호출 (단계 9 분기 시작 직후, 단계 9d hash 기록 직전).
- 단계 9b(`docs-to-ui-menu-mindmap` 호출)와 병행 가능하나 cross-check(단계 9d.5)는 양쪽 산출물이 완성된 뒤 별도로 실행.
- 단계 1c execution gate 결정·단계 4a README discovery 결과가 `input-manifest.yaml`에 기록된 상태여야 frontmatter 동기 가능.

## 입력
- PRD (정형화 1차 인풋 — 단계 6에서 확정)
- domain-knowledge/02-state-transition.{ext} → §5 상태 전이 요약 흡수
- domain-knowledge/04-permission-matrix.{ext} → §4 권한 매트릭스 흡수
- domain-knowledge/05-glossary.{ext} → §6 용어집 흡수
- domain-knowledge/01-user-scenario.{ext} → §1 9번 컬럼·§3 사용자 스토리에 **인용만**, 본문 흡수 X
- domain-knowledge/03-screen-layout.{ext} → 본 스킬 범위 외 (`docs-to-ui-menu-mindmap` 처리)
- `input-manifest.yaml > execution_gate:` / `playwright_verification:` / `readme_discovery:` / `final_artifacts:` 슬롯 (frontmatter 동기용)
- (선택) NFR 정의서 / 사용자 스토리 정의서 / 도메인 용어집 별도 파일이 있으면 §2/§3/§6에 1차 흡수
- (선택) 기존 v0.2.7/v0.2.8 산출물 (마이그레이션 모드에서 §0~§7 흡수)

## 출력
- `feature-spec.md` 단일 markdown (qa-handoff/{project}/feature-spec.md). frontmatter + §0~§8 9섹션 작성.
- 변경 항목 entry는 `scout-log.md`에 append (timestamp + 행 수·섹션·자료 부족 마커 카운트).

본 스킬은 `feature-spec.md`만 작성한다. `ui-menu-mindmap.md`는 `docs-to-ui-menu-mindmap` 스킬이 작성한다 (SDD §7 단일 writer 원칙).

## 절차 (9단계)

### 1) 입력 흡수
- summaryDocuments MCP (또는 동등) 호출 → PRD 1차 요약·구조 추출
- 식별: 도메인 모듈/메뉴 경로, 사용자 롤, 기능 동사(생성·수정·조회·승인 등), 입출력 데이터 명세
- 긴 문서(>1,000줄) Read chunking (offset+limit)
- 다중 파일이면 Glob/Grep으로 동일 도메인 키워드 교차 검증
- `input-manifest.yaml > received_artifacts` 카테고리 매핑 확인: 02-state-transition · 04-permission-matrix · 05-glossary가 있는지

### 2) frontmatter 채움
templates/feature-spec.md의 frontmatter 슬롯을 다음 SoT에서 채운다.

| frontmatter 필드 | SoT |
|---|---|
| `project` / `domain` | `input-manifest.yaml > project` / 단계 4 도메인 입력 |
| `ai_author` | `scout v0.2.9 (<model>)` (Sonnet/Opus 모델명) |
| `created` / `last_updated` | ISO 8601 (오늘) |
| `linked_artifacts.ui_menu_mindmap` | `ui-menu-mindmap.md` 고정 |
| `linked_artifacts.input_manifest` / `scout_log` / `research_seed` / `source_dir` | manifest 경로 그대로 |
| `linked_artifacts.sheets_url` | `null` (단계 17a markdown-to-sheets 후 채움) |
| `sheets_mapping.primary_sheet` | `03_기능정의서` 고정 |
| `sheets_mapping.side_sheets` | `[01_표지, 02_변경이력, 04_비기능요구, 05_사용자스토리]` 고정 |
| `sheets_mapping.excluded_from_sheets` | `[§4_권한매트릭스, §5_상태전이, §6_용어집, §8_마인드맵대조결과]` 고정 (markdown 본문 SoT) |
| `execution_policy.decision` 등 5필드 | `input-manifest.yaml > execution_gate:` 슬롯에서 1:1 복사 (decision·reviewer_status·environment_class·forbidden_actions·`confirmed_at` → frontmatter `gate_decided_at`) |
| `related_specs` | SDD 경로 고정 |

`execution_policy:`는 단계 1c execution gate 게이트에서 확정된 값만 사용. enum 외 값 / 비어있는 상태 금지.

#### 2-1. execution_policy.decision ↔ reviewer_status 1:1 매핑 (SDD §5-10-2)

본 매핑은 frontmatter `execution_policy.decision`·`execution_policy.reviewer_status` 두 필드를 채울 때 강제 기준이다. enum 외 값 금지.

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

### 3) §0 표지 채움 (기존 01_표지 흡수)
14항목 표 + execution_gate 3행(decision / reviewer_status / environment_class). 모두 frontmatter `execution_policy:`와 동기.

채움 SoT:
- 프로젝트명·솔루션 종류·핵심 가치·대상 사용자·플랫폼·문서 버전·문서 상태·AI 작성자·최초 작성일·최종 수정일·관련 문서 → PRD + manifest
- 사람 검수자·배포 지역 → `[현업 확인 필요]` 마커 (검수자가 채움)

### 4) §1 17컬럼 본체 채움 (기존 03_기능정의서 본체 — 양식 유지)

#### 4-1. F-NNN 단위 분해
한 섹션 = 한 기능. F-NNN 번호 순차 부여.

**분해 기준** (우선순위):
1. 사용자 행위 단위 ("사용자가 X를 한다"의 X)
2. 자원 CRUD 단위 (Create/Read/Update/Delete 분리되면 별도 F)
3. 시스템 자동 동작 ("시스템이 Y 시 자동 Z" — 별도 F)

**피해야 할 분해**:
- 너무 잘게 (필드 1개 검증 = 별도 F) → UI 조각 수준은 통합
- 너무 큼지막하게 (메뉴 1개 = F 1개) → 기능 목적이 다르면 분리

**번호 부여**: FR-<PROJECT>-001 ~ NNN, 모듈 코드는 PROJECT 헤더 단일. 도메인 구분은 4번 컬럼 [중분류].

결번 허용 (삭제된 ID 재사용 금지 — GxP 추적 무결성). 0 패딩 3자리 (`001` ~ `999`).

#### 4-2. 17컬럼 채움 (각 F-NNN당)

| # | 컬럼 | 채움 가이드 |
|---|---|---|
| 1 | 기능 ID | `FR-<PROJECT>-NNN`, 결번 허용 |
| 2 | 화면 ID | `SCR-<PROJECT>-NNN`, 한 화면이 여러 FR에 등장 가능 (단계 9d.5 cross-check에서 마인드맵 §2와 매핑 강제) |
| 3 | 페이지 경로 / Depth | PRD 표기 그대로 (예: `Web > <상위 메뉴> > <하위 메뉴>`) |
| 4 | 중분류 | 도메인 영역 (예: `<중분류 코드>` — 프로젝트별 정의) |
| 5 | 기능명 | 명사형, 15~30자 |
| 6 | 기능 목적 (Why) | "···을 위해 ···한다" 한 줄 |
| 7 | 기능 요약 (1줄) | 행위·결과 요약 |
| 8 | 사전 조건 | 권한·상태·이전 단계 등 |
| 9 | 상세 정책 / 기능 설명 | PRD 본문 인용 + BR 코드 매핑. 01-user-scenario가 있으면 시나리오 줄거리도 본 컬럼 인용. |
| 10 | 입력 (Input) | 필드/타입/필수/검증 규칙 (자유 텍스트 또는 미니 표) |
| 11 | 처리 로직 (Process) | 1) 2) 3) 단계 |
| 12 | 상태 전이 | "X → Y" (예: `(none) → ACTIVE`). 02-state-transition이 있으면 본 컬럼·§5 양쪽 동기. |
| 13 | 출력 (Output) | 화면 갱신·이벤트·DB 변경 |
| 14 | 예외/에러 처리 | 케이스/메시지·동작/HTTP 코드/BR 코드 — 음성·예외 TC 도출 핵심 |
| 15 | TC ID | `TC-<PROJECT>-NNN` 다중 (RTM 매핑) — 후공정에서 채움 (공란 OK) |
| 16 | 인풋 출처 | 행 단위 GxP 추적 — `(PRD §x.x; USER_MANUAL §y.y; BR-XXX-NN; README §z.z [README 출처 — 본문 확인 필요])` |
| 17 | 비고 | FR↔NFR 연결 노트 등 자유 (예: `<정책명> → NFR-<PROJECT>-NNN 참조`). README에서 추출한 값이면 `[README 출처 — 본문 확인 필요]` 마커 필수. |

### 5) §2~§7 받기 5종 흡수 + 변경이력

#### 5-1. §2 비기능 요구 (기존 04_비기능요구 흡수 — 9컬럼)
| NFR-ID | 분류(성능/보안/가용성/접근성/...) | 요구사항 | 측정 기준 | 우선순위 | 출처 | 관련 FR | 비고 | 검수 상태 |

#### 5-2. §3 사용자 스토리 (기존 05_사용자스토리 흡수 — 9컬럼)
| US-ID | 사용자 역할 | 시나리오 | 행동 | 결과/가치 | 관련 FR | 관련 NFR | 출처 | 비고 |

01-user-scenario 자료가 있으면 본 §3에 줄거리 인용 (전체 복사 X). 원본 PNG/PDF는 `_source/`에 보존.

#### 5-3. §4 권한 매트릭스 (받기 04-permission-matrix 흡수)
| role × FR-ID × {visible, edit, delete, approve, ...} | 사유/비고 |

- role enum은 프로젝트별 정의 — placeholder만 사용 (프로젝트별 고유 명사 X)
- 액션 컬럼은 본 프로젝트 매트릭스에 맞춰 가감
- "✗" 셀이라도 사유 비고에 짧게 (예: `<상태 X>에서만 허용`)
- 원본이 PNG/이미지/PDF면 `_source/<file>` 인용 + 본 요약 표만 채움
- 본 §4는 Sheets 이행 X — markdown 본문 SoT (단계 17a 시 `excluded_from_sheets`)

#### 5-4. §5 상태 전이 요약 (받기 02-state-transition 흡수)
| 상태 | 허용 행위 | 발화 조건 | 다음 상태 | 관련 FR |

§1 12번 상태 전이 컬럼과 동기. Mermaid·PNG 원본은 `_source/`에 그대로.

#### 5-5. §6 용어집 (받기 05-glossary 흡수)
| 용어 | 정의 | 동의어 | 영문 표기 | 출처 |

abc 정렬. ubiquitous language 원본은 `_source/`에 보존.

#### 5-6. §7 변경 이력 (기존 02_변경이력 흡수 — append-only, template SoT 정합)
| 버전 | 변경일 | 변경자 | 변경 유형 | 변경 내용 | 영향받는 ID | 리뷰/승인자 |

`templates/feature-spec.md` §7(7컬럼)과 1:1 정합. 본 스킬 호출 시점에 0.1 초안 entry 1행 작성 — `버전=0.1`, `변경일=<YYYY-MM-DD>`, `변경자=scout v0.2.9 (<model>)`, `변경 유형=최초 작성`, `변경 내용=<project> 도메인 정형화 1차 초안: FR <N>건·NFR <N>건·US <N>건`, `영향받는 ID=FR-<PROJECT>-001~NNN, NFR-<PROJECT>-001~NNN, US-<PROJECT>-001~NNN`, `리뷰/승인자=[현업 확인 필요]`.

scout 작성·후공정 정정·검수자 의견 반영 모두 본 §7에 append. 기존 행 수정 X. 변경 유형 enum은 `templates/feature-spec.md` §7 변경 유형 섹션 SoT — `최초 작성 (Draft 0.1)` / `검수 후 수정` / `사람 검수 통과 (1.0 정식 발행)` / `고도화 (V2 신규 기능)` / `폐기 (Deprecated)` / `revert (롤백)` 6종. enum 외 사용 금지.

### 6) §8 마인드맵 대조 결과 placeholder

§8은 단계 9d.5 cross-check 게이트(SDD §5-9)에서 채운다. 본 스킬은 다음 골격만 미리 작성한다.

```markdown
## §8 마인드맵 대조 결과 (cross-check — 단계 9d.5에서 채움)

검증 결과 메타: `PASS | PASS_WITH_NOTES | FAIL | NOT_RUN` (단계 9d.5 진입 전 초기 상태는 `NOT_RUN`)

| FR-ID | 화면 ID | 마인드맵 노드 경로 | 매핑 상태 | 마커 |
|---|---|---|---|---|
| (단계 9d.5에서 채움) | | | | |
```

본 placeholder는 cross-check 미실행 상태에서도 §8 섹션 존재를 보장한다 (SDD §6 AC: §0~§8 9섹션 모두 존재).

### 7) 무망상 가드 (위반 시 환각 위험 큼)

#### 7-1. 추정 금지
- 자료에 명시 안 된 항목 X
- "보통 이런 시스템은..." 일반 지식 채움 X
- 비즈니스 정책 단정 X — 원본 인용만
- **README 출처 단정 금지** (SDD §5-11) — README에서 추출한 값은 §1 16번에 `README §x.x` 인용 + 17번에 `[README 출처 — 본문 확인 필요]` 마커

#### 7-2. 모호 시 즉시 중단
다음 신호 발견 시 작성 중단·사용자 질의 (5개 패턴):
- 같은 용어 2가지 의미
- 동일 기능 정의 충돌
- 행위자(누가) 불분명
- 입출력 필드 타입/범위 불명
- 단위 불명

질의 양식:
```
[질의] {파일명 §섹션}에서 "{용어/문장}"이 두 가지로 해석됩니다.
A) {해석 1}
B) {해석 2}
어느 쪽이 맞나요?
```

질의 결과 `scout-log.md`에 누적 (timestamp + Q + A).

#### 7-3. `[자료 부족]` 마커
양식 골격 보존, 빈 셀에 `[자료 부족]` 마커. 추정 채움 X. reviewer가 SKIP + 사유 명시할 수 있게.

#### 7-4. `[자료 부족]` 마커 self-check (v0.2.6+ 유지)
마커 부여 **전** 강제 grep 검증 — Opus 정독 1패스 누락 방지.

1. 마커 본문에서 키워드 자동 추출:
   - 권한 코드 (예: `<권한 코드>` — 프로젝트별 정의)
   - BR 코드 (예: `BR-<도메인>-NN` — PRD 명시 코드 그대로)
   - 정책 명사 (예: `시스템 기본 역할`, `재사용`, `자동 잠금`, `비밀번호 이력`)
2. **모든 인풋 자료에 Grep 자동 실행** (input-manifest.yaml `found_files` 전체):
   ```
   grep -rn "{keyword}" {input-manifest 자료 경로}
   ```
3. 결과 처리:
   - **hit 0건** → 마커 확정 (실제 자료 부족)
   - **hit ≥ 1건** → **마커 X**. 본문에 해당 자료 §섹션 인용 추가 (`<PRD 파일> §x.x; <보완 문서> §y.y` 형식)
4. self-check 결과를 `input-manifest.yaml > self_check_results` 섹션에 기록:
   - `candidates_total`·`confirmed`·`rejected` 카운트
   - `rejected_details`에 키워드·발견 위치·취해진 조치 명시

### 8) 출처 표기 (16번 컬럼 핵심 + §4~§6 출처)
모든 채움 항목 끝에 16번 컬럼에 출처:
```
<PRD 파일> §x.x; <보완 문서> §y.y; BR-<도메인>-NN
```

다중 출처 세미콜론 구분. 자료 부족:
```
[자료 부족] (해당 영역 — PRD에 명시 없음)
```

§4 권한 매트릭스·§5 상태 전이·§6 용어집도 각 행 끝에 출처 컬럼을 두고 동일 양식 적용 (받기 5종 원본 파일 + §섹션 또는 `_source/<file>`).

### 9) 자가 검증 체크리스트
- [ ] frontmatter 모든 필드 채움 (placeholder 잔존 X)
- [ ] `execution_policy:` 5필드가 manifest `execution_gate:` 값과 1:1 일치
- [ ] §0~§8 9섹션 모두 존재 (§8은 placeholder 골격이라도 존재)
- [ ] 모든 F-NNN에 컬럼 1~13 채움 또는 `[자료 부족]` 마커
- [ ] 14번 예외/에러 처리 채움 (음성 TC 도출 핵심)
- [ ] 15번 TC ID는 후공정에서 채움 — 공란 OK
- [ ] 16번 인풋 출처 누락 행 없음 (행 단위 GxP 추적)
- [ ] 17번 비고: NFR 연결 등 cross-reference 명시 + README 출처 시 마커 부착
- [ ] 사용자 질의 항목 `scout-log.md` 누적
- [ ] 영역 헤더 이모티콘 X (Sheets 그룹 헤더 mergeCells 적용 X)
- [ ] **[자료 부족] 마커 self-check 통과 (v0.2.6+)**: 모든 마커가 §단계 7-4 grep 검증 거침. `self_check_results.candidates_total == confirmed + rejected`
- [ ] §4 권한 매트릭스의 role enum은 프로젝트별 정의 (프로젝트별 고유 명사 X — placeholder만)
- [ ] §5 상태 전이가 §1 12번 컬럼과 동기 (불일치 시 §7 변경이력 entry)
- [ ] §7 변경 이력에 본 스킬 호출 entry append (timestamp + 작성자 + 변경 개요)
- [ ] §8 cross-check 결과 메타 enum이 4종 중 하나 (`PASS | PASS_WITH_NOTES | FAIL | NOT_RUN`) — 초기 작성 시 `NOT_RUN`

## 한계
- 본 스킬은 `feature-spec.md` 단일 markdown 작성 전용. `ui-menu-mindmap.md`는 `docs-to-ui-menu-mindmap` 스킬이 작성 (SDD §7 단일 writer 원칙).
- §8 cross-check 결과는 본 스킬에서 채우지 않음 — 단계 9d.5 cross-check 게이트가 채움.
- 받기 5종 중 03-screen-layout은 본 스킬 범위 외 (마인드맵 스킬 처리).
- Sheets 이행은 본 스킬 범위 외 — 단계 17a `markdown-to-sheets` 스킬이 처리.
- 마이그레이션 (v0.2.7/v0.2.8 → v0.2.9)은 본 스킬 범위 외 — `scripts/migrate-to-v029.mjs`가 처리.

## 참조
- spec: `../../docs/qa-scout/spec.md` §5-1-1 · §5-2 · §5-8 단계 9c · §5-9 cross-check
- 이전 spec: `../../docs/qa-scout/spec.md` · `../../docs/qa-scout/spec.md` · `../../docs/qa-scout/spec.md`
- scout 에이전트: `agents/scout.md` 단계 9c
- 선행 스킬: `skills/curate-input/SKILL.md` (단계 5)
- 병행 스킬: `skills/docs-to-ui-menu-mindmap/SKILL.md` (단계 9b)
- 후공정 스킬: `skills/markdown-to-sheets/SKILL.md` (단계 17a)
- 양식 골격: `templates/feature-spec.md`
- manifest 슬롯: `templates/input-manifest.yaml > execution_gate:` / `playwright_verification:` / `readme_discovery:` / `final_artifacts:` / `two_doc_cross_check:`

## 변경 이력 (스킬 자체)

| 버전 | 일자 | 변경 |
|---|---|---|
| 0.1 | 2026-04-30 | 초기 작성 (markdown function-spec.md 자유 양식, 35컬럼 base) |
| 0.2 | 2026-05-06 | 17컬럼 표준 양식 적응 (영역 헤더 폐지·이모티콘 제거·TC ID·인풋 출처·비고 추가). spec: ../../docs/qa-scout/spec.md |
| 0.2.6 | 2026-05-07 | [자료 부족] 마커 self-check (단계 4-4 grep 자동 검증) 추가. dogfood 프로젝트 산출물 검증 9건 회피 경험 반영. |
| 0.2.9 | 2026-05-21 | 5 md → 1 md 압축 (feature-spec.md 단일 산출물). §0~§8 9섹션 작성 + frontmatter execution_policy 동기 + 받기 5종 중 02/04/05 본문 흡수 + 03-screen-layout 분리(마인드맵 스킬) + §8 cross-check placeholder + README 출처 마커. spec: ../../docs/qa-scout/spec.md |
