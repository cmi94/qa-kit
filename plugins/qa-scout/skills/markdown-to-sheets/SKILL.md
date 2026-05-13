---
name: markdown-to-sheets
description: QA가 단계 17a에서 호출하는 스킬. 개발자가 인계한 feature-spec/ markdown 5개를 QA 본인 Google 계정의 Google Sheets 5시트로 자동 이행한다 + GxP 표준 디자인 결정론적으로 적용한다. google-sheets MCP 활용 — create_spreadsheet (옵션 A 신규) 또는 batch_update_cells (옵션 B 사전 공유 시트). feature-spec.yaml 메타 자동 생성 + share_spreadsheet로 개발자 editor 권한 부여 (단계 18c 검수 준비).
---

# markdown-to-sheets

scout v0.2 단계 17a (QA 측 markdown → Sheets 이행) 전용 스킬. 사용자 정정 6차로 신설 (개발자 MCP 인증 부담 해결).

v0.2.7 갱신 (2026-05-13): GxP 표준 디자인 결정론적 적용 단계 추가. 시트 번호 체계 표준 양식(01·02·03·04·05·06) 채택. 디자인 spec: `docs/specs/2026-05-13-feature-spec-standard-design.md`.

## 사용 시점
QA가 단계 13~16 인계 패키지 수령 + 무결성 점검 통과 후 호출. QA PC의 google-sheets MCP는 QA 본인 OAuth 인증 필수.

## 입력
- 인계 패키지: `qa-handoff/{프로젝트명}/feature-spec/` markdown 5개 (`01_표지.md`·`02_변경이력.md`·`03_기능정의서.md`·`04_비기능요구.md`·`05_사용자스토리.md`)
- `developer_email` 입력 우선순위 (v0.2.5):
  1. `qa-handoff/{프로젝트명}/input-manifest.yaml > contact.developer_email` (단계 11b 자동 수집 — 권장)
  2. engagement-brief의 `google_sheets_id`/이메일
  3. 사용자 인터랙티브 입력 (1·2 모두 부재 시)
- `mode`: `new` (옵션 A 신규 생성) | `pre-shared` (옵션 B 사전 공유 시트)
- `google_sheets_id`: pre-shared 모드일 때 사전 시트 ID (필수)
- `include_optional`: 06_18c_개발팀_질의 시트 포함 여부 (선택, 기본 false)

## 출력
- Google Sheets 5시트(또는 6시트 with `--include-optional`) 채움 + 표준 디자인 적용
- `qa-handoff/{프로젝트명}/feature-spec.yaml` 작성 (URL·ID·owner·shared_with)
- `share_spreadsheet` 호출 → 개발자 editor 권한
- `scout-log.md` append

## 절차 (6단계)

### 1) 모드 결정 + Sheets 셋업

#### 옵션 A — 신규 생성
```python
sheet = create_spreadsheet(title="<프로젝트명> Feature Spec (qa-scout-kit v0.2)")
sheets_id = sheet.id
```

> 신규 시트 생성은 절차 3 디자인 적용 단계에서 `apply.py --stage add` payload 호출로 일괄 처리. 본 단계에선 spreadsheet만 생성.

#### 옵션 B — 사전 공유 시트
```python
sheets_id = engagement_brief["google_sheets_id"]
```

> 기존 시트 매핑은 `list_sheets`로 확인 후 절차 3에 전달.

### 2) markdown 파싱 + 시트별 데이터 추출

각 markdown frontmatter `sheet:` 필드로 대상 시트 식별:

| markdown | 대상 시트 | 파싱 방식 |
|---|---|---|
| `01_표지.md` | 01_표지 | 메타 표 → key-value 2컬럼 (자유 디자인) |
| `02_변경이력.md` | 02_변경이력 | 표 → 7컬럼 (버전·일자·변경자·유형·내용·영향 ID·승인자) |
| `03_기능정의서.md` | 03_기능정의서 | F-NNN 섹션별 17컬럼 행 추출 |
| `04_비기능요구.md` | 04_비기능요구 | 표 → 8컬럼 |
| `05_사용자스토리.md` | 05_사용자스토리 | 표 → 8컬럼 |

### 3) 표준 디자인 적용 (Stage 1 — addSheet)

`{PLUGIN_ROOT}/scripts/feature-spec-design/apply.py` 호출로 batch_update payload 생성 → MCP `batch_update` 호출.

```bash
python {PLUGIN_ROOT}/scripts/feature-spec-design/apply.py \
    --spreadsheet-id <sheets_id> \
    --stage add \
    --existing-sheets-json '<{title:sheetId} JSON>' \
    [--include-optional]
```

stdout JSON의 `requests` 배열을 `mcp__google-sheets__batch_update`에 전달. 6시트(또는 5시트) 생성 완료 후 `list_sheets` 재호출하여 sheetId 매핑 갱신.

