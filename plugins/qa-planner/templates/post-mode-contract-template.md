# {PROJECT} 플래너 운영 계약 — 사후(POST) 모드

> **템플릿** — `{PROJECT}`·경로·대역을 프로젝트 값으로 채워 대상 레포에 설치한다(예: `qa-planner/contracts/post-mode-contract.md`). 프로젝트 상수의 SoT는 `planner-config.yaml`(플러그인 `scripts/planner-config.example.yaml` 참조) — 본 계약은 config를 인용하고 값을 중복 정의하지 않는다.

- **확정일**: {YYYY-MM-DD} (승인자)
- **왜**: 일부 기능은 개발 완료 후 문서가 따라간다(사후 문서화). 플래너는 대상 레포 안에서 돌며 기능정의서·정책정의서를 delta 방식으로 유지보수한다.

---

## 1. 홈 구조와 I/O 경로

```
{대상 레포}/
├── {config: baseline.funcspec_master 의 폴더}      # 마스터 원본 (사람 소유, CSV = SoT, 시트는 미러)
│   ├── 기능정의서_master.csv                        # 컬럼 = config: columns.funcspec_master_columns
│   └── 정책정의서_master.csv                        # 컬럼 = config: columns.policyspec_master_columns
│
└── qa-planner/                                     # 플래너 실행기
    ├── contracts/post-mode-contract.md             # 본 문서 (템플릿 인스턴스)
    ├── knowledge/                                  # rubric v2·audit-log schema·handoff schema (플러그인 카피)
    ├── scripts/                                    # deterministic-gate.py · validate-audit-log.py + planner-config.yaml
    └── outputs/{기능명}/                            # 아웃풋: 기능당 폴더 1개, 회차 없음
        ├── 기능정의서_delta_{기능명}.csv             # 산출물 = CSV 2개 (git 추적)
        ├── 정책정의서_delta_{기능명}.csv
        └── _run/                                   # 루프 중간물 (git 미추적, 재실행 시 초기화)
```

**인풋(POST)**: 별도 인입 없음 — **레포 자체가 인풋**. 문서 변경이력·설계 문서·커밋 이력에서 변경 기능을 식별한다. 호출자가 기능별 커밋 범위·설계 문서 좌표를 지정한다(에이전트 자체 수집 금지 — 기능 경계 오분류 방지).

**증적 = git.** 별도 증적 문서를 남기지 않는다:
- 근거(커밋·설계 문서·baseline) → delta CSV의 **근거 컬럼** (행마다)
- 구현≠요구 QA 신호 → delta CSV의 **마커 컬럼** (`[충돌]`)
- 품질 판정·런 요약 → **커밋 메시지** (예: `docs(planner): {기능명} delta — 게이트 5축 pass, 크리틱 5/4/5, [충돌] 1건`)
- 회차·재수정 이력 → **git log** (재수정 런은 같은 CSV를 갱신하고 커밋)
- `_run/`(gate-input·loop-audit-log·handoff·source 스냅샷)은 루프 제어용 임시물 — 커밋하지 않으며 재실행 시 초기화된다.

## 2. 모드

| 구분 | POST (사후) — **본 계약 범위** | PRE (사전) — `[후속]` 미지원 |
|---|---|---|
| 시점 | 개발 완료 후 | 개발 착수 전 |
| 인풋 | 레포(문서 변경이력·설계 문서·커밋 — 호출자 지정) + baseline | (미지원 — 요구 문서 인입 채널·기획서/화면설계서 산출 체인은 후속 버전) |
| 진실의 원천 | **코드가 사실** — 요구·설계서는 의도 설명 보조 | — |
| delta 분해 | **코드 ↔ baseline 대조가 1차** | — |
| 산출물 | **기능정의서 delta CSV + 정책정의서 delta CSV** | — |
| 크리틱 rubric | v2 (정합성·명료성·코드정합성) | — |

baseline = config `baseline.*` 마스터 CSV 2종. 시트 미러가 있어도 baseline이 아니다.

