---
name: markdown-to-sheets
description: 'QA가 단계 17a에서 호출하는 스킬. v0.3.1 단일 feature-spec.md markdown(§0~§8)을 Google Sheets로 자동 이행 + GxP 표준 디자인 결정론적 적용. 옵션 A(5시트 기본)/B(8시트)/C(1시트 03 단독)/D(1시트 15컬럼 — 인풋 출처 직접 매핑) 4종 분기. D-1·D-2·D-3 발행 게이트 — D-1(UTF-8 raw 한글 + 인라인 \uXXXX escape 금지) / D-2(apply-cells.py 헬퍼 경유) / D-3(readback diff 차단 게이트 — verify-readback.py exit 0 전까지 published=false, share·완료·handoff 차단). ui-menu-mindmap.md는 Sheets 이행 X. google-sheets MCP — create_spreadsheet/batch_update_cells/get_sheet_data. Auto-Healing Loop 차단 (bridge-wrapping-pattern 준수, 자동 정정 X).'
---

# markdown-to-sheets (v0.3.1)

scout v0.3.0 단계 17a (QA 측 markdown → Sheets 이행) 전용 스킬. v0.3.0에서 Sheets 옵션 A/B/C/D 4종 + D-3 readback diff 차단 게이트 추가 (SDD `../../docs/qa-scout/spec.md` §4-3·§4-4).

## v0.3.0 변경 (SDD §4-3·§4-4)

- **옵션 D 신설** (§4-4): 15컬럼 layout (No. + spec 1~13 + 인풋 출처). 인풋 출처를 Sheets 인풋 출처 컬럼으로 직접 매핑 — GxP 추적성 강화. 옵션 A/B/C 호환 유지 (비고에 evidence 표기로 매립)
- **D-1·D-2 보조 개선** (§4-3): 인라인 JSON `\uXXXX` escape 한글 직접 작성 금지. **UTF-8 raw 한글** + `apply-cells.py` 헬퍼 경유로 MCP `batch_update_cells` 호출
- **D-3 차단 게이트 신설** (§4-3): 발행 직후 즉시 `get_sheet_data` 재조회 + `verify-readback.py` (NFC 정규화 + exact cardinality + source 일관성 + cell-by-cell diff). **diff 0건 전 published=false 유지, share_spreadsheet 금지, scout-log entry 미작성, handoff 차단**
- **sheets-layout.json v3.0 호환** (§4-4-2): top-level `sheets[]` 구조 유지 + `visible_in[]` + `headers_by_option` + `column_widths_by_option` 옵션 분기. apply.py `--sheets-option <A|B|C|D>` 인자 활용
- **Auto-Healing Loop 차단** (`bridge-wrapping-pattern` 메모리): D-3 diff 자동 정정 금지 — QA 승인 후 D-1/D-2 경로 재시도

## v0.2.9와의 차이 (호환성)

v0.2.9 sheets-layout.json (v1.0) 인스턴스는 신규 필드 부재 상태로도 유효 — apply.py `--sheets-option` 미지정 시 v1.0 동일 동작 (fallback `headers`·`column_widths` 사용). v0.3.0 신규 옵션 D는 사용자 명시 선택 시만 사용.

v0.2.7 갱신 (2026-05-13) 유지: GxP 표준 디자인 결정론적 적용 단계. 디자인 spec: `../../docs/qa-scout/spec.md`.

## 사용 시점
QA가 단계 13~16 인계 패키지 수령 + 무결성 점검(`scripts/validate-package.py`) PASS 후 호출. QA PC의 google-sheets MCP는 QA 본인 OAuth 인증 필수.

## 입력
- 인계 패키지: `qa-handoff/{프로젝트명}/feature-spec.md` 단일 markdown (§0~§8 9섹션)
  - **`ui-menu-mindmap.md`는 Sheets 이행 X — 본 스킬 입력에서 제외** (SDD §5-5)
- `developer_email` 입력 우선순위:
  1. `qa-handoff/{프로젝트명}/input-manifest.yaml > contact.developer_email` (단계 11b 자동 수집 — 권장)
  2. engagement-brief의 `google_sheets_id` / 이메일
  3. 사용자 인터랙티브 입력 (1·2 모두 부재 시)
- `mode`: `new` (옵션 A 기본 — 신규 생성) | `pre-shared` (사전 공유 시트)
- `google_sheets_id`: `pre-shared` 모드일 때 사전 시트 ID (필수)
- `sheets_option`: **`A` (기본, 5시트) | `B` (8시트, §4·§5·§6 포함) | `C` (1시트 최소) | `D` (1시트 15컬럼, 인풋 출처 직접 매핑 — v0.3.0 신규)** — 단계 17a 입력
- `include_optional`: 06_18c_개발팀_질의 시트 포함 여부 (선택, 기본 false — 옵션 A/B 시만 적용. 옵션 C·D는 03 단독이라 미지원)

