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

# <TEAM> 전개도

> scout 정제 데이터 + live-verifier 라이브 검증 대상. 메뉴·화면 구조. 추정 금지.

## 메뉴 트리

```
<루트>
├── <대분류 1>
│   ├── <중분류 1-1>
│   │   ├── <메뉴 1-1-1>
│   │   └── <메뉴 1-1-2>
│   └── <중분류 1-2>
└── <대분류 2>
    └── <메뉴 2-1>
```

## 화면 구성

### Screen: <화면 ID·이름>

- **메뉴 경로**: <대분류 > 중분류 > 메뉴>
- **URL·route**: <경로>
- **사용자 롤**: <접근 가능 롤>
- **연관 기능**: <F-NNN, F-NNN>

#### 구성 요소
| 영역 | 요소 | 종류 | 비고 |
|---|---|---|---|
| <영역> | <요소명> | <button/input/grid/...> | <비고> |

#### 액션
| 액션명 | 트리거 | 결과 |
|---|---|---|
| <액션> | <트리거> | <결과> |

---

### Screen: <화면 ID·이름 2>

(Screen 1과 동일 양식. 자료 부족 시 `[자료 부족]` 마커.)

---

## 작성 규칙

- 메뉴 트리는 ASCII 아트로 계층 표현 (들여쓰기 + 박스 문자).
- Screen 단위는 한 화면 = 한 섹션.
- live-verifier가 `live-verify` frontmatter에 직접 기록.
- 자료 부족 시 표 비우고 `[자료 부족]` 마커.
- 필수 헤더 (PostToolUse 훅 검증): `## 메뉴 트리`, `## 화면 구성`, 최소 1건의 `### Screen:`
