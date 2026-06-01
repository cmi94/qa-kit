# qa-kit

> QA용 Claude Code 플러그인 컬렉션. 1인 QA 운영, GxP 환경, 환각 가드 설계 사례.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Plugin-blue)](https://code.claude.com)

## 설치

Claude Code에서 마켓플레이스 1회 등록 후 원하는 플러그인을 설치합니다.

```
/plugin marketplace add cmi94/qa-kit
/plugin install qa-scout@qa-kit
```

## 수록 플러그인

### [qa-scout](plugins/qa-scout/) (v0.2.0)

개발자가 보유한 5종 도메인 지식(사용자 시나리오·상태 전이도·화면 전개도·권한 매트릭스·도메인 용어집)을 인계받고 PRD를 GxP 양식 기능 정의서(Google Sheets 5시트, 17컬럼)로 정형화.

| 구성요소 | 모델 | 역할 |
|---|---|---|
| `scout` 에이전트 | Sonnet | 오케스트레이션·markdown 작성·인터뷰 |
| `scout-curator` 에이전트 | Haiku | 자료 큐레이션 (대량 파일 단순 패턴) |
| `scout-analyzer` 에이전트 | Opus | PRD 깊이 분석 (F-NNN 분해·BR 매핑) |
| `curate-input` 스킬 | — | 자료 자동 스캔·매핑·최신성 확인 |
| `docs-to-function-spec` 스킬 | — | PRD → 17컬럼 기능 정의서 정형화 |
| `markdown-to-sheets` 스킬 | — | markdown → Google Sheets 이행 |

**환각 가드 6종**

1. 추정 금지
2. 최신본 확인 우선
3. `[자료 부족]` 마커
4. 출처 표기 강제 (행 단위 GxP 추적)
5. 받기 5종 본문 변환 금지
6. 이모티콘 금지

자세한 사용법: [plugins/qa-scout/README.md](plugins/qa-scout/README.md)
스펙: [docs/qa-scout/spec.md](docs/qa-scout/spec.md)

### [qa-report](plugins/qa-report/) (v0.1.4)

N차 통합테스트 결과 보고서(.xlsx)를 양식 고정·데이터만 채우는 방식으로 결정론적 생성. `/qa-report`가 입력 5개(솔루션명·Jira 프로젝트 키·QA 일정·이전 차수 파일·출력 폴더)를 강제 수집하고, Atlassian(Jira) MCP로 신규/이월 버그를 fetch해 count-only 보고서(이슈 수 집계·결함 원인 유형별 분포·차수별 추이·결론)를 만든다.

| 구성요소 | 역할 |
|---|---|
| `/qa-report` 커맨드 | 입력 강제 수집 → Jira fetch → 집계 → 렌더 오케스트레이션 |
| `build_report.py` | 결정론적 렌더러 (양식 RGB 고정·메타 블록 기록) |
| `read_meta.py` | 이전 차수 .xlsx 메타 읽기 (회차 자동 감지) |

- 회차 누적은 결과 `.xlsx` 내장 `_meta` 블록 체인(1차→2차→3차, 발부 시점 동결).
- 보고자(reporter) 선택 — 비우면 `currentUser()`(본인), 지정 시 타 QA·팀 데이터도 집계 (v0.1.1).

설치: `/plugin install qa-report@qa-kit` · 자세한 사용법: [plugins/qa-report/README.md](plugins/qa-report/README.md)

## 향후 추가 예정

- `qa-tc` — JIRA 이슈 분석 → 테스트 케이스 자동 생성
- `qa-launch` — 런칭 준비 스펙 분석·TC·자동화 스크립트 생성
- `qa-regression` — pytest 회귀 실행·리포트

## 라이선스

[MIT](LICENSE)

## 작성자

최명인 (chlauddls12@gmail.com) — 6년차 제약 QA, 1인 QA 운영