## 출력
- Google Sheets 시트 채움 + 표준 디자인 적용 (옵션별 시트 수 변동)
- `qa-handoff/{프로젝트명}/feature-spec.yaml` 작성 (URL·ID·owner·shared_with·sheets_option·sheets[] + **published 상태**)
- `feature-spec.md` frontmatter `linked_artifacts.sheets_url` 업데이트 (D-3 게이트 PASS 후만)
- `share_spreadsheet` 호출 → 개발자 editor 권한 (**D-3 게이트 PASS 후만**)
- `scout-log.md` append (이행 행 수·디자인 PASS·옵션·공유 결과·D-3 diff 결과) — **D-3 PASS 후만 entry 작성**

## v0.3.0 발행 게이트 (D-1·D-2·D-3) — §4-3

### D-1 (보조 개선) — UTF-8 raw 한글 강제

- 인라인 JSON `\uXXXX` escape를 통한 한글 cell 직접 작성 **금지**
- 한글 cell 값은 로컬 JSON 파일에 UTF-8 raw로 저장 후 본 스킬이 읽기
- 메인 Claude·QA가 batch_update_cells MCP 호출에 한글 escape 작성 X

### D-2 (보조 개선) — apply-cells.py 헬퍼 경유

```bash
python plugins/qa-scout/scripts/markdown-to-sheets/apply-cells.py \
    --spreadsheet-id <ID> \
    --sheet "03_기능정의서" \
    --source-json section1_rows.json \
    --sheets-option <A|B|C|D> \
    --start-row 2 \
    --compact > batch_payload.json
```

- source JSON: `{"rows": [["<cell1>", "<cell2>", ...], ...]}` (UTF-8 raw 한글)
- col count 정합 검증 자동 (옵션 D=15, A/B/C=14)
- stdout JSON을 google-sheets MCP `batch_update_cells`에 전달

### D-3 (차단 게이트) — Readback Diff

**발행 직후 즉시 실행**:

```bash
# 1. MCP get_sheet_data 호출 → sheet_data.json dump
mcp__google-sheets__get_sheet_data --spreadsheet-id <ID> --sheet "03_기능정의서" --range "A1:<last>"
# (Claude/호출자가 결과를 sheet_data.json으로 저장)

# 2. verify-readback.py 실행
python plugins/qa-scout/scripts/markdown-to-sheets/verify-readback.py \
    --source-json section1_rows.json \
    --sheet-data-json sheet_data.json \
    --sheets-option <A|B|C|D> \
    --report-json readback_report.json
```

**exit code 처리**:
- `exit 0` (PASS, diff 0건) → feature-spec.yaml `published=true` + `share_spreadsheet` 호출 + scout-log entry append
- `exit 1` (FAIL) → feature-spec.yaml `published=false` 유지 + share_spreadsheet 금지 + scout-log entry 미작성 + QA에게 readback_report.json 보고
- `exit 2` (ERROR) — 인자 오류·파일 부재 → 게이트 재실행 필요

**검증 항목** (§4-3-1):
- sheets_option ↔ src_col_count 정합 (D=15, A/B/C=14)
- source rows 일관성 (모든 row col count 동일)
- 시트 row 수 == header + data rows (exact match)
- 각 row col 수 == src_col_count (exact match)
- NFC 정규화 후 cell raw string 비교

**FAIL 시 처리 워크플로** (§4-3-5):
1. QA 보고 (readback_report.json 첨부)
2. QA 승인 후 D-1/D-2 경로로 재호출
3. D-3 재실행 → PASS 시 발행 완료 / FAIL 시 QA 재보고 (사이클 반복)
4. **자동 정정 금지** (Auto-Healing Loop 차단, `bridge-wrapping-pattern` 메모리 준수)

## 절차 (7단계)

### 1) 모드 + 옵션 결정 + Sheets 셋업

