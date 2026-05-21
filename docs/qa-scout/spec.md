# qa-scout v0.2 산출물 골격 스펙 정의서

- **ID**: SPEC-2026-05-06-qa-scout-v0.2-skeleton
- **작성일**: 2026-05-06
- **작성자**: QA 파트너 (사용자 티키타카 검토 후 ExitPlanMode 승인)
- **상태**: approved (2026-05-06, 4차 검수 + 17갭 정정 완료, 사용자 승인)
- **최신 적용 버전 (footer 갱신)**: v0.2.9 (2026-05-21) — 최종 산출 문서 2종 압축(`feature-spec.md` + `ui-menu-mindmap.md`) + 단계 1c execution gate (decision 4종 × reviewer_status 4종 1:1 매핑) + 단계 4a README discovery gate + 단계 9 5단계 분기(9a/9b/9c/9d/9d.5 cross-check) + 단계 17a Sheets 옵션 A/B/C 분기 + 핵심 규약 7번 표현 변경("승인 범위 밖 상태 변경 액션 금지") + 신규 스킬 `docs-to-ui-menu-mindmap` + 신규 마이그레이션 유틸 `scripts/migrate-to-v029.mjs` + input-manifest schema_version 0.2.9 + 신규 슬롯 4종. 본 spec의 §5 절차는 v0.2.6 골격을 보존하며, v0.2.7~v0.2.9 보강은 CHANGELOG와 `plugins/qa-scout/agents/scout.md` 본문에 반영됨.
- **연계 산출물 위치**:
  - `plugins/qa-scout/agents/scout.md` (갱신)
  - `plugins/qa-scout/skills/curate-input/SKILL.md` (신규 — 자료 큐레이션·최신성 확인)
  - `plugins/qa-scout/skills/docs-to-function-spec/SKILL.md` (갱신 — 17컬럼·5시트 반영 (정정 1차 G1·G2·G3 후 14→17))
  - `plugins/qa-scout/templates/feature-spec/` (신규 디렉토리 — 5시트 양식 골격)
  - `plugins/qa-scout/templates/handoff-meta.yaml` (신규 — 받기 5종 표지·변경이력 메타)
  - `plugins/qa-scout/README.md` (갱신 — v0.2 사용법)

---

## 1. 목적 (Why)

MYAPP Stage 2 진입을 앞두고 qa-scout 산출물 골격을 사용자 의도("산출물 = TC·자동화 스크립트를 뽑을 수 있는 도메인 지식")에 맞게 재정의한다. 2026-05-06 회의(내부 리뷰어·시니어 개발자·도메인 개발자·사용자) 인사이트를 참조하되 결정은 사용자 티키타카 사이클로 확정.

해결하려는 문제:
1. 현 6종(glossary·function-spec·e2e-flow·layout·permission·state-transition) 모두를 GxP 양식으로 정형화하는 가정이 무거움. 후공정(tc-writer 등)이 실제 직접 입력으로 쓰는 건 정제 자산이고 6종은 중간 단계.
2. MYAPP 6월 구축 일정에서 GxP 산출물 요건 만족이 필요한 건 사실상 **기능 정의서 1종**. 나머지는 도메인 지식으로 활용 가능.
3. 개발자 자료 산재(GitHub) + 다중 버전 혼재 → 잘못된 버전 인풋으로 GxP 위반 위험. 자료 최신성 확인이 진짜 핵심.

본 스펙의 목표:
1. **개발자 도메인 지식 5종 그대로 인계** + **PRD를 GxP 양식 기능 정의서로 정형화**하는 단순 구조
2. MYAPP Sheets 양식 차용 + 사용자 정정 반영(17컬럼·이모티콘 제거·NFR 시트 분리·TC ID 추가)
3. 자료 큐레이션·최신성 확인 절차로 GxP 데이터 무결성 확보

## 2. 범위 (Scope)

### 2-1. 포함 (In Scope)
- scout-kit 산출물 6종 정의 (정형화 1 + 받기 5)
- 기능 정의서 5시트 양식 (01_표지·04_변경이력·06_기능정의서·07_비기능요구·08_사용자스토리) — **Google Sheets 산출** (사용자 정정 5차)
- 06 시트 17컬럼 (Sheets 22컬럼에서 운영 메타 3 + 다른 시트 흡수 3 제거 + TC ID·인풋 출처·비고 신규/부활)
- 받기 5종 메타 처리 (frontmatter / .meta.yaml)
- 자료 큐레이션·최신성 확인 절차 V1 (8단계)
- 워크플로 시나리오 V2 (단계 -1 ~ 20 — QA↔개발자 양방향 인계 포함)
- ID 체계 1차안 (FR·SCR·NFR·US·TC MYAPP-NNN)
- 검수 게이트 (자동 + 사람 슬롯)
- MYAPP USER_PERMISSION 마이그레이션 노트 (legacy 보존 정책)

### 2-2. 제외 (Out of Scope)
- 5시트 양식 파일 실제 작성 (별도 후속 작업 — 본 spec 승인 후)
- 신규 스킬(`curate-input`·`markdown-to-sheets`) 구현 (별도)
- `docs-to-function-spec` 스킬 17컬럼 적응 (별도)
- exporter (md → docx/xlsx) — 본 spec은 source-of-truth 양식 정의만
- URS 양식 — 6월 고객 협의 후 별도 트랙
- 품질 보증 방안 문서 — 회의 deliverable 후보, 도메인 지식 차원과 분리, 보류
- ID owner 협의 — 본 spec 1차안 후 실행 단계
- 단계 0 사전 안내 자료 — 별도 후속 작업
- 단계 2 트리거 키워드 정확 매칭 패턴 (`scout 호출` 텍스트 vs `/scout` 슬래시 등 정확한 텍스트 매칭 명세) — 단, **PROJECT 헤더 포함 원칙은 본 spec에서 확정**

## 3. 입력 (Inputs)

### 3-1. 개발자 측 인풋 자료

| # | 자료 | 용도 | 필수 |
|---|---|---|---|
| 1 | PRD (요구사항 정의서) | 기능 정의서 정형화 인풋 | 필수 |
| 2 | 도메인 용어집 (Ubiquitous Language) | 받기 산출물 #5 (그대로 인계) | 필수 |
| 3 | 유스케이스 다이어그램 | 받기 산출물 #1 (사용자 시나리오) 인풋 | 필수 |
| 4 | 시퀀스 다이어그램 | 받기 산출물 #2 (상태 전이도) 인풋 | 필수 |
| 5 | Process Flow | 사용자 시나리오 보강 인풋 | 권장 |
| 6 | 와이어프레임 / 화면 구조 | 받기 산출물 #3 (화면 전개도) 인풋 | 옵션 (부재 시 라이브 탐색) |
| 7 | 권한 자료 (PRD 권한 섹션 등) | 받기 산출물 #4 (권한 매트릭스) 인풋 | 필수 |
| 8 | ERD / 아키텍처 | 자동화·테스트 데이터 매핑 참조 (산출물 X) | 권장 |
| 9 | 라이브 환경 URL + 계정 | 화면 전개도 부재 시 보강 | 옵션 |

