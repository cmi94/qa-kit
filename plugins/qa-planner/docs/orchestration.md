# qa-planner 오케스트레이션 — 드라이버 없이 품질 루프를 돌리는 검증된 경로

본 플러그인에는 자동 실행 드라이버가 없다(미검증 자동화는 배포하지 않는다는 원칙). 대신 **오케스트레이터(사람이 지켜보는 Claude Code 세션)가 루프를 소유**한다. 이 절차는 실전 런에서 검증된 방식이다 — 오케스트레이터가 Agent 도구로 planner-lead·planner-critic을 스폰하고, 결정론 게이트를 직접 실행하고, 감사로그를 직접 쓴다.

역할 분담(불변):
- **planner-lead** = 저술만 (delta CSV + gate-input). 게이트 실행·크리틱 스폰·로그 작성 금지.
- **planner-critic** = 채점만 (report-only). **오케스트레이터로부터만 호출**된다.
- **오케스트레이터** = 반복 제어 · 게이트 실행 · 크리틱 스폰 · 감사로그 · handoff. 아래 절차의 주어는 전부 오케스트레이터다.

---

## 절차 (반복 N = 1부터, max-N 기본 5)

### 0. 런 준비
- run-id 확정: `{기능명}-{YYYYMMDD}`.
- `outputs/{기능명}/_run/` 생성. 이전 런 잔재가 있으면 초기화(git 미추적 임시물).

### 1. author 스폰 (planner-lead)
Agent 도구로 planner-lead를 스폰한다. 헤더: `[MODE: POST] [PROJECT] [CONFIG] [FEATURE] [CODE] [DESIGN] [RUN_ID]` (+ 반복 2 이후엔 "직전 loop-audit-log 최신 줄의 failed_axes만 수정" 지시).
완료 시 산출: delta CSV 2종 + `_run/gate-input-iter{N}.json` (+ 반복 1이면 `_run/source/*.yaml` preflight).

### 2. 결정론 게이트 실행
```
python scripts/deterministic-gate.py outputs/{기능명}/_run/gate-input-iter{N}.json
```
stdout의 JSON을 그대로 보관한다 — iteration 레코드의 `deterministic_gate` 필드가 된다. exit 0 = clean 자격(5축 pass + 마커 0).

### 3. 크리틱 스폰 (planner-critic)
Agent 도구로 planner-critic을 스폰한다. 헤더: `[PROJECT] [RUN_ID] [ITERATION] [DRAFT_PATHS: delta CSV 2종] [RUBRIC: knowledge/planner-critique-rubric-v2.md] [BASELINE] [CODE]`.
반환 JSON(`scores`·`pass`·`failed_axes`)을 그대로 보관한다 — iteration 레코드의 `critic_scores` 필드가 된다.

### 4. 해시 계산 + iteration 레코드 append
**해시 계산 명령** (Git Bash / PowerShell 공통 — python):
```
python -c "import hashlib,sys;print('sha256:'+hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" <파일>
```
- `input_hash` = `{"baseline": <기능정의서 master 해시>, "code": <_run/source/code-reference.yaml 해시>}` (반복 간 입력이 안 바뀌면 반복 1 값 재사용).
- `draft_hash` = delta CSV 2종을 각각 해시해 `"<기능정의서delta해시>+<정책정의서delta해시>"` 또는 두 파일을 이어 한 해시 — 방식을 런 안에서 일관되게.
- iteration 레코드 1줄을 `_run/loop-audit-log.jsonl`에 **append**(덮어쓰기 금지). 필수 필드 = schema §2-1 (record_type·run_id·iteration·mode·executor·model[실측 모델 id]·rubric_version·max_n·input_hash·draft_hash·deterministic_gate[절차 2 출력 그대로]·critic_scores[절차 3 반환 그대로]·failed_axes[게이트 fail 축 + 크리틱 <4 축 합집합]·fix_summary·timestamp[시스템 시각]).

### 5. 수렴 판정 (분기)
- **clean**: 게이트 exit 0(clean_eligible=true) AND 크리틱 pass(3축 전부 ≥4) → 절차 6으로 (stop_reason=gate_pass).
- **미수렴**: N < max-N → N+1로 절차 1부터 반복(failed_axes만 수정 지시).
- **flagged**: N = max-N 도달, 또는 통과 축이 2반복 연속 정체(no_progress), 또는 고칠 축이 없는데 마커 잔존 → 절차 6으로.
- **blocked**: 절차 1에서 author가 입력 불충분을 보고(저술 미진입) → iteration 레코드 없이 절차 6으로 (stop_reason=input_insufficient).

### 6. terminal 레코드 + handoff 작성
- terminal 레코드 1줄 append (schema §2-2: final_status·stop_reason·iterations_run·iso_triage_table·unresolved_markers·timestamp).
- `_run/handoff.yaml` 작성 — 필드 정의는 `knowledge/handoff-schema.md`. `[충돌]` 항목은 `implementation_conflicts:`로 격상.

### 7. 감사로그 자가 검증
```
python scripts/validate-audit-log.py outputs/{기능명}/_run/loop-audit-log.jsonl
```
exit 0 확인. FAIL이면 로그를 고치는 게 아니라 **잘못 기록된 원인을 고치고 레코드를 append로 정정**한다(append-only — 기존 줄 수정·삭제 금지).

### 8. 사람 인계
handoff.yaml + delta CSV 2종을 사람 검토자에게 보고. **마스터 반영·커밋·미러 재생성은 전부 사람 몫** — 오케스트레이터도 자동 반영하지 않는다(no-auto-apply).

---

## 자주 틀리는 지점

- **planner-lead에게 게이트를 돌리게 하지 마라** — lead 자가판정은 "커버됨" 선언 환각의 온상. 게이트는 오케스트레이터가 스크립트로.
- **크리틱 결과를 lead가 요약 전달하게 하지 마라** — 오케스트레이터가 critic 반환 JSON을 로그에 원문 그대로 넣는다.
- **model 필드는 실측** — 스폰한 에이전트의 실제 모델 id. 추측 금지.
- **timestamp는 시스템 시각 인용** — 에이전트가 지어내지 않는다.
- 하네스에서 **중첩 서브에이전트는 동기 대기가 안 될 수 있다**(lead가 critic을 불러도 결과를 같은 턴에 못 받는 제약) — 그래서 루프 제어를 오케스트레이터로 올린 것이다. 이 구조를 유지하라.