#### 옵션 결정 가이드 (SDD §5-5)
| 옵션 | 시트 수 | 포함 시트 | 사용 시점 |
|---|---|---|---|
| **A (기본, 권장)** | 4 | 01_표지·02_변경이력·03_기능정의서·04_TestCase | 표준 발행. §2·§3·§4·§5·§6은 markdown 본문에만 (Sheets 정형 데이터 한정) |
| **B** | 7 | A + 06_권한매트릭스·07_상태전이·08_용어집 | §4·§5·§6도 Sheets 정형화 필요한 경우 (감사·검수자 요청 시) |
| **C** | 1 | 03_기능정의서 단일 (14 컬럼) | 최소 발행 — 검수 비용 최소화, 다른 섹션은 markdown 본문으로만 |
| **D (v0.3.0 신규)** | 1 | 03_기능정의서 단일 (15 컬럼, 인풋 출처 직접 매핑) | GxP 추적성 강화 발행 — 인풋 출처를 sheet 인풋 출처 컬럼으로 직접 이행 |

기본값은 옵션 A. 단계 17a 인터뷰에서 사용자 명시 입력으로 옵션 선택.

#### 옵션 A — 신규 생성 (mode=new)
```python
sheet = create_spreadsheet(title="<프로젝트명> Feature Spec (qa-scout v0.2.9)")
sheets_id = sheet.id
```

신규 시트 생성은 절차 4 디자인 적용 단계에서 `apply.py --stage add` payload 호출로 일괄 처리. 본 단계엔 spreadsheet만 생성.

#### 옵션 B — 사전 공유 시트 (mode=pre-shared)
```python
sheets_id = engagement_brief["google_sheets_id"]
```

기존 시트 매핑은 `list_sheets`로 확인 후 절차 4에 전달. 사전 시트가 옵션 A/B/C 양식과 호환되는지 검증 (시트명·컬럼 수).

### 2) 단일 markdown 파싱 → 섹션별 데이터 추출

`feature-spec.md`의 frontmatter + §0~§8 9섹션을 한 번에 파싱하고 시트 옵션에 따라 매핑한다.

| feature-spec.md 섹션 | 옵션 A 시트 | 옵션 B 시트 | 옵션 C 시트 | **옵션 D 시트** (v0.3.0 신규) |
|---|---|---|---|---|
| frontmatter `linked_artifacts` / `execution_policy` | (참조만, Sheets 직접 매핑 X) | 동일 | 동일 | 동일 |
| §0 표지 (메타 14항목 + execution gate 3행) | 01_표지 | 01_표지 | 이행 X | 이행 X |
| §1 기능 행 (14컬럼) | **03_기능정의서** (본체) | 03_기능정의서 | **03_기능정의서** (단일 14컬럼) | **03_기능정의서** (단일 15컬럼) |
| §1 TC 취합 (04_TestCase) | **04_TestCase** | **04_TestCase** | **04_TestCase** | **04_TestCase** |
| §2 비기능 요구 | **이행 X** (markdown SoT) | **이행 X** (markdown SoT) | 이행 X | 이행 X |
| §3 사용자 스토리 | **이행 X** (markdown SoT) | **이행 X** (markdown SoT) | 이행 X | 이행 X |
| §4 권한 매트릭스 | **이행 X** (markdown SoT) | **06_권한매트릭스** | 이행 X | **이행 X** (markdown SoT) |
| §5 상태 전이 요약 | **이행 X** (markdown SoT) | **07_상태전이** | 이행 X | **이행 X** (markdown SoT) |
| §6 용어집 | **이행 X** (markdown SoT) | **08_용어집** | 이행 X | **이행 X** (markdown SoT) |
| §7 변경 이력 | 02_변경이력 | 02_변경이력 | 이행 X | 이행 X |
| §8 마인드맵 대조 결과 | **이행 X** (markdown SoT) | **이행 X** (markdown SoT) | **이행 X** (markdown SoT) | **이행 X** (markdown SoT) |
| §1 인풋 출처 (비고 embedded) | **이행 X** (markdown SoT — 비고 evidence 표기로 매립) | **이행 X** (markdown SoT) | **이행 X** (markdown SoT — 비고 evidence 표기로 매립) | **인풋 출처 컬럼 직접 매핑** (§4-4-1 정합) |

`§8 cross-check` 결과는 어느 옵션에서도 Sheets에 이행하지 않는다 — 단계 9d.5 cross-check 게이트 결과는 markdown SoT 유지.

#### 2-1. frontmatter 검증
- `execution_policy.decision` 등 5필드가 채워져 있는지 확인 (manifest `execution_gate:` 동기 상태)
- `linked_artifacts.ui_menu_mindmap` 존재 (마인드맵은 Sheets 이행 X지만 링크는 feature-spec.yaml에 기록)
- `sheets_mapping.primary_sheet` = `03_기능정의서` 고정
- 위반 시 본 스킬 중단 + scout-log에 사유 기록 (자동 보정 X — `feedback_bridge_wrapping_pattern`)

