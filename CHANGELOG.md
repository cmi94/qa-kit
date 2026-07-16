# qa-kit Changelog

마켓플레이스 단위 변경 이력 (플러그인 추가·제거·구조 변경 등).

## [1.3.0] — 2026-07-16

- 신규 수록: `qa-planner` v0.1.0 — 기능정의서·정책정의서 baseline 위 delta 유지보수(POST 사후 문서화 전용). planner-lead·planner-critic 에이전트 + 결정론 게이트 5축 + rubric v2 품질 루프 + 오케스트레이션 문서. delta draft까지만(no-auto-apply). 선행 의존 qa-scout v0.4.0+.
- marketplace 레지스트리 정비: metadata.version 동기(1.1.5→1.3.0), qa-scout description v0.4.0(docs-to-policy-spec) 반영.

## [1.2.0] — 2026-07-16

- `qa-scout` v0.3.1 → **v0.4.0**: 신규 스킬 `docs-to-policy-spec` — 기능정의서 상세정책에서 정책정의서 draft(11컬럼 delta 양식)를 파생. 변수형 정책 ID 대역제(config 분리) + 결정론 validator(8컬럼·관련 FR 실재·대역·3요소) + scout 단계 9c.7 배선. 코드 전용 규칙은 `[원본필요]` 후보만(본문 행 X), 마스터 자동 반영 금지(draft까지만).

## [1.1.5] — 2026-06-01

- `qa-report` v0.1.4 → **v0.1.5**: 이슈 유형 기본값 `Bug` → `오류/버그`. 입력·0건 가드로 타 유형 override 가능.

## [1.1.4] — 2026-06-01

- `qa-report` v0.1.3 → **v0.1.4**: 이슈 유형(issuetype) 설정 가능 — Jira 유형명이 영문 Bug가 아니어도(예 한글 유형) 조회되도록 수정 + 0건 시 실제 유형명 자동 확인.

## [1.1.3] — 2026-06-01

- `qa-report` v0.1.2 → **v0.1.3**: 입력을 한 항목씩 인터랙티브로 수집(한 질문→답→다음). 로직 변경 없음.

## [1.1.2] — 2026-06-01

- `qa-report` v0.1.1 → **v0.1.2**: 결함 원인 분포 표 해결/잔여 → 분포%, 차수별 추이 로직 수정(기간 스코프 신규 + 이전 차수 발견 키 기준 이월, 누적=신규 running sum)

## [1.1.1] — 2026-06-01

- `qa-report` v0.1.0 → **v0.1.1**: 보고자(reporter) 선택 입력 추가 — 비우면 currentUser(), 지정 시 타 QA·팀 데이터 집계

## [1.1.0] — 2026-06-01

- 신규 수록: `qa-report` v0.1.0 — N차 통합테스트 결과서 자동 생성 (Jira fetch → count-only 보고서, 회차 누적 체인)

## [1.0.0] — 2026-05-07

- 마켓플레이스 신규 출범
- 수록: `qa-scout` v0.2.0
- 라이선스: MIT