### 3-2. 시스템 측 인풋

| 항목 | 출처 |
|---|---|
| PROJECT 헤더 (`[PROJECT: <프로젝트명>]`) | 개발자 트리거 텍스트 (단계 2) — qa-handoff/{프로젝트명}/ 폴더 결정 |
| 개발자 자료 폴더 경로 | 개발자 입력 (단계 4). 절대 경로 (예: `D:/work/myapp-dev/docs`) 또는 작업 폴더 기준 상대 경로 (예: `./docs`). 다중 폴더 가능 (콤마 또는 줄바꿈 구분). scout-kit이 폴더 존재·읽기 권한 검증 후 진행 (검증 실패 시 재입력 요청). |
| 자료 메타 (mtime, git 마지막 commit) | 파일 시스템·git log |

## 4. 산출물 (Outputs / Deliverables)

### 4-1. 산출물 카테고리

```
[정형화 1종 — Google Sheets 산출 (사용자 정정 5차)]
■ 기능 정의서 (Google Sheets 5시트)
   ├── 01_표지         (메타)
   ├── 04_변경이력     (V1→V2 누적)
   ├── 06_기능정의서   (17컬럼 본문)
   ├── 07_비기능요구   (9컬럼 본문)
   └── 08_사용자스토리 (9컬럼 본문)
   * scout-kit이 Google Sheets MCP로 신규 시트 생성 + URL을 feature-spec.yaml에 기록
   * 받기 5종은 개발자 본인이 원본 관리 — scout-kit은 사본·메타만 인계

[받기 5종 — 도메인 지식]
■ 사용자 시나리오   (← 유스케이스 + Process Flow, 본문 그대로 인계)
■ 상태 전이도       (← 시퀀스 다이어그램, 본문 그대로 인계)
■ 화면 전개도       (← 와이어프레임 / 라이브 탐색, 본문 그대로 인계)
■ 권한 매트릭스     (← 권한 자료, 본문 그대로 인계)
■ 도메인 용어집     (← Ubiquitous Language, 본문 그대로 인계)
   * 각 산출물에 표지·변경이력은 frontmatter / .meta.yaml로 첨부
   * 본문 양식 변환 X (사용자 정정 "그대로 인계" 일관)

[별도 트랙]
■ URS — 6월 구축 후 고객 협의 → 받음 → 기능 정의서 커버리지 보강 입력. scout-kit이 사전 작성 X.
```

### 4-2. 기능 정의서 산출물 — 시트 상세

#### 01_표지 (MYAPP Sheets 차용)
- 프로젝트명 (Project Name)
- 솔루션/제품 종류
- 핵심 가치 제안
- 대상 사용자
- 배포 지역
- 플랫폼
- 문서 버전
- 문서 상태 (Draft/Review/Approved/Superseded)
- AI 작성자 (AI Author)
- 사람 검수자 (Human Reviewer)
- 최초 작성일
- 최종 수정일
- 관련 문서 (인풋 출처 다중 — 단계 인풋 보증)

#### 04_변경이력 (MYAPP Sheets 차용)
| 컬럼 | 설명 |
|---|---|
| 버전 (Version) | V1, V2, ... |
| 변경일 (Date) | YYYY-MM-DD |
| 변경자 (Changed by) | AI / 사람 |
| 변경 유형 (Type) | 최초 작성·수정·검수·승인·고도화·revert |
| 변경 내용 (Description) | 자유 텍스트 (요점) |
| 영향받는 ID (Affected IDs) | FR-MYAPP-NNN, NFR-MYAPP-NNN, US-MYAPP-NNN 다중 |
| 리뷰/승인자 (Approved by) | 사람 검수자 |

#### 06_기능정의서 (17컬럼 — Sheets 22 → 17, self-review 반영, 영역 헤더 폐지 평면)

| # | 컬럼 |
|---|---|
| 1 | 기능 ID |
| 2 | 화면 ID |
| 3 | 페이지 경로 / Depth |
| 4 | 중분류 |
| 5 | 기능명 |
| 6 | 기능 목적 (Why) |
| 7 | 기능 요약 (1줄) |
| 8 | 사전 조건 |
| 9 | 상세 정책 / 기능 설명 |
| 10 | 입력 (Input) |
| 11 | 처리 로직 (Process) |
| 12 | 상태 전이 |
| 13 | 출력 (Output) |
| 14 | 예외/에러 처리 (★ 음성·예외 TC 도출 핵심) |
| 15 | TC ID (★ RTM 매핑) |
| 16 | 인풋 출처 (★ 행 단위 GxP 추적 — Sheets "관련 문서/링크" 역할) |
| 17 | 비고 (FR↔NFR 연결 노트 등 자유 텍스트) |