#### 2-2. 섹션 파싱
- §0 표지 표 → key-value 2컬럼 (옵션 A/B 시 01_표지에 매핑)
- §1 F-NNN 섹션별 14컬럼 행 추출 (정렬·결번 그대로)
- §2/§3 9컬럼 표 → 그대로 변환
- §4 권한 매트릭스 (옵션 B만) → role × FR × {visible, edit, ...} 매트릭스 변환
- §5 상태 전이 (옵션 B만) → 상태 × 허용 행위 × 발화 조건 × 다음 상태 × 관련 FR 5컬럼
- §6 용어집 (옵션 B만) → 용어·정의·동의어·영문·출처 5컬럼
- §7 변경 이력 → 7컬럼 (버전·일자·변경자·유형·내용·영향 ID·승인자)

### 3) §8 cross-check 결과 무이행 검증

§8은 단계 9d.5 cross-check 게이트 결과 (PASS / PASS_WITH_NOTES / FAIL / NOT_RUN) 기록 위치이며 markdown SoT 유지. 본 스킬은 다음 검증만 수행:

- `feature-spec.md` §8 섹션 존재 확인 (없으면 단계 9c 미완료 — 본 스킬 중단)
- §8의 cross-check `result` enum이 4종 중 하나인지 확인 (NOT_RUN이면 단계 17a 진입 가능하지만 단계 9d.5 미실행 경고)
- §8 본문은 Sheets에 매핑 X (옵션 무관)

### 4) 표준 디자인 적용 (Stage 1 — addSheet)

`{PLUGIN_ROOT}/scripts/feature-spec-design/apply.py` 호출로 batch_update payload 생성 → MCP `batch_update` 호출.

```bash
python {PLUGIN_ROOT}/scripts/feature-spec-design/apply.py \
    --spreadsheet-id <sheets_id> \
    --stage add \
    --sheets-option <A | B | C | D> \
    --existing-sheets-json '<{title:sheetId} JSON>' \
    [--include-optional]
```

옵션별 시트 생성 수:
- 옵션 A: 4시트 (01_표지·02_변경이력·03_기능정의서·04_TestCase)
- 옵션 B: 7시트 (A + 06_권한매트릭스·07_상태전이·08_용어집)
- 옵션 C: 1시트 14 컬럼 (`include-optional` 무시)
- **옵션 D**: 1시트 15 컬럼 (03_기능정의서 단독, `include-optional` 무시)

stdout JSON의 `requests` 배열을 `mcp__google-sheets__batch_update`에 전달. 생성 완료 후 `list_sheets` 재호출하여 sheetId 매핑 갱신.

> apply.py가 옵션 B의 06_권한매트릭스·07_상태전이·08_용어집 디자인 layout을 지원하지 않으면 본 스킬 패치 후 apply.py 보강 필요 (별도 task — 본 SDD 범위 외 / dogfood 시 발견 시 처리).

### 5) 표준 디자인 적용 (Stage 2 — design)

각 design_managed 시트별로 design payload 생성 + 적용:

```bash
python {PLUGIN_ROOT}/scripts/feature-spec-design/apply.py \
    --spreadsheet-id <sheets_id> \
    --stage design \
    --sheets-option <A | B | C | D> \
    --existing-sheets-json '<갱신 매핑>' \
    --sheet-title <시트명> \
    --compact
```

각 시트별로 MCP `batch_update` 호출 (사이즈 분할 — 03 14컬럼은 단일 호출이 큼, memory `feedback_mcp_payload_size_split` 참조). 결과: 헤더 텍스트·색·폰트·행 높이·컬럼 너비·보더·frozenRowCount 결정론적 적용.

> 동일 텍스트 통일 룰(`design-tokens.json > column_widths_by_name`)로 시트 간 동일 헤더는 동일 너비.

### 5-1) column_validation 적용 (테스트 결과 드롭다운 + 조건부 서식)

`sheets-layout.json > sheets[].column_validation` 정의를 기반으로 `테스트 결과` 컬럼에 드롭다운 + 조건부 서식 적용. 시트 생성(step 4) + 디자인(step 5) 직후, 데이터 입력(step 6) 이전에 실행.

적용 대상: `design_managed: true` + `column_validation` 정의 보유 시트 (`03_기능정의서`, `04_TestCase`).

