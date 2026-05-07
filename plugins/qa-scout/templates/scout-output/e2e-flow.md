---
team: <TEAM>
source: <개발팀 산출물 파일명·버전>
version: 0.1
generated_by: scout
generated_at: <YYYY-MM-DD>
live-verify:
  status: <PASS|SKIP|NOT-FOUND|보강>
  verified_at: <YYYY-MM-DD or null>
  verified_by: <live-verifier or null>
  tool: <playwright|chrome|null>
  notes: <보강·미일치·SKIP 사유>
---

# <TEAM> E2E 플로우

> scout 정제 데이터 + live-verifier 라이브 검증 대상. 시나리오 흐름. 추정 금지.

## E2E 플로우

### Flow: <플로우 이름>

- **트리거**: <사용자 행동 / 시스템 이벤트>
- **목표**: <업무 결과>
- **사용자 롤**: <롤>
- **연관 기능**: <F-NNN, F-NNN>

#### 전제 조건
- <조건>

#### 단계
| # | 화면·메뉴 | 행동 | 입력·선택 | 검증 포인트 | 결과 |
|---|---|---|---|---|---|
| 1 | <화면> | <행동> | <입력> | <검증> | <결과> |

#### 종료 조건
- <조건>

#### 분기·예외
| 분기 | 조건 | 처리 |
|---|---|---|
| <분기> | <조건> | <처리> |

---

### Flow: <플로우 이름 2>

(Flow 1과 동일 양식. 자료 부족 시 `[자료 부족]` 마커.)

---

## 작성 규칙

- 한 섹션 = 한 플로우. 단계는 화면 단위로 끊음.
- live-verifier가 `live-verify` frontmatter에 직접 기록 (별도 양식 X).
- 자료 부족 시 단계 표 비우고 `[자료 부족]` 마커. 추정 금지.
- 필수 헤더 (PostToolUse 훅 검증): `## E2E 플로우`, 최소 1건의 `### Flow:`