### 4) 표준 디자인 적용 (Stage 2 — design)

각 design_managed 시트별로 design payload 생성 + 적용:

```bash
python {PLUGIN_ROOT}/scripts/feature-spec-design/apply.py \
    --spreadsheet-id <sheets_id> \
    --stage design \
    --existing-sheets-json '<갱신 매핑>' \
    --sheet-title <시트명> \
    --compact
```

각 시트별로 MCP `batch_update` 호출 (사이즈 분할 — 03 17컬럼은 단일 호출이 큼). 결과: 헤더 텍스트·색·폰트·행 높이·컬럼 너비·보더·frozenRowCount 모두 결정론적 적용.

> 동일 텍스트 통일 룰(`design-tokens.json > column_widths_by_name`)로 시트 간 동일 헤더는 동일 너비. 예: `No.`=40, `TC ID`=80, ID류=100.

### 5) markdown 본문 데이터 입력

각 design_managed 시트의 row 2 이하에 markdown 행 데이터 입력:

```python
batch_update_cells(
  spreadsheet_id=sheets_id,
  sheet="03_기능정의서",
  ranges={"A2:Q22": [[FR-<PROJECT>-001~021 행]]}  # 21행 × 17컬럼
)
```

01_표지는 자유 디자인 — markdown 표 그대로 매핑(키-값 2컬럼 또는 시트별 양식).

### 6) feature-spec.yaml + share + scout-log

```yaml
project: <project>
google_sheets_id: <sheets_id>
url: https://docs.google.com/spreadsheets/d/<sheets_id>/edit
design:
  spec: SPEC-2026-05-13-feature-spec-standard-design
  applied_at: <ISO 8601>
sheets:
  - 01_표지
  - 02_변경이력
  - 03_기능정의서
  - 04_비기능요구
  - 05_사용자스토리
  # 06_18c_개발팀_질의 (include_optional=true 시)
owner: <QA 이메일>
shared_with:
  - email: <개발자 이메일>
    role: editor
mode: <new | pre-shared>
```

```python
share_spreadsheet(spreadsheet_id=sheets_id, email_addresses=[developer_email], role="editor")
```

scout-log.md append (timestamp + 이행 행 수 + 디자인 PASS 여부 + 공유 결과).

## 핵심 룰

- **QA 단독 owner**: 시트 생성·수정 책임은 QA (정정 6차)
- **개발자 권한 = editor**: 검수·댓글 가능. 권한 변경 X (소유권 이전 X)
- **markdown SoT 임시**: 이행 후 markdown 5개는 archive (Sheets가 SoT)
- **이행 정합성**: markdown 행 수 ↔ Sheets 행 수 일치 검증. 불일치 시 scout-log 경고
- **02_변경이력 갱신**: 이행 시점 + QA ID 행 추가 (markdown V0.1 → Sheets V0.1+이행)
- **디자인 결정론**: design-tokens.json·sheets-layout.json·apply.py 변경 시 spec 변경 이력 추가 필수

## 디자인 표준 자산

- 토큰: `{PLUGIN_ROOT}/templates/feature-spec-design/design-tokens.json` (색·폰트·행 높이·보더·표준 컬럼명별 너비 매핑)
- 레이아웃: `{PLUGIN_ROOT}/templates/feature-spec-design/sheets-layout.json` (6시트 구조·헤더 텍스트)
- 적용: `{PLUGIN_ROOT}/scripts/feature-spec-design/apply.py` (payload 생성)
- 검증: `{PLUGIN_ROOT}/scripts/feature-spec-design/verify.py` (token 일치성)
- spec: `docs/specs/2026-05-13-feature-spec-standard-design.md`

## 한계

- 옵션 B 사전 공유 시트 ID는 engagement-brief에서 받음. 양식이 v0.2.7 6시트와 호환되어야 (시트명·컬럼 수)
- 본 스킬은 markdown → Sheets 단방향. 역방향 동기화 X
- 받기 5종은 본 스킬 범위 외 (개발자 본인 관리)
- design 적용은 design_managed:true 시트 한정 (01_표지 자유 디자인 비대상)

## 참조

- spec (스킬): `docs/specs/2026-05-06-qa-scout-kit-v0.2-skeleton.md` §5-1 단계 17a
- spec (디자인): `docs/specs/2026-05-13-feature-spec-standard-design.md`
- scout 에이전트: `agents/scout.md`
- 관련 스킬: `skills/docs-to-function-spec/SKILL.md` (markdown 작성 — 본 스킬의 입력)
- 양식: `templates/feature-spec/*.md` (markdown 골격 5개)
- 디자인 자산: `templates/feature-spec-design/`·`scripts/feature-spec-design/`