**제거 컬럼** (사용자 정정 — 1차 개발 완료 후 산출 문서라 무의미):
- 운영 메타 3: 우선순위, 담당자 / 공수, 진행 상태
- 다른 시트로 흡수 3: 필요 권한 (받기 #4 권한 매트릭스), 보안 / 개인정보 (07_비기능요구), 성능 요구 (07_비기능요구)

**self-review 발견 갭 부활** (2026-05-06):
- G1 예외/에러 처리: 받기 5종 사용자 시나리오는 정상 흐름 위주, BR 코드·HTTP 코드 매핑 없음 → 음성 TC 도출 위해 06 시트에 보존
- G2 인풋 출처: frontmatter 산출물 메타로는 행 단위 GxP 추적 부족 → 행 단위 컬럼 필요
- G3 비고: FR↔NFR 연결 노트 등 자유 텍스트 위치 필요

**영역 헤더 자체 폐지**: Sheets 22컬럼의 영역 그룹(🔖 식별 / 📂 분류 / 📝 정의 / ⚙️ 요구·제약 / 📊 관리)을 모두 폐지. 17컬럼 평면 운영. mergeCells 적용 X. 시각적 그룹화는 Sheets 컬럼 너비·색상으로 (필요 시).

#### 07_비기능요구 (Sheets 9컬럼 그대로)
| 컬럼 | 설명 |
|---|---|
| NFR ID | NFR-MYAPP-NNN |
| 범주 (Category) | 보안·감사·성능·접근성·가용성·신뢰성·사용성·유지보수·관측성·호환성·지속가능성 |
| 항목 (Item) | 명사형 |
| 요구 내용 (Requirement) | 자유 텍스트 |
| 측정 지표 / 임계값 (Metric & Threshold) | 정량 지표 |
| 검증 방법 (Verification) | 코드 리뷰·단위 테스트·통합 테스트·Penetration Test 등 |
| 우선순위 (Priority) | M / S / C / W (MoSCoW) |
| 관련 기능 ID (Related FR) | FR-MYAPP-NNN 다중 |
| 비고 (Notes) | 자유 |

#### 08_사용자스토리 (Sheets 9컬럼 그대로)
| 컬럼 | 설명 |
|---|---|
| Story ID | US-MYAPP-NNN |
| 에픽 (Epic) | 묶음 단위 |
| Sprint | S1·S2·S3 |
| 사용자 스토리 | "As a ___, I want ___, so that ___" |
| 인수 기준 (G/W/T) | "Given ... / When ... / Then ..." |
| 관련 기능 ID | FR-MYAPP-NNN 다중 |
| 포인트 (SP) | 1·2·3·5·8 (Fibonacci) |
| 우선순위 | M / S / C / W |
| 상태 | Backlog·In Progress·Done |

### 4-3. 받기 5종 — 메타 처리 + 형식별 분기 (G15 정정)

| 자료 형식 | 메타 처리 | 본문 처리 |
|---|---|---|
| markdown (`.md`) | 파일 머리 frontmatter 첨부 (project·domain·version·status·source·last_updated·change_log·confidence) | 그대로 |
| Mermaid (`.mmd`) | 별도 `{파일명}.meta.yaml` | 그대로 |
| PDF / DOCX | 별도 `.meta.yaml` | 원본 인계 + 옵션: scout-kit이 텍스트 추출 보조 파일 `{파일명}.text.md` 생성 (후공정 LLM 파싱 부담 경감) |
| 이미지 / 다이어그램 (PNG·JPG·SVG·.drawio·.puml) | 별도 `.meta.yaml` | 원본 그대로 인계. 후공정 처리 시 OCR 또는 사람 검수 (§7-2 후공정 처리 정책) |
| Excel (`.xlsx`·`.xls`) | 별도 `.meta.yaml` | 원본 그대로 |
| **공통 정책** | 본문 변환 **금지** — 받은 양식 그대로. ID 부여 **하지 않음** — 도메인 지식 차원, 후공정 참조용 | |

**다중 인풋 결합 정책** (G17 정정 — 받기 5종 1종에 다중 인풋 매핑 시):
- 예: 사용자 시나리오 = 유스케이스 다이어그램 + Process Flow (2건 인풋)
- 처리: 두 자료를 별도 파일로 인계 (`01-user-scenario-usecase.{ext}` + `01-user-scenario-flow.md`)
- 단일 인덱스 파일 옵션: `01-user-scenario.md` 추가 — 두 파일 참조·결합 설명 (사람 검수 보강 가능)
- `.meta.yaml`에 `source[]` 배열로 다중 원본 명시

**PRD 다중 역할 정책** (G16 정정):
- PRD가 정형화 인풋(기능 정의서) + 권한 매트릭스 인풋 둘 다인 경우 (예: 권한 매트릭스가 PRD §3.4 안에 흡수)
- 처리:
  - PRD 본문 → feature-spec (Google Sheets) 정형화 (전체 처리)
  - PRD 권한 섹션 추출 → `04-permission-matrix.md` 발췌 인계 (`.meta.yaml`에 `source: PRD_v2.md §3.4` 명시)
  - 원본 PRD는 `_source/`에 그대로 보존 (read-only)
- 단계 9 정형화 시 자동 분기 처리

### 4-4. 작업 폴더 구조 (개발자 측)

scout-kit은 개발자 작업 폴더에 다음 표준 구조를 생성한다.

```
{개발자 작업 폴더}/                  (예: D:/work/myapp-dev/)
└── qa-handoff/                      ← scout-kit 작업·인계 표준 root
    └── {프로젝트명}/                 (예: myapp — 트리거 시 [PROJECT: myapp] 헤더로 결정)
        ├── feature-spec.yaml        ← 정형화 산출물 = Google Sheets URL·ID 메타 (5시트: 01·04·06·07·08)
        ├── domain-knowledge/        ← 받기 5종 인계
        │   ├── 01-user-scenario.{원본 확장자}        (예: usecase.md / .pdf)
        │   ├── 01-user-scenario.meta.yaml             (표지·변경이력 메타)
        │   ├── 02-state-transition.{원본 확장자}
        │   ├── 02-state-transition.meta.yaml
        │   ├── 03-screen-layout.{원본 확장자}
        │   ├── 03-screen-layout.meta.yaml
        │   ├── 04-permission-matrix.{원본 확장자}
        │   ├── 04-permission-matrix.meta.yaml
        │   ├── 05-glossary.{원본 확장자}
        │   └── 05-glossary.meta.yaml
        ├── _source/                  ← 개발자 원본 사본 (reviewer 환각 검증용)
        ├── input-manifest.yaml       ← 자료 큐레이션 결과 (카테고리 매핑·최신본 ID·신뢰도)
        └── scout-log.md              ← 질의 이력·결정 이력
```

**폴더 운영 규약**:
- `qa-handoff/`는 git 추적 권장 (GxP 무결성·변경 이력 보존). 단 개발자 자료 라이선스 고려 시 .gitignore 검토.
- 파일 이름 prefix `01-` ~ `05-`은 받기 5종 정렬·식별용. 사용자 시나리오 = 01, 상태 전이도 = 02, 화면 전개도 = 03, 권한 매트릭스 = 04, 도메인 용어집 = 05.
- **Google Sheets**가 정형화 산출물 source-of-truth (사용자 정정 5차). `feature-spec.yaml`은 Sheets URL·ID·시트명·created_at 메타. 5시트 안 컬럼은 §4-2에서 정의.

**`_source/` ↔ `domain-knowledge/` 역할 분리** (G4 명확화):
- `_source/`: 자료 큐레이션 단계에서 식별된 **모든 입력 자료**의 원본 사본. PRD + 받기 5종 원본 + ERD/아키텍처 + 기타 참조 자료 모두 포함. **read-only**. 용도 = reviewer 환각 검증 + 단계 인풋 추적 보존.
- `domain-knowledge/`: 받기 5종에 `.meta.yaml` 메타가 첨부된 **1차 가공본**. 이름·prefix 정형화. 용도 = 후공정(tc-writer·script-generator 등) 직접 입력.

**기존 `qa-handoff/{프로젝트명}/` 폴더 재진입 처리** (G8 정정):
- 폴더 없음 → 신규 생성
- 폴더 이미 있음 → 사용자에게 처리 옵션 제시:
  - (a) 덮어쓰기 (기존 산출물 삭제 후 재작성)
  - (b) 다른 프로젝트명으로 진행 (예: `myapp-v2`)
  - (c) 부분 갱신 (input-manifest.yaml과 비교해 변경된 카테고리만 재작성)
  - (d) 중단
- 자동 덮어쓰기 **금지** (현 scout 가드레일 일관)

### 4-5. 산출물 생성 도구·스키마 (G10 정정 — 슬롯 정의)

본 spec은 슬롯만 정의. 상세 스키마는 후속 구현 단계에서 확정.

| 산출물 | 생성 도구 후보 | 스키마 슬롯 |
|---|---|---|
| `feature-spec` (Google Sheets, 5시트) | **Google Sheets MCP** (사용자 정정 5차 — 단일 채택. 외부 .xlsx 도구 검토 X). 시트 5개 (01·04·06·07·08) 신규 생성 → 본문 채움 → URL 인계. | §4-2 5시트 정의 차용 |
| `feature-spec.yaml` | YAML 직접 작성 | `google_sheets_id`, `url`, `sheets[]` (시트명 5개), `created_at`, `last_updated`, `owner` (개발자 이메일), `shared_with[]` (QA 이메일·역할) |

**Google Sheets 계정·공유 운영 패턴** (사용자 정정 6차 — 5차-1 갱신):
- **시트 생성 주체**: **QA 본인** Google 계정 (QA PC의 google-sheets MCP OAuth 인증)
  - 사유: 개발자 MCP 인증 미보유 케이스 다수 → 현실 반영. Sheets owner QA 단일점 통제 (GxP).
- **개발자 측**: markdown 5개로 정형화 (단계 9). Google 계정 OAuth **불필요**.
- **단계 17a 이행**: QA가 `markdown-to-sheets` 스킬 호출 → markdown 5개 → Sheets 5시트 자동 이행
  - 옵션 A: 신규 시트 생성 (`create_spreadsheet`)
  - 옵션 B: 사전 공유 시트 활용 (engagement-brief에 `google_sheets_id` 사전 등록 → `batch_update_cells`)
- **개발자 검수 권한**: QA가 `share_spreadsheet`로 개발자 이메일에 editor 권한 (단계 18c)
- **GxP 무결성**: Sheets owner=QA 단일. 변경 추적 = Sheets revision history. 개발자 검수 = 댓글·수정 (revision 기록).

**금지 패턴** (보안):
- 개발자 PC에서 QA 계정 강제 인증 X (토큰 유출 위험)
- 공용 서비스 계정 X (계정 책임 추적 어려움)
- 개발자 단독 owner X (정정 6차 — QA 단일점 통제로 변경)

**금지 패턴** (보안):
- 개발자 PC에서 QA 계정 강제 인증 X (토큰 유출 위험)
- 공용 서비스 계정 X (계정 책임 추적 어려움)
| `{N}-{받기5종}.meta.yaml` | YAML 파일 직접 생성 | 필수 필드: `project`, `domain`, `category`(user-scenario·state-transition·screen-layout·permission-matrix·glossary), `source`(원본 파일명), `confidence`(★★★/★★/★), `last_updated`. 옵션 필드: `version`, `change_log[]`, `notes` |
| `input-manifest.yaml` | YAML 파일 직접 생성 | `scan_root`, `found_files[{path, mtime, git_commit, category, confidence, status(confirmed/skipped/missing)}]`, `missing_categories[]`, `developer_responses[]` |
| `scout-log.md` | Markdown append-only | 항목 형식: `## YYYY-MM-DD HH:MM · {event_type}` + 본문 (event_type = 질의·답변·결정·정형화 진행) |

### 4-6. 모델 라우팅 정책 (사용자 정정 7차)

scout-kit 내부 단계별 모델 매핑 — 단순 작업은 Haiku, 균형 작업은 Sonnet, 깊은 분석은 Opus. 비용·속도·정확도 최적화.

| 단계 | 작업 성격 | 모델 | 에이전트 |
|---|---|---|---|
| 메인 오케스트레이션 | 단계 흐름·의사결정·인터뷰 | **Sonnet** | `scout` (메인) |
| 단계 5 자료 큐레이션 | Glob·파일명 매칭·1차 분류 (대량 파일 단순 패턴) | **Haiku** | `scout-curator` (sub-agent) |
| 단계 9 PRD 분석 | F-NNN 분해·17컬럼·BR 코드 매핑·5패턴 모호점 탐지 (깊이 있는 분석) | **Opus** | `scout-analyzer` (sub-agent) |
| 단계 9 markdown 작성 | 분석 결과 → 양식 채움 (균형) | **Sonnet** | `scout` 메인 |
| 단계 17a Sheets 이행 | markdown 파싱·MCP 호출 (단순 변환) | **Haiku** | `scout` 메인이 `markdown-to-sheets` 스킬 호출 (sub-agent 분리 X — over-engineering) |

### 라우팅 메커니즘

- 메인 `scout` 에이전트가 Agent 도구로 sub-agent spawn
- sub-agent는 자기 frontmatter `model:` 사용 (haiku / opus)
- 메인 scout는 sonnet — sub-agent 결과 종합·다음 단계 진입

### 모델 ID

- Haiku 4.5: `claude-haiku-4-5-20251001` 또는 alias `haiku`
- Sonnet 4.6: `claude-sonnet-4-6` 또는 alias `sonnet`
- Opus 4.7: `claude-opus-4-7` 또는 alias `opus`

agent frontmatter는 alias 사용 (예: `model: haiku`).

### 4-7. ID 체계 1차안 (내부 ID owner 협의 후 최종)

### 4-4. ID 체계 1차안 (내부 ID owner 협의 후 최종)

기준: 모듈 코드 MYAPP 단일. 종류 prefix 앞에. 도메인 구분은 ID에 포함 X, [중분류] 컬럼.

| 시트 | ID 패턴 | 예시 |
|---|---|---|
| 06_기능정의서 (기능 ID) | FR-MYAPP-NNN | FR-MYAPP-001 |
| 06 화면 ID 컬럼 | SCR-MYAPP-NNN | SCR-MYAPP-001 |
| 07_비기능요구 | NFR-MYAPP-NNN | NFR-MYAPP-001 |
| 08_사용자스토리 | US-MYAPP-NNN | US-MYAPP-001 |
| TC ID (06 매핑 컬럼) | TC-MYAPP-NNN | TC-MYAPP-001 |

규약:
- 일련번호: 결번 허용 (삭제된 ID 재사용 금지 — GxP 추적 무결성)
- 0 패딩 3자리 (`001` ~ `999`). 1000 도달 시 4자리 확장
- 받기 5종: ID 부여 X
- RTM: 06 시트 TC ID 컬럼이 곧 RTM. 별도 RTM 시트 X
- 도메인 구분: 시트 안 [중분류] 컬럼으로 (USER_PERMISSION·MASTER_DATA_SAP·RECIPE_MBR·BATCH_EXECUTION·ESIGN_AUDIT 등 7도메인)

## 5. 절차 (Procedure)

### 5-1. 워크플로 시나리오 V2 (단계 -1 ~ 20, 양방향 인계)

```
[양방향 인계 — QA ↔ 개발자]

-1. QA → 개발자 사전 인계 (G20 정정):
    - 플러그인 install 가이드: `/plugin marketplace add cmi94/qa-kit` → `/plugin install qa-scout@qa-kit` (또는 수동 카피)
    - 사전 안내서 1쪽: 무엇을 준비·무엇을 받는지·자료 부족 보강 옵션·예상 소요
    - 인계 약속 합의: 결과 전달 방법 (zip / git / 클라우드 — 단계 14에서 선택) + 일정
    - 전달 매체: Slack / 이메일 등

[개발자 측 단계]

0. 개발자: 사전 안내서 1쪽 검토 + 자료 폴더 정리·확보
1. 개발자: Claude Code 세션 시작 (자기 개발 폴더에서)
2. 개발자: 트리거 with PROJECT 헤더 (예시: `[PROJECT: myapp] scout 호출` — 정확한 트리거 키워드는 후속 결정, **PROJECT 헤더 포함 원칙은 본 spec 확정**)
3. 플러그인: qa-handoff/{프로젝트명}/ 작업 폴더 처리 (§4-4 재진입 처리 정책: 신규 생성 / 사용자 옵션 제시) + 자료 폴더 경로 요청
4. 개발자: 자료 폴더 경로 제공 (절대 또는 상대, 다중 가능 — §3-2 입력)
   - scout-kit이 폴더 존재·읽기 권한 검증 → 실패 시 재입력 요청 (오류 사유 명시)
5. 플러그인: 자동 스캔 → 카테고리 매핑 + 최신본 식별 (★ 핵심)
6. 개발자: 매핑·최신본 확정 (텍스트 답변)
7. 플러그인: 빠진 카테고리 가이드 (라이브 URL / 자기 AI / 생략)
8. 개발자: 응답 (텍스트)
9. 플러그인: 정형화 + 인계 (qa-handoff/{프로젝트명}/ 안에 저장)
   - **feature-spec/ markdown 5개** (개발자 측 — 사용자 정정 6차)
     · 01_표지.md / 04_변경이력.md / 06_기능정의서.md (17컬럼) / 07_비기능요구.md / 08_사용자스토리.md
     · 개발자 측은 markdown 작성만 — Google Sheets MCP OAuth 인증 불필요
     · Sheets 이행은 단계 17a QA 측에서 수행
   - domain-knowledge/ (받기 5종 + .meta.yaml 메타. 다중 인풋 결합 시 §4-3 G17 정책 적용)
   - _source/ (개발자 원본 사본)
   - input-manifest.yaml (큐레이션 결과)
   - scout-log.md (질의 이력)
10. 플러그인: 모호점·자료 부족 발견 시 추가 질문
11. 개발자: 답변
12. 플러그인: 완료 보고 (산출물 위치 + 채움률 + 질의 이력)

[개발자 → QA 인계 — G18 정정]

13. 개발자: 결과 검토 (qa-handoff/{프로젝트명}/ 내 산출물·input-manifest 검증)
14. 개발자: 인계 패키지 구성 (단계 -1 합의 옵션 따름):
    - (a) zip 압축: `qa-handoff-{프로젝트}-{YYYY-MM-DD}.zip` → Slack/이메일
    - (b) git commit + push (저장소 합의 시) → QA pull
    - (c) 클라우드 업로드 (Google Drive 등) + 공유 링크 → Slack
15. QA: 패키지 수령 + 무결성 점검 (input-manifest.yaml 일치 + 모든 파일 존재 + scout-log 검토)
16. QA: 무결성 OK 시 단계 17 진입. 결손 발견 시 개발자에 추가 자료 요청 → 단계 7 회귀.

[QA 측 후속 처리 — G19 정정]

17a. **QA: markdown → Google Sheets 이행** (사용자 정정 6차 — 신규 단계, G23 정정)
    - **호출 주체** (G23): QA가 Claude Code 일반 세션에서 `Skill: markdown-to-sheets` **직접 호출**. 메인 scout 에이전트 spawn 없음 — 단계 17a~20은 QA 측 별도 흐름.
    - QA 본인 Google 계정으로 Sheets 신규 생성 (또는 사전 공유 시트 활용 — 옵션 B)
    - feature-spec/ markdown 5개 → Sheets 5시트로 자동 이행 (batch_update_cells)
    - `feature-spec.yaml` 작성 (google_sheets_id·url·owner=QA·shared_with=개발자)
    - 04_변경이력 시트 첫 행 추가 (이행 시점 + QA 검수자 ID)
17b. QA: qa-workbench 저장소 흡수
    - 위치: `knowledge/{프로젝트}/scout-handoff/` (제안)
    - markdown 5개 + Sheets URL 메타 + domain-knowledge/ + _source/ + input-manifest + scout-log 모두 보존
    - Sheets가 SoT, markdown은 인계 매개체로 archive
18a. **인사팀 reviewer 자동 검수** (§5-3 자동 검증, G24 정정 — 검증 대상 명시)
    - **검증 대상** (G24): **Sheets 5시트** (단계 17a 이행 후 — Sheets가 SoT). markdown 단계 검증은 단계 16 무결성 점검에서 처리됨.
    - 헤더·자료부족 마커·환각 패턴·일관성·인풋 출처 ID 유효성 자동 점검 — Google Sheets MCP `get_sheet_data`로 시트 본문 읽어 검증
    - reviewer 에이전트 호출 (qa-workbench 측)
18b. **인사팀 reviewer 사람 검수** (사람 검수 슬롯)
    - "현업 확인 필요" 슬롯 (배포 지역·검수자 ID 등)
    - "GxP 디테일 보강" 슬롯
    - 검수 의견 → 04_변경이력 시트 행 추가
18c. **개발팀 검수 요청** (사용자 정정 6차 — 신규 단계)
    - QA가 Sheets URL을 개발팀(원작성 개발자)에 공유 + 검수 요청
    - 개발팀 검수 권한: editor (댓글/수정 가능)
    - 검수 의견은 Sheets 댓글 또는 별도 채널 (Slack)
19. **개발팀 검수 → QA 회귀** (양방향 검수 사이클)
    - 개발팀 검수 의견 → QA 측 처리:
      - 단순 정정: QA가 Sheets 직접 갱신 (04_변경이력 행 추가)
      - 자료 부족·근거 부재: 단계 7 회귀 (개발팀에 추가 자료 요청)
      - 양식·정책 변경: 단계 17a 회귀 (재이행)
20. 인계 사이클 종료. Sheets v1.0 정식 발행 (04_변경이력 행 추가). 후속 회귀는 부분 갱신.
```

### 5-2. 자료 큐레이션·최신성 확인 절차 V1 (단계 5 상세)

```
1. 스캔
   - Glob 광범위 패턴: **/*.{md,pdf,docx,doc,png,jpg,svg,mmd,xlsx,xls,csv,json,yaml,yml,txt,drawio,puml,plantuml}
   - 제외 디렉토리: .git/, node_modules/, dist/, build/, .venv/, __pycache__/ 등 시스템·빌드 산출물
   - 추가 패턴: 트리거 옵션 또는 engagement-brief에서 확장 (구현 단계 결정)
   - 메타: mtime + git 마지막 commit (있으면)

2. 1차 매핑 (저비용)
   - 파일명 패턴 (prd*, requirement*, usecase*, sequence*, flow*, wireframe*, role*, permission*, glossary*, ubiquitous*, erd*)
   - 디렉토리명 (./docs/prd/ → PRD 후보)
   - 신뢰도 ★★★

3. 2차 매핑 (모호 시)
   - 파일 첫 N줄 Read (Mermaid 시퀀스·표·자유 텍스트 추정)
   - 신뢰도 ★~★★ / X(분류 불가)

4. 다중 후보 정렬 (같은 카테고리 N건 발견 시)
   - 파일명 버전 표기 (v1·v2·draft·final)
   - mtime
   - git log 마지막 commit
   - frontmatter 메타

5. 단일 보고서 출력
   "카테고리별 발견 현황 + 최신 선택 요청 + 분류 불가 + 빠진 카테고리"

6. 빠진 카테고리 가이드 (보고서 안에 포함)
   - 와이어프레임 → 라이브 URL+계정 / 생략
   - ERD → 자기 AI 생성 (프롬프트 템플릿 제공) / 생략

7. 개발자 텍스트 답변 (자연어) → AI 파싱 → 확정 매핑

8. 메타 태깅
   {카테고리, 형식(MD/PDF/Mermaid…), 버전, 일자, 신뢰도, 인풋 출처}
   → 인계 frontmatter에 기록 (단계 인풋 보증 = 회의 결정 #3)
```

핵심 룰:
- **추정 금지**: 단일 후보여도 사용자 확인 1줄 ("이게 최신 맞나요?")
- **신뢰도 명시**: ★★★ 파일명 / ★★ 디렉토리 / ★ 내용 추정 / X 분류 불가
- **다층 메타 활용**: 파일명·mtime·git log·frontmatter 종합
- **개발자 부담 최소**: AI 1차 매핑 추정 → 개발자 텍스트 답변만

### 5-3. 검수 게이트

#### 자동 검증 (PostToolUse 훅 또는 reviewer 에이전트)
- 헤더 존재 (시트별 필수 헤더)
- `[자료 부족]` 마커 분포 (필수 카테고리 임계 초과 시 경고)
- 출처 표기 누락 셀 카운트
- 환각 패턴 (출처 없음 + 단정형 문장)
- 일관성 (도메인 용어집의 용어가 다른 산출물에 동일 표기)
- 단계 인풋 ID 유효성 (frontmatter 인풋 출처가 실제 존재하는 산출물 ID)
- TC ID 매핑 무결성 (06 시트 TC ID 컬럼의 ID가 실제 TC와 매핑)

#### 사람 검수 슬롯 (산출물에 명시 표시)
- "현업 확인 필요" — 정책·규제 결정 사안 (MYAPP B의 8건 같은 사례)
- "표지·배포 정보" — 표지 사람 영역 (MYAPP C의 4셀 같은 사례)
- "변경이력 V1.0 행" — 검수 후 1.0 정식 발행 (MYAPP D 같은 사례)
- "GxP 디테일 보강" — 도메인 특화 디테일 (레인지·예외·길이 등 — 받기 5종·07 비기능에 분산되어 있는 정보를 사람이 종합 보강)

MYAPP USER_PERMISSION이 본 게이트의 첫 인스턴스가 됨 (B/C/D 잔여 → 새 게이트로 흡수).

## 6. 성공 기준 (Acceptance Criteria)

### 6-1. spec 자체 (본 문서)
- [x] 9섹션 전체 작성
- [x] 사용자 정정 10개 모두 반영 (Core/Meta 폐기·RTM 흡수·변경이력 frontmatter·URS 별도·NFR 시트 분리·한글화·셋 분리·받기 5종·최신성 확인·정형화 1종)
- [x] MYAPP Sheets 양식 5시트 차용 명시
- [x] 17컬럼 (self-review 후 G1·G2·G3 부활) + 이모티콘 제거 명시
- [x] 작업 폴더 구조 명시 (qa-handoff/{프로젝트명}/ 표준 root, feature-spec.yaml = Google Sheets URL 메타, domain-knowledge/, _source/, input-manifest.yaml, scout-log.md)
- [x] PROJECT 헤더 입력 명시 (트리거 시점)
- [x] 받기 5종 본문 변환 X 명시
- [x] ID 체계 1차안 명시
- [x] 자료 큐레이션 V1 8단계 명시
- [ ] 사용자 review·승인

### 6-2. 후속 구현 검증 (본 spec 범위 외)
- [ ] 5시트 양식 파일 작성 (`plugins/qa-scout/templates/feature-spec/`)
- [ ] `curate-input` 스킬 구현
- [ ] `docs-to-function-spec` 스킬 17컬럼 적응
- [ ] MYAPP USER_PERMISSION → v0.2 매핑 dry-run 성공 (FR 21건 + NFR 9건 + US 14건이 v0.2 양식에 손실 없이 매핑됨)
- [ ] ID owner 협의 완료 (1차안 검토·정정·확정)

## 7. 제약·주의 (Constraints)

### 7-1. 양식 제약
- **이모티콘 전면 금지** (공식 문서). 06 시트 그룹 헤더 이모티콘(🔖📂📝⚙️📊) 제거. 모든 양식·README·스킬 정의에 이모티콘 사용 X.
- **받기 5종 본문 변환 금지** — frontmatter 메타만 첨부, 본문은 받은 양식 그대로.
- **표지·변경이력은 모든 산출물 공통** (5시트 안 + 받기 5종 frontmatter 모두).
- **6시트 → 5시트** (Sheets 02_AI작성지침 시트 — v0.2 양식에서는 메타 가이드라 별도 산출물 X. 보존하되 산출물 카운트에서 제외).

### 7-2. 워크플로 제약
- **추정 금지** — 자료 큐레이션 단계에서 단일 후보여도 사용자 확인. 인풋 ID 매핑 단계에서도 추정 X.
- **단계 인풋 보증** — 모든 산출물 frontmatter에 인풋 산출물·버전 명시. 회의 결정 #3 (RTM 단계 추적).
- **GxP 정형화 = 기능 정의서 1종**. 받기 5종은 도메인 지식이라 GxP 양식 요건 면제.
- **개발자 답변 = 자연어 텍스트** — YAML 매니페스트·인터랙티브 Q&A보다 단일 보고서 + 텍스트 답변 (Claude Code 대화형 환경 자연스러움).
- **받기 5종 후공정 처리 정책** (G7 정정):
  - 후공정(tc-writer·script-generator 등)은 받기 5종을 도메인 지식 입력으로 받음
  - `.meta.yaml` 메타로 양식·신뢰도 식별 후 적절 처리
  - markdown / Mermaid: 직접 파싱
  - PDF / DOCX / 이미지: summaryDocuments MCP 또는 OCR로 텍스트 추출 후 처리
  - 양식이 후공정 처리 한계를 넘으면 사람 검수 슬롯 활성화 ("도메인 지식 보강 필요" 마커)
  - 후공정은 받기 5종 양식 변환·재포맷 시도 X (사용자 정정 "그대로 인계" 일관)

### 7-3. 보안·범위 제약
- 개발자 자료에 PII·비밀번호 등 민감 정보 포함 시 _source 인계 패키지에 그대로 포함될 수 있음 → 개발자가 사전 검토 책임. scout-kit은 자동 마스킹 X (GxP 추적성 우선).
- URS는 본 spec 범위 외. 6월 구축 후 별도 트랙. 사전 작성 시도 금지 (고객 측 SoT).
- 품질 보증 방안 문서는 보류. 회의 deliverable 후보지만 도메인 지식 차원과 별도라 별도 spec에서 다룸.

### 7-4. 마이그레이션 제약 (MYAPP Stage 1)
- MYAPP Stage 1 USER_PERMISSION (Sheets <sheets-id-redacted>) 결과는 **legacy 보존**. 22컬럼 그대로 유지.
- v0.2 적용은 **MYAPP Stage 2 신규 도메인부터** (MASTER_DATA_SAP 등).
- 사유: Stage 1 결과 재포맷 비용 + Stage 1 검수 게이트(B/C/D)가 진행 중이라 양식 변경이 검수 흐름 저해.
- 단, MYAPP Stage 1 결과를 v0.2 양식에 dry-run 매핑은 검증 단계에서 수행 (후속 작업).

## 8. 검증 (Verification)

### 8-1. spec 자체 검증
- 사용자 review (본 spec 승인 게이트)
- 사용자 정정 10개 누적 vs spec 본문 대조 (반영 여부 자가 점검)

### 8-2. MYAPP Stage 1 → v0.2 매핑 dry-run (후속)
- 입력: MYAPP Sheets 6시트 (현 USER_PERMISSION) + scout-output 5종 (현)
- 출력: v0.2 양식에 손실 없이 매핑되는지 점검
- 매핑 표:
  - Sheets 01 → v0.2 01_표지 (그대로)
  - Sheets 02_AI작성지침 → 메타 가이드 보존 (산출물 X)
  - Sheets 04 → v0.2 04_변경이력 (그대로)
  - Sheets 06 (22컬럼) → v0.2 06 (17컬럼) — 6컬럼 제거 (운영 메타 3 + 다른 시트 흡수 3) + TC ID 신규 + 예외/에러·인풋 출처·비고 보존
  - Sheets 07 → v0.2 07 (그대로)
  - Sheets 08 → v0.2 08 (그대로)
  - scout-output glossary → 받기 5종 #5 (도메인 용어집)
  - scout-output e2e-flow → 받기 5종 #1 (사용자 시나리오)
  - scout-output layout → 받기 5종 #3 (화면 전개도)
  - scout-output permission → 받기 5종 #4 (권한 매트릭스)
  - scout-output state-transition → 받기 5종 #2 (상태 전이도)
  - scout-output function-spec (stub) → 폐기 (Sheets 06이 대체)

### 8-3. 후속 구현 검증 (본 spec 범위 외)
- 5시트 양식 파일 생성 후 MYAPP USER_PERMISSION 데이터로 채우기 dry-run
- `curate-input` 스킬 MYAPP 자료 폴더 대상 자동 스캔·매핑 정확도 (수동 검수)
- 17컬럼이 실제 TC 도출에 충분한지 (받기 5종 + 07 시트와 함께) — TC 5건 시작성 (실증)
- ID owner 검토 결과 반영

### 8-4. 회귀 검증 — 후공정 호환성
- tc-writer·script-generator·ticket-analyzer가 v0.2 산출물 묶음(기능 정의서 5시트 + 받기 5종)을 입력으로 받아 정상 동작
- 받기 5종 양식 가변(MD·PDF·Mermaid 혼재) 처리 가능

## 9. 변경 이력

| 일자 | 변경 | 사유 |
|---|---|---|
| 2026-05-06 | draft 작성 | 회의 인사이트 + 사용자 티키타카 정정 10개 누적 → 골격 정리. ExitPlanMode 승인 후 정식 spec 진입. |
| 2026-05-06 | 06 시트 14 → 17컬럼 정정 | self-review에서 G1(예외/에러)·G2(인풋 출처)·G3(비고) Critical 갭 발견. MYAPP FR-MYAPP-001·010 dry-run에서 음성 TC 도출 불가 + GxP 행 단위 추적 부족 확인. 사용자 결정에 따라 3컬럼 부활. |
| 2026-05-06 | §4-4 작업 폴더 구조 신규 + feature-spec.xlsx 5시트 형식 결정 + PROJECT 헤더 입력 명시 | 사용자 지적 — 개발자 측 산출물 저장 표준 부재. qa-handoff/{프로젝트명}/ root 채택, .xlsx 1파일 5시트 채택, 트리거 시 PROJECT 헤더로 폴더명 결정. |
| 2026-05-06 | 2차 self-review Minor 갭 4건 정정 | G4 (_source/ 범위 명확화 — 모든 입력 자료 사본·domain-knowledge 역할 분리) + G5 (트리거 결정·후속 경계 명확화 — PROJECT 헤더 원칙 확정, 키워드 패턴만 후속) + G6 (영역 헤더 폐지 — 17컬럼 평면, mergeCells 적용 X) + G7 (받기 5종 후공정 처리 정책 — .meta.yaml 식별·양식별 처리·사람 검수 활성화). spec 정합성·구현 명세 향상. |
| 2026-05-06 | 3차 시나리오 검증 Major 5건 정정 | MYAPP 시나리오 단계 0~12 끝까지 시뮬레이션. G8(폴더 충돌 처리 정책 §4-4) + G9(자료 폴더 경로 형식·검증 §3-2·§5-1) + G10(산출물 도구·스키마 §4-5 신설, ID 체계 §4-6으로 번호 밀림) + G14(Glob 패턴 18개 형식 + 제외 디렉토리 §5-2) + G15(받기 5종 형식별 분기 §4-3 — markdown/Mermaid/PDF/이미지/Excel 처리). 입력→출력 흐름 일관성 + 구현 명세 명확화. |
| 2026-05-06 | 4차 실제 동작 시나리오 검증 Critical 2 + Major 3 정정 | end-to-end 흐름 QA↔개발자 양방향 인계 보강. G16(PRD 다중 역할 — 정형화 + 권한 매트릭스 발췌, §4-3 정책 추가) + G17(받기 #1 다중 인풋 결합 — 별도 파일 + 인덱스 옵션, §4-3 정책 추가) + G18(단계 13~16 개발자→QA 인계 — zip/git/클라우드 3옵션, §5-1 추가) + G19(단계 17~20 QA 측 후속 처리 — qa-workbench 저장소 흡수·후공정 트리거·검수 피드백, §5-1 추가) + G20(단계 -1 QA→개발자 사전 인계 — install 가이드·사전 안내서·인계 약속, §5-1 추가). spec 범위 확장 (단계 -1 ~ 20 양방향). |
| 2026-05-06 | 5차 정정 — feature-spec.xlsx → Google Sheets 단일 채택 | 사용자 의견: ".xlsx 도구 부재 한계 + 받기 5종은 개발자 본인 관리". 정형화 산출물 = Google Sheets (Google Sheets MCP 단일 도구). 폴더 구조 `feature-spec.xlsx` → `feature-spec.yaml` (Sheets URL·ID 메타). 협업 친화·실시간 검수·외부 .xlsx 도구 의존 제거. §2-1·§4-1·§4-3·§4-4·§4-5·§5-1·§6 정정. 받기 5종 정책 그대로 — 본문 변환 X, 개발자 본인 원본 관리 강화 명시. |
| 2026-05-06 | 5차-1 정정 — Sheets 계정·공유 운영 패턴 명시 (§4-5) | 사용자 질의 "개발자 PC에서 QA 계정 인증 가능?". 답: 보안상 권장 X. 표준 패턴 — 개발자 본인 계정으로 시트 생성 + scout-kit이 share_spreadsheet로 QA 이메일 자동 공유. owner=개발자·reviewer=QA 분리 추적 (GxP). feature-spec.yaml에 owner·shared_with 필드 추가. |
| 2026-05-06 | 6차 정정 — 운영 모드 변경: markdown → QA 이행 + 양방향 검수 | 사용자 의견 "개발자 MCP 인증 안 된 케이스 多. markdown 받고 내가 Sheets 만들고 인사팀 reviewer 체크 + 개발팀 검수 순서?". 답: 권장. (1) 단계 9 산출물 = markdown 5개 (개발자 OAuth 불필요). (2) 단계 17a 신규 — QA 측 markdown→Sheets 이행 (markdown-to-sheets 신규 스킬). (3) 단계 18a~c — 인사팀 자동·사람 검수 + 개발팀 검수. (4) 단계 19 양방향 회귀. (5) Sheets owner=QA 단일점 통제 — 5차-1 패턴 갱신. 신규 스킬 `markdown-to-sheets` 추가. spec §5-1·§4-5·§9. |
| 2026-05-06 | 7차 정정 — 모델 라우팅 (Haiku·Sonnet·Opus) | 사용자 의견 "최적화 필요 — 문서 찾기 Haiku, 분석 Opus, md 작성 Sonnet". §4-6 모델 라우팅 정책 신설. 단계 5 자료 큐레이션(대량 파일 단순 패턴) → Haiku, 단계 9 PRD 분석(F-NNN 분해·BR 매핑·5패턴 모호점) → Opus, 메인 오케스트레이션 + markdown 작성 → Sonnet. 신규 sub-agent 2개: scout-curator (Haiku), scout-analyzer (Opus). scout 메인은 Agent 도구로 sub-agent spawn. plugin.json agents 3개 등록. ID 체계 §4-6 → §4-7로 번호 밀림. |
| 2026-05-06 | 8차 검수 + 정정 — 도구·tools·표기·운영 흐름 일관성 | 8차 self-review. 6갭 정정: **G21 Critical** Task→Agent 일괄 4곳 (도구 이름 불일치, 실제 호출 실패 위험) + **G22 Major** scout-curator tools에 Skill 추가 (curate-input 호출 가능) + **G23 Major** 단계 17a 호출 주체 명시 (QA가 Skill: markdown-to-sheets 직접 호출, 메인 scout spawn X) + **G24 Major** 단계 18a 검증 대상 = Sheets 5시트 (markdown 검증은 단계 16) + **G26 Minor** scout-analyzer 반환 형식 옵션 a 채택 명시 + **G27 Minor** sub-agent 본문 "Task prompt"→"Agent prompt" + **G28 Minor** spec 본문 "14컬럼" 옛 표기 5건 → "17컬럼" (변경이력 행 보존). G25 plan 파일 5~7차 누락은 별도 갱신. |
