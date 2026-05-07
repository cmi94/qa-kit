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

## 향후 추가 예정

- `qa-tc` — JIRA 이슈 분석 → 테스트 케이스 자동 생성
- `qa-launch` — 런칭 준비 스펙 분석·TC·자동화 스크립트 생성
- `qa-regression` — pytest 회귀 실행·리포트

## 라이선스

[MIT](LICENSE)

## 작성자

최명인 (chlauddls12@gmail.com) — 6년차 제약 QA, 1인 QA 운영