```python
# 예시 — 03_기능정의서 테스트 결과 컬럼 (headers 내 index=12 → col M)
batch_update(spreadsheet_id=sheets_id, requests=[
  # 1. 드롭다운 setDataValidation (row 2 이하 전체)
  {"setDataValidation": {
    "range": {"sheetId": sheet_id, "startRowIndex": 1, "startColumnIndex": 12, "endColumnIndex": 13},
    "rule": {
      "condition": {"type": "ONE_OF_LIST", "values": [
        {"userEnteredValue": "PASS"}, {"userEnteredValue": "FAIL"}, {"userEnteredValue": "N/A"}
      ]},
      "showCustomUi": True, "strict": False
    }
  }},
  # 2a. 조건부 서식 — PASS (진한 초록 R:0 G:0.38 B:0)
  {"addConditionalFormatRule": {
    "rule": {
      "ranges": [{"sheetId": sheet_id, "startRowIndex": 1, "startColumnIndex": 12, "endColumnIndex": 13}],
      "booleanRule": {
        "condition": {"type": "TEXT_EQ", "values": [{"userEnteredValue": "PASS"}]},
        "format": {"backgroundColor": {"red": 0, "green": 0.38, "blue": 0}}
      }
    }, "index": 0
  }},
  # 2b. 조건부 서식 — FAIL (진한 빨강 R:0.753 G:0 B:0)
  {"addConditionalFormatRule": {
    "rule": {
      "ranges": [{"sheetId": sheet_id, "startRowIndex": 1, "startColumnIndex": 12, "endColumnIndex": 13}],
      "booleanRule": {
        "condition": {"type": "TEXT_EQ", "values": [{"userEnteredValue": "FAIL"}]},
        "format": {"backgroundColor": {"red": 0.753, "green": 0, "blue": 0}}
      }
    }, "index": 1
  }},
  # 2c. 조건부 서식 — N/A (하늘색 R:0.741 G:0.843 B:0.933)
  {"addConditionalFormatRule": {
    "rule": {
      "ranges": [{"sheetId": sheet_id, "startRowIndex": 1, "startColumnIndex": 12, "endColumnIndex": 13}],
      "booleanRule": {
        "condition": {"type": "TEXT_EQ", "values": [{"userEnteredValue": "N/A"}]},
        "format": {"backgroundColor": {"red": 0.741, "green": 0.843, "blue": 0.933}}
      }
    }, "index": 2
  }}
])
```

**col index 결정 룰**:
- `03_기능정의서` — `headers_by_option[option]`에서 `테스트 결과` 위치 (0-based). 옵션 A/B/C/D 모두 index=12 (col M).
- `04_TestCase` — `headers`에서 `테스트 결과` 위치 = index=10 (col K). 동일 4 requests 적용, `startColumnIndex: 10, endColumnIndex: 11`.
- `endRowIndex` 생략 시 해당 열 전체 적용 → 신규 행 추가 시 드롭다운 자동 상속.

### 6) markdown 본문 데이터 입력

각 design_managed 시트의 row 2 이하에 §섹션 행 데이터 입력. 옵션별 시트당 호출 분리.

**v0.3.0 권장 경로** — `apply-cells.py` 헬퍼 (§D-2):

```bash
python {PLUGIN_ROOT}/scripts/markdown-to-sheets/apply-cells.py \
    --spreadsheet-id <sheets_id> \
    --sheet "03_기능정의서" \
    --source-json section1_rows.json \
    --sheets-option <A|B|C|D> \
    --start-row 2 \
    --compact > batch_payload.json
```

생성된 payload를 google-sheets MCP `batch_update_cells`에 전달. 인라인 JSON `\\uXXXX` escape 한글 직접 작성 금지 (D-1 보조 개선).

호출 예시:

```python
# 옵션 A 예시 (03_기능정의서 — §1 14컬럼)
batch_update_cells(
  spreadsheet_id=sheets_id,
  sheet="03_기능정의서",
  ranges={"A2:N22": [[FR-<PROJECT>-001~021 행]]}  # 21행 × 14컬럼
)

# 옵션 B 추가 — 06_권한매트릭스 (§4)
batch_update_cells(
  spreadsheet_id=sheets_id,
  sheet="06_권한매트릭스",
  ranges={"A2:H10": [[role × FR × action 매트릭스]]}
)

# 옵션 D 예시 (03_기능정의서 — §1 15컬럼, 인풋 출처 14번 컬럼 포함, v0.3.1)
batch_update_cells(
  spreadsheet_id=sheets_id,
  sheet="03_기능정의서",
  ranges={"A2:O63": [[FR-<PROJECT>-001~062 행 × 15컬럼]]}  # 62행 × 15컬럼
)
```

01_표지는 자유 디자인 — markdown 표 그대로 매핑(키-값 2컬럼). 옵션 C·D는 03_기능정의서만 채움 (C=14컬럼, D=15컬럼).

