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

추가(선택): Build Ver., 결함 원인 유형 커스텀필드명(기본값 `결함 원인 유형`), **보고자(reporter)** — 비우면 실행 본인(currentUser), 특정 인물(들) 지정 시 그 사람이 등록한 버그로 집계 (이름/이메일/계정, 복수 가능).

## 2. 회차 자동 감지 + 이전 차수 발견 목록 로드
- 이전 파일 있으면: `python ${CLAUDE_PLUGIN_ROOT}/scripts/read_meta.py "<이전파일>"` 실행 → JSON.
  - `round`(=M) → 이번 차수 **N = M + 1**.
  - `trend`(이전 회차 행), `discovered_keys`(이전까지 발견된 **모든 이슈 키 배열**), `cumulative_found`(이전 누적) 확보.
  - `round`=0(메타 없음) → N = 1.
- 이전 파일 "없음" 또는 N=1 → trend=[], discovered_keys=[].

## 3. Jira fetch (Atlassian MCP — 기간 스코프 + 이월 키 상태 확인)
**보고자 결정**: 비었으면 `currentUser()`, 지정 시 이름/이메일 → accountId 해석 후 `reporter in (...)`. 아래 `reporter = currentUser()`를 치환.

**(1) 신규 = 지정 기간 내 생성 이슈만** (⚠ 기간 밖은 절대 날짜로 조회하지 않는다):
```
project = {프로젝트키} AND issuetype = Bug AND reporter = currentUser()
  AND created >= "{start}" AND created <= "{end} 23:59" ORDER BY created ASC
```
수집: `key`, `summary`, `status`(statusCategory), **결함 원인 유형 커스텀필드 값**. 필드 못 찾으면 `cause_field_available=false`.

**(2) 이월 확인 = N ≥ 2에서만, 이전 발견 키 목록의 현재 상태만 재확인** (기간 무관, **키로 직접 조회**):
```
key in ({discovered_keys})    # 또는 getJiraIssue로 각 키 status·요약·원인 확인
```
- statusCategory != Done 인 키 = **이월**. (이전 차수에서 발견됐는데 아직 미해결)
- 1차거나 discovered_keys 비었으면 이월 없음.
- ⚠ 이월은 **오직 이전 차수 발견 목록** 기준. 기간 밖 이슈를 날짜로 긁지 않는다(옛 무관 이슈 혼입 방지).

## 4. 클라이언트 집계
- `new_keys` = (1) 신규 키 중 이전 `discovered_keys`에 없는 것 (교집합 제거).
- `carry_keys` = (2)에서 미해결로 확인된 이전 키.
- `discovered_keys_now` = 이전 `discovered_keys` ∪ `new_keys`.

집계값:
- `new` = len(new_keys), `carry` = len(carry_keys)
- `cumulative_found` = len(discovered_keys_now) (= 이전 누적 + new)
- `resolved` = discovered_keys_now 중 statusCategory==Done 수 (신규는 (1), 이전 키는 (2)에서 확인)
- `remaining` = cumulative_found − resolved (= carry + 신규 중 미해결)

`cause_breakdown` = **상세 이슈(신규+이월) 원인별 건수** (8 고정값). → 렌더러가 분포% 계산. (이월 키 원인은 (2)에서 함께 수집)

`issues` (상세 이슈 표) = 신규 키 + 이월 키, 각 `{key, kind(신규|이월), cause, summary}`. 신규 먼저.

`trend` = 이전 trend + `{round_label: "{N}차 통합테스트", new: len(new_keys)}`. (누적 열은 렌더러가 new running sum으로 계산)

`verdict` 자동 제안:
- `remaining == 0` → "판정: 이슈 없음 · 최종 결과서 전환 권장 …"
- `remaining > 0` → "판정: 다음 빌드({N+1}차) 배포 요청 권장\n근거: 잔여 미해결 {remaining}건 (금차 신규 {new} + 이월 {carry}), 해결률 {rate}% …"

## 5. 페이로드 작성 → 렌더 실행
스펙(§4-3) 메타 블록 포함해 페이로드 JSON을 임시 파일로 쓴다(`.qa-report-payload.json`):
```json
{
  "solution": "...", "project_key": "...", "round": N,
  "period_start": "...", "period_end": "...",
  "build_ver": "...", "qa_staff": "QA: ...",
  "cause_field_available": true,
  "issues": [ ... ],
  "agg": {"new":, "carry":, "cumulative_found":, "resolved":, "remaining":},
  "cause_breakdown": { "<원인유형>": <건수>, ... },
  "trend": [ {"round_label":"{n}차 통합테스트","new":<신규건수>}, ... ],
  "verdict": "...",
  "output_path": "<출력폴더>/{솔루션} QA {N}차 통합테스트 결과서.xlsx",
  "meta": {
    "spec_id": "qa-report/0.1.2",
    "solution":, "project_key":, "round": N,
    "period_start":, "period_end":,
    "cumulative_found":, "resolved":, "remaining":, "new_count":, "carry_count":,
    "trend": [ ...append된 전체... ],
    "discovered_keys": [ ...이번 차수까지 발견된 모든 이슈 키... ],
    "reporter": "currentUser | <지정 보고자 표시명>",
    "generated_marker": "qa-report v0.1.2"
  }
}
```
> `discovered_keys`는 **다음 차수 이월 판정의 핵심** — 반드시 이번 신규 키까지 누적해 저장한다.
> `qa_staff`(보고서 QA 담당자 칸)는 보고자를 지정했으면 그 보고자(들) 표시명으로 채운다. 비웠으면 실행 본인.
실행: `python ${CLAUDE_PLUGIN_ROOT}/scripts/build_report.py .qa-report-payload.json`
완료 후 임시 페이로드 삭제.

## 6. 완료 보고
- 산출 파일 경로 + 1줄 요약: `{솔루션} {N}차 · 신규 {new}·이월 {carry}·잔여 {remaining}·해결률 {rate}% → {판정}`.
- QA가 결론 문구를 직접 다듬을 수 있음을 안내.

## 제약
- 보고자 미지정 시 `currentUser()`(실행 본인 등록분). 지정 시 그 보고자(들) 등록분 집계 — 타 QA·팀 데이터도 뽑을 수 있음.
- 결과 숫자는 발부 시점 동결(메타 블록). 재생성 시에도 과거 차수 보존.
- 솔루션·프로젝트 명사는 전부 입력값 — 하드코딩 금지.
