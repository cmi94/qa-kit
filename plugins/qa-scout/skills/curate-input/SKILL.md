---
name: curate-input
description: scout v0.2 에이전트가 단계 5에서 호출하는 자료 큐레이션 스킬. 개발자 자료 폴더를 자동 스캔하고 7개 카테고리(PRD·사용자 시나리오·상태 전이도·화면 전개도·권한 매트릭스·도메인 용어집·ERD/아키텍처)로 매핑한 후 다중 후보 디스앰비규에이션·최신본 식별을 통해 잘못된 버전 인풋(GxP 위반)을 방지한다. 단일 보고서 + 개발자 텍스트 답변 → AI 파싱 패턴.
---

# curate-input

scout v0.2의 단계 5 (자동 스캔 → 카테고리 매핑 + 최신본 식별) 전용 스킬. 추정 금지·신뢰도 명시·다층 메타 활용·개발자 텍스트 답변만 룰 적용.

## 사용 시점
scout가 단계 5 진입 시 호출. 단계 4(자료 폴더 경로 확정)가 선행되어 있어야 함.

## 입력
- 자료 폴더 경로 (절대 또는 상대, 다중 가능 — 단계 4에서 받음)
- PROJECT 헤더 (단계 2)

## 출력
- 단일 보고서 (카테고리별 발견·다중 후보·분류 불가·빠진 카테고리)
- `input-manifest.yaml` 1차 작성 (개발자 확정 후 단계 8에서 최종)

## 절차 (V1 8단계)

### 1) 스캔
- Glob 광범위 패턴: `**/*.{md,pdf,docx,doc,png,jpg,svg,mmd,xlsx,xls,csv,json,yaml,yml,txt,drawio,puml,plantuml}`
- 제외 디렉토리: `.git/`, `node_modules/`, `dist/`, `build/`, `.venv/`, `__pycache__/`
- 메타: mtime + git 마지막 commit (있으면)

### 2) 1차 매핑 (저비용 — 신뢰도 ★★★)

| 카테고리 | 파일명 패턴 | 디렉토리 패턴 |
|---|---|---|
| PRD | `prd*`, `requirement*`, `요구*` | `*/prd/`, `*/requirements/` |
| 사용자 시나리오 | `usecase*`, `user-story*`, `scenario*`, `flow*` | `*/usecase/`, `*/scenario/`, `*/flow/` |
| 상태 전이도 | `sequence*`, `seq-*`, `state*` | `*/sequence/`, `*/state/` |
| 화면 전개도 | `wireframe*`, `screen*`, `mockup*`, `layout*` | `*/wireframe/`, `*/ui/`, `*/screen/` |
| 권한 매트릭스 | `permission*`, `role*`, `rbac*`, `auth*` | `*/permission/`, `*/auth/` |
| 도메인 용어집 | `glossary*`, `ubiquitous*`, `terminology*`, `용어*` | `*/glossary/` |
| ERD / 아키텍처 | `erd*`, `architecture*`, `db-schema*` | `*/architecture/`, `*/db/` |

### 3) 2차 매핑 (모호 시 — 신뢰도 ★~★★)
파일명 매칭 실패 시 파일 첫 N줄 Read로 추정:
- Mermaid 시퀀스 다이어그램: `sequenceDiagram` 키워드
- Mermaid 상태 머신: `stateDiagram` 키워드
- 표 구조 (마크다운): `| ... |` 헤더 + 도메인 키워드 (역할·권한·상태)
- 자유 텍스트: 도메인 키워드 빈도

분류 불가 (신뢰도 X) → 사용자 확인 단계로.

### 4) 다중 후보 정렬 (같은 카테고리에 N건 발견 시)
우선순위:
1. 파일명 버전 표기 (`v1`·`v2`·`draft`·`final`) — 최신 가장 위
2. mtime
3. git log 마지막 commit
4. frontmatter 메타 (있으면)

### 5) 단일 보고서 출력
형식:
```
[자료 큐레이션 결과]

[PRD] N건 — 최신 선택 필요 (또는 1건 — 최신 확인 필요)
- {파일1} (mtime, ★★★)
- {파일2} (...)
→ 어느 파일이 현재 유효한 PRD입니까?

[사용자 시나리오] ...
[상태 전이도] ...
[화면 전개도] ...
[권한 매트릭스] ...
[도메인 용어집] ...
[ERD/아키텍처] ...

[분류 불가] N건
- {파일}
→ 어떤 카테고리? (없음 = 무시)

[빠진 카테고리]
- 와이어프레임 — (a) 라이브 URL+계정 / (b) 자기 AI 생성 / (c) 생략
- ...
```

### 6) 빠진 카테고리 가이드 (보고서 안 포함)
- **와이어프레임 부재**: 라이브 URL+계정 받음 → live-verifier 활용 (qa-workbench 측)
- **ERD 부재**: 개발자 자기 AI에게 요청 (프롬프트 템플릿 옵션 제공)
- **권한 자료 부재**: PRD에 권한 섹션(예: §3.4) 있는지 확인 → 발췌 (G16 정책)
- **PRD 부재**: 작업 진행 불가 — 단계 4 재입력 또는 중단
- **기타**: 생략 옵션

### 7) 개발자 텍스트 답변 → AI 파싱
자연어 답변 처리:
- 예시: "PRD는 v2.md, 유스케이스 디렉토리 맞음, 와이어프레임 라이브 URL: https://..."
- 모호 답변 시 재질문 1회

### 8) 메타 태깅 + `input-manifest.yaml` 작성
확정 매핑을 manifest에 기록:
```yaml
project: <project>
scan_root: <자료 폴더>
scanned_at: <ISO 8601>
found_files:
  - path: <상대 경로>
    mtime: <ISO 8601>
    git_commit: <hash | null>
    category: <category | null>
    confidence: <★★★|★★|★|X>
    status: <confirmed|skipped|missing>
missing_categories: [...]
developer_responses: [...]
```

## 핵심 룰
- **추정 금지**: 단일 후보여도 사용자 확인 1줄 ("이게 최신 맞나요?")
- **신뢰도 명시**: ★★★ 파일명 / ★★ 디렉토리 / ★ 내용 추정 / X 분류 불가
- **다층 메타 활용**: 파일명·mtime·git log·frontmatter 종합
- **개발자 부담 최소**: AI가 1차 매핑 추정 → 개발자 텍스트 답변만

## 한계
- 본 스킬은 단계 5 (큐레이션) 전용
- 단계 9 정형화는 `docs-to-function-spec` 스킬
- 라이브 탐색은 `live-verifier` 에이전트 (qa-workbench 측)

## 참조
- spec: `docs/qa-scout/spec.md` §5-2
- scout 에이전트: `agents/scout.md`
- 후속 스킬: `skills/docs-to-function-spec/SKILL.md`