### 6-1. v0.3.0 신규 — D-3 Readback Diff 차단 게이트 (§4-3-1)

위 6단계 batch_update_cells 호출 직후 즉시 D-3 게이트 실행:

```bash
# 1. MCP get_sheet_data 호출 후 결과를 sheet_data.json으로 dump (Claude/호출자 처리)
# 2. verify-readback.py 실행
python {PLUGIN_ROOT}/scripts/markdown-to-sheets/verify-readback.py \
    --source-json section1_rows.json \
    --sheet-data-json sheet_data.json \
    --sheets-option <A|B|C|D> \
    --report-json readback_report.json
```

**exit code 분기**:
- `exit 0` (diff 0건) → 절차 7 진입 (published=true + share + scout-log)
- `exit 1` (FAIL) → **절차 7 진입 차단**. feature-spec.yaml published=false 유지 + share_spreadsheet 금지 + scout-log entry 미작성 + QA에게 readback_report.json 보고
- `exit 2` (ERROR) — 인자 오류·file 부재 → 게이트 재실행

### 7) feature-spec.yaml + share + frontmatter sheets_url 갱신 + scout-log

**전제 조건 (v0.3.0)**: 절차 6-1 D-3 readback diff 게이트 `exit 0` PASS 후에만 본 단계 진입 가능. D-3 FAIL 시 본 단계 전체 차단 ([[bridge-wrapping-pattern]] 메모리 준수).

```yaml
project: <project>
google_sheets_id: <sheets_id>
url: https://docs.google.com/spreadsheets/d/<sheets_id>/edit
schema_version: "0.3.0"
sheets_option: <A | B | C | D>
published: true                                  # v0.3.0 신규 — D-3 PASS 후 true 마킹
published_at: <ISO 8601>                          # v0.3.0 신규
design:
  spec: SPEC-2026-05-22-qa-scout-v3-0-coverage-completeness-gate
  applied_at: <ISO 8601>
readback_gate:                                    # v0.3.0 신규
  executed_at: <ISO 8601>
  result: PASS                                    # PASS | FAIL (FAIL 시 published=false 유지, 본 yaml 미작성)
  diff_count: 0
  report_path: <qa-handoff/{project}/readback_report.json>
sheets:
  # 옵션별 동적 구성 — 옵션 A 4시트 예시
  - 01_표지
  - 02_변경이력
  - 03_기능정의서
  - 04_TestCase
  # 옵션 B 추가: 06_권한매트릭스 · 07_상태전이 · 08_용어집 (총 7시트)
  # 옵션 C는 03_기능정의서 단일 (14컬럼)
  # 옵션 D는 03_기능정의서 단일 (15컬럼, 인풋 출처 14번 매핑)
excluded_from_sheets:
  - feature-spec.md §8 (cross-check 결과 — markdown SoT)
  - ui-menu-mindmap.md 전체 (Sheets 이행 X — SDD §5-5)
linked_artifacts:
  feature_spec_md: feature-spec.md
  ui_menu_mindmap_md: ui-menu-mindmap.md
owner: <QA 이메일>
shared_with:
  - email: <개발자 이메일>
    role: editor
mode: <new | pre-shared>
```

```python
# D-3 PASS 후에만 호출 (v0.3.0)
share_spreadsheet(spreadsheet_id=sheets_id, email_addresses=[developer_email], role="editor")
```

`feature-spec.md` frontmatter 갱신 (D-3 PASS 후):
- `linked_artifacts.sheets_url`: `null` → 본 단계에서 작성한 URL
- `last_updated`: 본 단계 ISO 8601
- (옵션 B의 경우) `sheets_mapping.side_sheets`에 `06_권한매트릭스`/`07_상태전이`/`08_용어집` 추가
- (옵션 D의 경우) `sheets_mapping.input_source_column_published: true` 추가
- `sheets_mapping.excluded_from_sheets`에서 본 옵션에서 이행된 항목 제거

scout-log.md append (timestamp + 이행 시트 수 + 행 수 + 디자인 PASS 여부 + 공유 결과 + 옵션 + cross-check 결과 enum + **D-3 readback diff_count + report_path**) — D-3 PASS 후만 entry 작성.

## 핵심 룰

