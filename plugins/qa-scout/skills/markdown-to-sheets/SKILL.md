---
name: markdown-to-sheets
description: 명인이 단계 17a에서 호출하는 스킬. 개발자가 인계한 feature-spec/ markdown 5개를 명인 본인 Google 계정의 Google Sheets 5시트로 자동 이행한다. google-sheets MCP 활용 — create_spreadsheet (옵션 A 신규) 또는 batch_update_cells (옵션 B 사전 공유 시트). feature-spec.yaml 메타 자동 생성 + share_spreadsheet로 개발자 editor 권한 부여 (단계 18c 검수 준비).
---

# markdown-to-sheets

scout v0.2 단계 17a (명인 측 markdown → Sheets 이행) 전용 스킬. 사용자 정정 6차로 신설 (개발자 MCP 인증 부담 해결).

## 사용 시점
명인이 단계 13~16 인계 패키지 수령 + 무결성 점검 통과 후 호출. 명인 PC의 google-sheets MCP는 명인 본인 OAuth 인증 필수.

## 입력
- 인계 패키지: `qa-handoff/{프로젝트명}/feature-spec/` markdown 5개
- engagement-brief 또는 사용자 입력:
  - `mode`: `new` (옵션 A 신규 생성) | `pre-shared` (옵션 B 사전 공유 시트)
  - `google_sheets_id`: pre-shared 모드일 때 사전 시트 ID (필수)
  - `developer_email`: 단계 18c 검수 권한 부여 대상

## 출력
- Google Sheets 5시트 채움 (01·04·06·07·08)
- `qa-handoff/{프로젝트명}/feature-spec.yaml` 작성 (URL·ID·owner·shared_with)
- `share_spreadsheet` 호출 → 개발자 editor 권한
- `scout-log.md` append

## 절차 (5단계)

### 1) 모드 결정 + Sheets 셋업

#### 옵션 A — 신규 생성
```python
# 명인 PC 명인 OAuth 인증 가정
sheet = create_spreadsheet(title="<프로젝트명> Feature Spec (qa-scout v0.2)")
sheets_id = sheet.id

# 5시트 생성 (Sheet1 → 01_표지로 rename + 4개 추가)
rename_sheet(sheets_id, sheet="Sheet1", new_name="01_표지")
create_sheet(sheets_id, title="04_변경이력")
create_sheet(sheets_id, title="06_기능정의서")
create_sheet(sheets_id, title="07_비기능요구")
create_sheet(sheets_id, title="08_사용자스토리")
```

#### 옵션 B — 사전 공유 시트
```python
# engagement-brief의 google_sheets_id 사용
sheets_id = engagement_brief["google_sheets_id"]
# 시트 5개 존재 확인 (없으면 create_sheet 추가)
```

### 2) markdown 파싱 + 시트별 데이터 추출

각 markdown frontmatter `sheet:` 필드로 대상 시트 식별:

| markdown | 대상 시트 | 파싱 방식 |
|---|---|---|
| `01_표지.md` | 01_표지 | 메타 표 → key-value 2컬럼 |
| `04_변경이력.md` | 04_변경이력 | 표 → 7컬럼 (버전·일자·변경자·유형·내용·영향 ID·승인자) |
| `06_기능정의서.md` | 06_기능정의서 | F-NNN 섹션별 17컬럼 행 추출 |
| `07_비기능요구.md` | 07_비기능요구 | 표 → 9컬럼 |
| `08_사용자스토리.md` | 08_사용자스토리 | 표 → 9컬럼 |

### 3) batch_update_cells 호출

각 시트에 헤더 + 본문 일괄 입력:
```python
batch_update_cells(
  spreadsheet_id=sheets_id,
  sheet="06_기능정의서",
  ranges={
    "A1:Q1": [[헤더 17컬럼]],
    "A2:Q22": [[FR-MYAPP-001 ~ 021 행]]  # 21행 × 17컬럼
  }
)
```

다른 4시트도 동일 패턴.

### 4) feature-spec.yaml 작성

```yaml
project: <project>
domain: <domain>
google_sheets_id: <sheets_id>
url: https://docs.google.com/spreadsheets/d/<sheets_id>/edit
sheets:
  - 01_표지
  - 04_변경이력
  - 06_기능정의서
  - 07_비기능요구
  - 08_사용자스토리
created_at: <ISO 8601>
last_updated: <ISO 8601>
owner: <명인 이메일>
shared_with:
  - email: <개발자 이메일>
    role: editor
    note: 단계 18c 검수 권한
mode: <new | pre-shared>
```

### 5) share_spreadsheet + scout-log append

```python
share_spreadsheet(
  spreadsheet_id=sheets_id,
  email_addresses=[developer_email],
  role="editor"
)
```

scout-log.md에 timestamp + 이행 결과 append (시트 URL·이행 행 수·공유 결과).

## 핵심 룰

- **명인 단독 owner**: 시트 생성·수정 책임은 명인 (정정 6차)
- **개발자 권한 = editor**: 검수·댓글 가능. 권한 변경 X (소유권 이전 X)
- **markdown SoT 임시**: 이행 후 markdown 5개는 archive (Sheets가 SoT)
- **이행 정합성**: markdown 행 수 ↔ Sheets 행 수 일치 검증. 불일치 시 scout-log 경고
- **04_변경이력 갱신**: 이행 시점 + 명인 ID 행 추가 (markdown V0.1 → Sheets V0.1+이행)

## 한계

- 옵션 B 사전 공유 시트 ID는 engagement-brief에서 받음. 양식이 v0.2 5시트와 호환되어야 (시트명·컬럼 수)
- 본 스킬은 markdown → Sheets 단방향. 역방향(Sheets → markdown) 동기화 X
- 받기 5종은 본 스킬 범위 외 (개발자 본인 관리 — 정정 5차·6차 정책)

## 참조

- spec: `docs/qa-scout/spec.md` §5-1 단계 17a
- scout 에이전트: `agents/scout.md`
- 관련 스킬: `skills/docs-to-function-spec/SKILL.md` (markdown 작성 — 본 스킬의 입력)
- 양식: `templates/feature-spec/*.md` (markdown 골격)
