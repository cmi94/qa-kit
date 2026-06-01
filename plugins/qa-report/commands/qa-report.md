---
description: N차 통합테스트 결과 보고서(.xlsx) 자동 생성 — 입력 5개 강제 수집 + Jira fetch + 결정론적 렌더
---

# /qa-report

차수별 통합테스트 결과서를 양식 고정·데이터만 채우는 방식으로 생성한다. 생성 본체는
`${CLAUDE_PLUGIN_ROOT}/scripts/build_report.py`(결정론적 렌더러)가 수행하고, 이 커맨드는
**입력 강제 수집 → Jira fetch → 집계 → 페이로드 작성 → 스크립트 실행**만 오케스트레이션한다.

> 셀을 직접 손으로 채우지 말 것. 반드시 build_report.py에 페이로드를 넘겨 렌더한다(동일 퀄리티 보장).

## 0. 전제 검사
- Atlassian(Jira) MCP 커넥터가 연결돼 있어야 한다. 없으면 안내하고 중단.
- Python 3 + openpyxl 필요. 없으면 `pip install openpyxl` 안내.

## 1. 입력 강제 수집 (AskUserQuestion — hard gate)
한 번의 AskUserQuestion으로 아래를 모두 받는다(누락 시 진행 불가):
1. **솔루션명** (예: MYAPP)
2. **Jira 프로젝트 키** (예: MYAPP)
3. **QA 일정** — 기간 시작·종료 (YYYY-MM-DD ~ YYYY-MM-DD)
4. **이전 차수 결과 파일 경로** — 1차면 "없음"
5. **출력 폴더 경로**

추가(선택): Build Ver., 결함 원인 유형 커스텀필드명(기본값 `결함 원인 유형`).

## 2. 회차 자동 감지
- 이전 파일 있으면: `python ${CLAUDE_PLUGIN_ROOT}/scripts/read_meta.py "<이전파일>"` 실행 → JSON.
  - `round`(=M) → 이번 차수 **N = M + 1**. `trend` 배열(이전 회차들 행) 확보.
  - `round`=0(메타 없음/빈 템플릿) → N = 1.
- 이전 파일 "없음" → N = 1, trend = [].

## 3. Jira fetch (Atlassian MCP — 단일 all-time 쿼리)
JQL:
```
project = {프로젝트키} AND issuetype = Bug AND reporter = currentUser() ORDER BY created ASC
```
각 이슈에서 수집: `key`, `summary`, `status`(→ statusCategory: Done 여부), `created`(날짜), **결함 원인 유형 커스텀필드 값**.
- 커스텀필드: 설정된 필드명으로 custom field id를 찾는다. 못 찾으면 `cause_field_available=false`로 두고 원인 유형 표는 생략.

## 4. 클라이언트 집계 (날짜·상태로 분류)
기간 = [start, end]. 각 이슈에 대해:
- **신규(new)** = `created`가 [start, end] 안.
- **이월(carry)** = `created < start` AND statusCategory != Done (이전 미해결 잔존).
- **해결(resolved)** = statusCategory == Done.

집계값:
- `new` = 신규 건수, `carry` = 이월 건수
- `cumulative_found` = 전체 이슈 수(=all-time)
- `resolved` = statusCategory==Done 수
- `remaining` = cumulative_found − resolved
- **검증**: `remaining == carry + (신규 중 미해결 수)` 가 성립해야 한다(불일치 시 보고).

`cause_breakdown` (8 고정값 각각, 전체 기준):
- `count` = 해당 원인 이슈 수, `resolved` = 그중 Done, `remaining` = 그중 not Done.

`issues` (상세 이슈 표용) = **신규 + 이월** 이슈만, created 내림차순. 각 항목 `{key, kind(신규|이월), cause, summary}`.

`trend` = 이전 trend 배열 + 이번 행 append:
- `{round_label: "{N}차 통합테스트", new: 신규건수, cumulative: cumulative_found}`

`verdict` 자동 제안:
- `remaining == 0` → "판정: 이슈 없음 · 최종 결과서 전환 권장 …"
- `remaining > 0` → "판정: 다음 빌드({N+1}차) 배포 요청 권장\n근거: 잔여 미해결 {remaining}건 (금차 신규 {new} + 이월 {carry}), 해결률 {rate}% …"

## 5. 페이로드 작성 → 렌더 실행
메타 블록 포함해 페이로드 JSON을 임시 파일로 쓴다(`.qa-report-payload.json`):
```json
{
  "solution": "...", "project_key": "...", "round": N,
  "period_start": "...", "period_end": "...",
  "build_ver": "...", "qa_staff": "QA: ...",
  "cause_field_available": true,
  "issues": [ ... ],
  "agg": {"new":, "carry":, "cumulative_found":, "resolved":, "remaining":},
  "cause_breakdown": { "<원인유형>": {"count":,"resolved":,"remaining":}, ... },
  "trend": [ ... ],
  "verdict": "...",
  "output_path": "<출력폴더>/{솔루션} QA {N}차 통합테스트 결과서.xlsx",
  "meta": {
    "spec_id": "qa-report/0.1.0",
    "solution":, "project_key":, "round": N,
    "period_start":, "period_end":,
    "cumulative_found":, "resolved":, "remaining":, "new_count":, "carry_count":,
    "trend": [ ...append된 전체... ],
    "generated_marker": "qa-report v0.1.0"
  }
}
```
실행: `python ${CLAUDE_PLUGIN_ROOT}/scripts/build_report.py .qa-report-payload.json`
완료 후 임시 페이로드 삭제.

## 6. 완료 보고
- 산출 파일 경로 + 1줄 요약: `{솔루션} {N}차 · 신규 {new}·이월 {carry}·잔여 {remaining}·해결률 {rate}% → {판정}`.
- QA가 결론 문구를 직접 다듬을 수 있음을 안내.

## 제약
- reporter=currentUser() 기준이라 **실행 QA 본인 등록 버그만** 집계(대리 등록 누락 가능).
- 결과 숫자는 발부 시점 동결(메타 블록). 재생성 시에도 과거 차수 보존.
- 솔루션·프로젝트 명사는 전부 입력값 — 하드코딩 금지.