- **QA 단독 owner**: 시트 생성·수정 책임은 QA
- **개발자 권한 = editor**: 검수·댓글 가능. 권한 변경 X (소유권 이전 X)
- **markdown SoT**: 이행 후에도 `feature-spec.md`는 SoT — Sheets는 사람 검수용 발행본. 본문 분기(§4·§5·§6·§8) 또는 옵션 C의 §0/§2/§3/§7도 markdown SoT
- **이행 정합성**: markdown 행 수 ↔ Sheets 행 수 일치 검증. 불일치 시 scout-log 경고 (자동 보정 X)
- **§7 변경이력 갱신**: 이행 시점 + QA ID + 옵션 행 추가 (`Sheets 이행 옵션 <A|B|C> 적용`)
- **디자인 결정론**: design-tokens.json·sheets-layout.json·apply.py 변경 시 spec 변경 이력 추가 필수
- **§8 cross-check 결과 Sheets 이행 금지**: markdown SoT 유지 (SDD §5-5·§5-9)
- **`ui-menu-mindmap.md` Sheets 이행 금지**: markdown 보조 산출물 유지 (SDD §5-5)
- **execution_policy frontmatter Sheets 이행 금지**: §0 표지 14항목 표에 통합된 3행(decision·reviewer_status·environment_class)만 Sheets에 반영, manifest SoT는 그대로

## 옵션 분기 자가 검증 체크리스트

옵션 A (4시트):
- [ ] 01_표지·02_변경이력·03_기능정의서·04_TestCase 4시트 생성
- [ ] §2·§3·§4·§5·§6·§8 시트 미생성 (markdown SoT)
- [ ] feature-spec.yaml `excluded_from_sheets`에 §2·§3·§4·§5·§6·§8·마인드맵 명시

옵션 B (7시트):
- [ ] 옵션 A 4시트 + 06_권한매트릭스·07_상태전이·08_용어집 추가
- [ ] §8 시트 미생성 (cross-check 결과는 markdown SoT)
- [ ] 06/07/08 디자인 layout이 design-tokens.json + sheets-layout.json에 정의되어 있는지 사전 검증 — 부재 시 본 스킬 중단

옵션 C (1시트):
- [ ] 03_기능정의서 단일 시트만 생성 (04_TestCase 미생성 — 최소 발행)
- [ ] §0·§2·§3·§4·§5·§6·§7·§8 시트 미생성
- [ ] feature-spec.yaml `excluded_from_sheets`에 §0·§2·§3·§4·§5·§6·§7·§8·마인드맵 모두 명시

옵션 D (1시트 15컬럼, v0.3.0 신규):
- [ ] 03_기능정의서 단일 시트만 생성 (15컬럼)
- [ ] 03_기능정의서 14번 컬럼 (인풋 출처) 값이 비고의 evidence 표기에서 직접 매핑 (markdown SoT 동시 유지)
- [ ] §0·§2·§3·§4·§5·§6·§7·§8 시트 미생성 (markdown SoT)
- [ ] feature-spec.yaml `excluded_from_sheets`에 §0·§2·§3·§4·§5·§6·§7·§8·마인드맵 모두 명시
- [ ] feature-spec.yaml `sheets_mapping.input_source_column_published: true` 마킹

공통 (v0.3.0):
- [ ] `feature-spec.md` §8 cross-check 결과 enum 확인 (`PASS | PASS_WITH_NOTES | FAIL | NOT_RUN`) — NOT_RUN이면 경고 + 진행
- [ ] `ui-menu-mindmap.md` Sheets 이행 0건
- [ ] **step 5-1 column_validation 적용** (테스트 결과 드롭다운 PASS/FAIL/N/A + 조건부 서식 — sheets-layout.json `column_validation` 정의 기반, 03_기능정의서 + 04_TestCase 양쪽)
- [ ] **D-3 readback diff `exit 0`** (`verify-readback.py`) — diff 0건 전 published=false / share·완료·handoff 차단 (§4-3-2)
- [ ] D-1 인라인 \uXXXX escape 금지 준수 (UTF-8 raw 한글 source JSON 경유)
- [ ] D-2 apply-cells.py 헬퍼 사용 (col count 정합 검증 포함)
- [ ] frontmatter `execution_policy:` 5필드 채워진 상태에서만 진행 (placeholder 잔존 시 중단)
- [ ] `feature-spec.md` frontmatter `sheets_url` 갱신
- [ ] 개발자 editor 권한 부여 완료
- [ ] scout-log.md entry append

## 디자인 표준 자산

- 토큰: `{PLUGIN_ROOT}/templates/feature-spec-design/design-tokens.json` (색·폰트·행 높이·보더·표준 컬럼명별 너비 매핑)
- 레이아웃: `{PLUGIN_ROOT}/templates/feature-spec-design/sheets-layout.json` (시트 구조·헤더 텍스트)
- 적용: `{PLUGIN_ROOT}/scripts/feature-spec-design/apply.py` (payload 생성, `--sheets-option` 분기 지원 필요 — 추가 보강 시 별도 task)
- 검증: `{PLUGIN_ROOT}/scripts/feature-spec-design/verify.py` (token 일치성)
- spec: `../../docs/qa-scout/spec.md`

