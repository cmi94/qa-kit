# qa-planner (v0.1.0)

기능정의서·정책정의서 baseline(마스터 CSV) 위에서 **코드 변경분을 delta로 유지보수**하는 자율 저술 플러그인. **POST(사후 문서화) 전용** — 개발이 문서보다 먼저 가는 프로젝트에서, 코드에 이미 있는데 문서에 없는 것을 delta CSV draft로 따라잡는다.

## 파이프라인에서의 위치

```
qa-scout (v0.4.0+)          사람                qa-planner (본 플러그인)
기능정의서 + 정책정의서   →   검토·확정   →   코드 변경분을 delta CSV로 저술
baseline 부트스트랩          (마스터 CSV)       → 품질 루프 수렴 → 사람 승인 → 마스터 반영
```

**선행 의존: [qa-scout](../qa-scout) v0.4.0 이상.** baseline 마스터 CSV 2종(기능정의서·정책정의서)이 있어야 돈다 — 없으면 qa-scout로 먼저 부트스트랩. baseline 없는 프로젝트에 planner만 설치하면 모든 런이 blocked다.

## 구성

| 경로 | 내용 |
|---|---|
| `agents/planner-lead.md` | 저술 워커 — delta 분해·CSV 저술·gate-input 작성 (루프 제어 안 함) |
| `agents/planner-critic.md` | 독립 크리틱 — rubric v2 3축(정합성·명료성·코드정합성) 채점, report-only |
| `templates/post-mode-contract-template.md` | 운영 계약 템플릿 — 프로젝트 값 채워 대상 레포에 설치 |
| `scripts/planner-config.example.yaml` | **프로젝트 결합 지점 단일화** — id 대역·baseline 경로·컬럼 스키마 |
| `scripts/deterministic-gate.py` | 결정론 게이트 5축 (완전성·추적성·ISO 25010·N/A 사유·정합성+FR연결) |
| `scripts/validate-audit-log.py` | 감사로그 스키마·상태 규칙 검증 (false pass 차단) |
| `knowledge/planner-critique-rubric-v2.md` | 크리틱 채점 척도 (0~5 anchor·건수 기준) |
| `knowledge/planner-loop-audit-log.schema.md` | gate-input + loop-audit-log 계약 |
| `knowledge/handoff-schema.md` | 검토 인계 패킷(handoff.yaml) 필드 정의 |
| `docs/orchestration.md` | **루프 실행 절차 SoT** — 오케스트레이터가 도는 검증된 경로 |

**자동 실행 드라이버는 없다.** 루프(반복·게이트·크리틱·로그·handoff)는 오케스트레이터 세션(사람이 지켜보는 Claude Code 세션)이 `docs/orchestration.md` 절차대로 소유한다.

## 설치 (대상 프로젝트 레포에)

```bash
# 1. 에이전트
cp plugins/qa-planner/agents/planner-lead.md   <레포>/.claude/agents/
cp plugins/qa-planner/agents/planner-critic.md <레포>/.claude/agents/

# 2. 실행기 골격
mkdir -p <레포>/qa-planner/{contracts,knowledge,scripts,outputs}
cp plugins/qa-planner/knowledge/*.md           <레포>/qa-planner/knowledge/
cp plugins/qa-planner/scripts/*.py             <레포>/qa-planner/scripts/
cp plugins/qa-planner/docs/orchestration.md    <레포>/qa-planner/

# 3. 프로젝트 값 채우기 (필수 — 이거 없이는 안 돈다)
cp plugins/qa-planner/scripts/planner-config.example.yaml <레포>/qa-planner/scripts/planner-config.yaml
#   → project·id 대역·baseline 경로·컬럼 스키마를 실제 값으로
cp plugins/qa-planner/templates/post-mode-contract-template.md <레포>/qa-planner/contracts/post-mode-contract.md
#   → {PROJECT}·{YYYY-MM-DD} 채움
```

## 사용 (런 1회)

1. 사람이 기능 경계 확정: 기능명 + 커밋 범위 + 설계 문서 좌표.
2. 오케스트레이터 세션에서 `docs/orchestration.md` 절차 0~8 수행 (planner-lead 스폰 → 결정론 게이트 → planner-critic 스폰 → 감사로그 → 수렴 → handoff).
3. 사람: handoff + delta CSV 검토 → 승인 행 마스터 반영 → 변경이력 → 커밋 → 미러 재생성.

## 안전 원칙 (불변)

- **no-auto-apply**: planner는 delta CSV draft까지만. 마스터 CSV·시트·소스 자동 수정 금지 (GxP).
- **`[충돌]` 자동 해소 금지**: 구현≠요구는 코드 기준 기술 + 마커로 드러내기만 — 판단은 사람.
- **크리틱 독립**: 채점은 planner-critic만, 호출은 오케스트레이터만 (자기평가 차단).
- **감사로그 append-only**: 덮어쓰기·삭제 금지 — 감사추적 무결성.

## 변경 이력

| 버전 | 일자 | 변경 |
|---|---|---|
| 0.1.0 | 2026-07-16 | 최초 발행 — POST 전용 delta 유지보수 파이프라인. 에이전트 2종 + 계약 템플릿 + config 분리(변수형) + 결정론 스크립트 2종 + handoff 스키마 + 오케스트레이션 문서 |