## 3. POST 확정 결정

1. **충돌 규칙 = 코드 기준 + `[충돌]` 병기** — 구현이 요구와 다르면 코드대로 기술하고 마커로 드러낸다(QA 신호). 자동 해소 금지.
2. **delta draft까지만** — 마스터 CSV 반영은 사람이 검토 후 수행(no-auto-apply). 반영 시 변경이력 기록 + 미러 재생성.
3. **코드 입력 = 호출자가 기능별 커밋·설계 문서 지정.**

## 4. delta CSV 양식

**기능정의서 delta** — 컬럼 = `변경 유형` + config `columns.funcspec_master_columns` **그대로 가운데 배치**(사각형 복사 → 마스터 반영) + `근거 | 마커`.

**정책정의서 delta** — 컬럼 = `변경 유형` + config `columns.policyspec_master_columns` 그대로 + `근거 | 마커`.

**공통 규칙:**
- 변경 유형 = `추가`/`변경`/`삭제`. `변경` 행은 수정 내용이 반영된 **행 전체**(마스터 행 통째 교체). `삭제`는 대상 ID + 사유(비고).
- id 발급: 기능 ID = config `id.fr_prefix`+NNN, 정책 ID = config `id.policy_prefix`+NNN — **도메인 대역제**(config `id.bands`) 안에서 기존 max+1, 결번 허용, 재사용 금지.
- 연결성: 정책의 관련 FR ↔ 기능정의서 delta·마스터의 FR id 양방향 추적(게이트 `frs[]` 검사).
- **쉬운언어 + 마스터 기존 행 문체 준수** — 명료성 크리틱 채점 대상.
- 인코딩 UTF-8(BOM), 셀 내 줄바꿈은 실제 줄바꿈(따옴표 감쌈 — csv 표준).
- 마커 3종: `[추정]`(추론 채움) / `[미확정]`(정보 부재) / `[충돌]`(구현≠요구).

## 5. 런타임 (품질 루프)

루프는 **오케스트레이터**가 소유한다(플러그인 `docs/orchestration.md`가 절차 SoT) — planner-lead는 반복별 author/fix 워커.

- author가 delta CSV 2종 + `_run/gate-input-iter{N}.json`을 남긴다. preflight 좌표(yaml)는 `_run/source/`.
- 결정론 게이트 5축(완전성·추적성·ISO 커버리지·N/A 사유·정합성[FR 연결 포함]) + 독립 크리틱(rubric v2).
- 종료 상태: clean(전축 pass + 마커 0 + 크리틱 3축 ≥4) / flagged(마커 잔존·미수렴 — [충돌]이 있으면 **정상적인 사람 검토 신호**) / blocked(입력 불충분).
- 종료 후 사람: 산출물 검토 → 승인분을 마스터 CSV에 반영 → 변경이력 기록 → 커밋(메시지에 판정 요약) → 미러 재생성.

## 6. 재수정 런 (같은 기능에 신규 요구 발생)

- 직전 delta가 마스터에 **반영됨** → 갱신된 마스터가 baseline. 같은 CSV 파일을 새 delta로 갱신(기존 FR/정책은 `변경` 행).
- **미반영** → 워킹트리의 기존 delta CSV가 원본 — 그 위에 변경을 병합해 갱신(id 승계, 해소된 마커 제거).
- 어느 쪽이든 이력은 git 커밋으로 남는다. 회차 폴더 없음.

## 7. 금지 (불변)

- 마스터 CSV·미러(시트)·소스 코드 자동 수정 금지 (draft까지만).
- `[충돌]` 자동 해소 금지 — 드러내기만, 판단은 사람.
- 크리틱 자기평가 금지 (독립 planner-critic만 채점, 호출은 오케스트레이터만).
- max-N(기본 5) 초과 반복 금지.

## 8. 변경 이력

| 일자 | 변경 |
|---|---|
| {YYYY-MM-DD} | 템플릿 인스턴스화 ({PROJECT}) |