## 한계

- 옵션 B 사전 공유 시트 ID는 engagement-brief에서 받음. 양식이 v0.2.9 8시트와 호환되어야 (시트명·컬럼 수)
- 본 스킬은 markdown → Sheets 단방향. 역방향 동기화 X
- 받기 5종(domain-knowledge/)은 본 스킬 범위 외 — feature-spec.md §4/§5/§6에 흡수된 요약만 Sheets로 이행 (옵션 B)
- design 적용은 design_managed:true 시트 한정 (01_표지 자유 디자인 비대상)
- 옵션 B의 06_권한매트릭스·07_상태전이·08_용어집 디자인 layout이 design-tokens.json에 미정의된 경우 본 스킬은 옵션 B 진입 차단 (자동 fallback 금지)
- 단계 9d.5 cross-check 게이트 미실행 (`NOT_RUN`) 상태에서도 단계 17a 진입은 가능하지만 scout-log 경고 + Sheets 발행 후 단계 17b reviewer 검수 시 보강 권고

## 참조

- spec (v0.2.9): `../../docs/qa-scout/spec.md` §5-5 Sheets 이행 정책 · §5-1-1 feature-spec.md 구조
- spec (디자인): `../../docs/qa-scout/spec.md`
- spec (v0.2 base): `../../docs/qa-scout/spec.md` §5-1 단계 17a
- scout 에이전트: `agents/scout.md` 단계 17a
- 선행 스킬: `skills/docs-to-function-spec/SKILL.md` (feature-spec.md 작성 — 본 스킬의 입력)
- 양식: `templates/feature-spec.md` (단일 markdown 골격) · `templates/ui-menu-mindmap.md` (Sheets 미이행)
- 디자인 자산: `templates/feature-spec-design/`·`scripts/feature-spec-design/`
- manifest 슬롯: `templates/input-manifest.yaml > execution_gate:` / `playwright_verification:` / `final_artifacts:` / `two_doc_cross_check:`

## 변경 이력 (스킬 자체)

| 버전 | 일자 | 변경 |
|---|---|---|
| 0.2 | 2026-05-13 | GxP 표준 디자인 결정론적 적용 단계 추가. 시트 번호 체계 dogfood 프로젝트 v0.2.6.2 양식 채택. spec: ../../docs/qa-scout/spec.md |
| 0.2.9 | 2026-05-21 | 단일 `feature-spec.md` 입력으로 전환 (5 md → 1 md) + 옵션 A/B/C 3종 분기 추가 (5시트 / 8시트 / 1시트). §4·§5·§6·§8 markdown SoT 유지 정책 명시. `ui-menu-mindmap.md` Sheets 이행 금지 명시. apply.py `--sheets-option` 분기 지원 요구 명시. spec: ../../docs/qa-scout/spec.md §5-5 |
| 0.3.0 | 2026-05-23 | 옵션 D 신설 (19컬럼, 인풋 출처 직접 매핑 — GxP 추적성 강화). D-1·D-2·D-3 발행 게이트 신설: D-1(UTF-8 raw 한글 + 인라인 escape 금지) + D-2(apply-cells.py 헬퍼) + D-3(verify-readback.py readback diff 차단 게이트 — exit code 0 전까지 published=false, share·완료·handoff 차단). sheets-layout.json v3.0 호환 (top-level sheets[] + visible_in + headers_by_option + column_widths_by_option). Auto-Healing Loop 차단 (자동 정정 X). spec: ../../docs/qa-scout/spec.md §4-3·§4-4 |
| 0.3.1 | 2026-05-26 | 팀장 피드백 반영 — (1) TC ID 컬럼 신설 + 테스트 결과 드롭다운(PASS/FAIL/N/A) 컬럼 재편. A/B/C=18컬럼·D=19컬럼으로 col count 전면 갱신. (2) 04_비기능요구·05_사용자스토리·06_18c_개발팀_질의 시트 삭제 + 04_TestCase(모든 옵션 공통) 신규 추가. 옵션 A=4시트·B=7시트로 갱신. (3) column_validation spec을 sheets-layout.json에 추가. step 5-1 신설 (테스트 결과 드롭다운 + 조건부 서식 적용 절차). 옵션 D 인풋 출처 col 17→18번으로 정정. apply-cells.py·verify-readback.py expected_col_count P0 정정. |
