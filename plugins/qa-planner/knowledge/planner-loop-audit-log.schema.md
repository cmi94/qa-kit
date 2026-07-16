# qa-planner — loop-audit-log + gate-input 스키마

- **왜**: 자율 노드의 품질 루프 자체가 감사 대상이다(GxP). 반복마다 무엇을 근거로 통과/미달을 판정했는지 append-only로 남겨 감사추적 무결성을 지킨다.
- **검증**: `scripts/validate-audit-log.py <log.jsonl>` (스키마 위반 시 exit 1).

이 문서는 두 계약을 정의한다.
1. **gate-input.json** — planner-lead가 반복마다 만들어 결정론 게이트에 넘기는 입력.
2. **loop-audit-log.jsonl** — 게이트·크리틱 판정을 append-only로 쌓는 감사로그.

---

## 1. gate-input.json (결정론 게이트 입력)

planner-lead가 반복 N마다 문서 초안에서 **기계 판정용 메타**를 뽑아 만든다. 결정론 게이트(`scripts/deterministic-gate.py`)는 문서 원문을 직접 파싱하지 않고 이 계약만 읽는다(문서 양식과 게이트를 분리 — 양식이 바뀌어도 게이트 불변).

```json
{
  "run_id": "session-timeout-20260716",
  "project": "app",
  "iteration": 1,
  "rubric_version": "v2",
  "max_n": 5,

  "urs_requirements": ["REQ-001", "REQ-002"],

  "delta_items": [
    {
      "id": "FR-APP-001",
      "doc": "feature-spec",
      "change_type": "MODIFY",
      "urs_refs": ["REQ-001"],
      "source_links": ["설계문서 §5.3", "baseline FR-APP-001", "commit abc1234"],
      "iso_triage": [
        {"characteristic": "functional_suitability", "applicable": true},
        {"characteristic": "performance_efficiency", "applicable": false, "na_reason": "UI 표기 변경뿐, 성능 요건 없음"},
        {"characteristic": "compatibility",          "applicable": false, "na_reason": "기존 연동 불변"},
        {"characteristic": "usability",              "applicable": true},
        {"characteristic": "reliability",            "applicable": false, "na_reason": "가용성 요건 없음"},
        {"characteristic": "security",               "applicable": true},
        {"characteristic": "maintainability",        "applicable": false, "na_reason": "내부 유지보수 영향 없음"},
        {"characteristic": "portability",            "applicable": false, "na_reason": "이식 대상 아님"}
      ],
      "fr_refs": ["FR-APP-001"]
    }
  ],

  "cross_doc_claims": [
    {"key": "비밀번호 최소 길이", "values": {"feature-spec": "8", "policy": "8"}}
  ],

  "frs": [
    {"id": "FR-APP-001", "implements": ["DELTA-001", "P-APP-001"]}
  ],

  "markers": {
    "[추정]": ["FR-APP-002 inputs"],
    "[미확정]": [],
    "[충돌]": []
  }
}
```

### 1-1. 필드 규칙

| 필드 | 필수 | 규칙 |
|---|---|---|
| `run_id` | O | 런 식별자. 로그 전 레코드가 공유 |
| `project` | O | 프로젝트 키 (planner-config `project`) |
| `iteration` | O | 1부터. 반복마다 +1 |
| `rubric_version` | O | 크리틱 rubric 버전 (POST = `v2`) |
| `max_n` | O | 정지 상한(기본 5) |
| `urs_requirements[]` | O | 요구 id 전체(완전성 분모). POST에서 요구 문서가 없으면 delta 식별에 쓴 변경 근거 id 목록 |
| `delta_items[]` | O | 저술한 추가/변경 항목. 빈 배열 금지(저술 결과이므로) |
| `delta_items[].urs_refs[]` | O | 이 항목이 반영한 요구 id (완전성 역매핑) |
| `delta_items[].source_links[]` | O | 요구·baseline·커밋 근거 링크(추적성). 빈 배열 = 추적성 FAIL |
| `delta_items[].iso_triage[]` | O | **8특성 모두** 존재해야 함. 각 항목 `applicable`은 **필수 boolean(true/false)** — 누락·문자열(`"false"`) 금지(조용한 제외 차단). `applicable:false`면 `na_reason` 필수 |
| `cross_doc_claims[]` | O(빈 배열 허용) | 문서 간 같아야 하는 값. `values` 불일치 = 정합성(결정론) 모순. **`values`의 각 소스 값은 대조할 표준값만 담아라 — 부연설명·수식 유도·`파일:라인` 인용·참조 번호 등 부가 문자열 금지**(게이트는 완전일치 대조라 부가 문자열이 붙으면 의미가 같아도 오탐 fail. 근거·유도는 `delta_items[].source_links`나 CSV 근거 컬럼에만) |
| `delta_items[].screen_refs[]` | X(선택) | 이 항목이 관련된 화면 SCR id. 화면 영향 없으면 생략 또는 빈 배열 (PRE 트랙 — `[후속]`) |
| `screens[]` | X(선택) | 화면 목록 `{id, implements[]}`. 존재하면 §1-3 연결성 검사 발동. 미산출 런은 생략(백워드 컴팻, PRE 트랙 — `[후속]`) |
| `delta_items[].fr_refs[]` | X(선택, POST) | 이 항목이 관련된 기능정의서 delta FR id. FR 영향 없으면 생략 또는 빈 배열 |
| `frs[]` | X(선택, POST) | 기능정의서 delta에서 추출한 FR 목록 `{id, implements[]}`. `implements` = 그 FR이 반영하는 DELTA·정책 id. 존재하면 §1-4 FR 연결성 검사 발동 |
| `markers` | O(게이트 필수 강제) | 3종 마커(`[추정]`·`[미확정]`·`[충돌]`) 위치. 세 키 모두 존재(값은 빈 배열 가능). 하나라도 잔존하면 `clean_eligible=false` |

### 1-2. ISO/IEC 25010 8특성 enum (고정)

```
functional_suitability · performance_efficiency · compatibility · usability ·
reliability · security · maintainability · portability
```

각 `delta_item.iso_triage`는 이 8개를 **모두** 담아야 한다(누락 = 조용한 제외 = FAIL). `security`를 `applicable:false`로 두면 `na_reason` 필수 + 게이트가 `security_na` notice를 남긴다(21 CFR Part 11 — 보안 함부로 N/A 불가, 사람 검토 유도).

### 1-3. 화면 연결성 검사 (정합성_결정론 축 내부 — PRE 트랙 `[후속]`)

`screens[]`가 존재할 때만 발동한다(없으면 기존 동작). 게이트가 검사:

| 검사 | fail 조건 |
|---|---|
| 화면 id 유일성 | `screens[].id` 중복 |
| delta→screen 해소 | `delta_items[].screen_refs`의 id가 `screens[]`에 없음 (dangling) |
| screen→delta 해소 | `screens[].implements`의 id가 delta 항목에 없음 (dangling). 매칭 = delta id와 **정확 일치** 또는 delta id가 `{ref}-` 접두 |
| 양방향 일치 | delta D가 SCR-S를 참조하는데 S의 implements에 D가 없음, 또는 그 반대 |

fail 상세는 `detail.screen_link_conflicts`에 남는다. 축 이름은 기존 5축 그대로(`정합성_결정론` 내부 확장).

### 1-4. FR 연결성 검사 (정합성_결정론 축 내부 — POST 모드)

`frs[]`가 존재할 때만 발동한다(없으면 기존 동작 — 백워드 컴팻). §1-3과 동형 규칙:

| 검사 | fail 조건 |
|---|---|
| FR id 유일성 | `frs[].id` 중복 |
| delta→FR 해소 | `delta_items[].fr_refs`의 id가 `frs[]`에 없음 (dangling) |
| FR→delta 해소 | `frs[].implements`의 id가 delta 항목에 없음 (dangling). 매칭 규칙은 §1-3과 동일 |
| 양방향 일치 | delta D가 FR-F를 참조하는데 F의 implements에 D가 없음, 또는 그 반대 |

fail 상세는 `detail.fr_link_conflicts`에 남는다. 축 세트 불변.

또한 POST 런의 gate-input에는 `rubric_version: "v2"`가 들어가고, planner-lead preflight가 `_run/source/code-reference.yaml`(repo·commit_range·설계 문서 목록)을 함께 남긴다(오케스트레이터 input_hash에 `code` 해시 추가).

---

## 2. loop-audit-log.jsonl (append-only 감사로그)

한 줄 = 한 JSON 객체. **덮어쓰기·삭제 금지**(append-only). 두 레코드 타입.

### 2-1. iteration 레코드 (반복마다 1줄)

```json
{
  "record_type": "iteration",
  "run_id": "session-timeout-20260716",
  "iteration": 1,
  "mode": "post",
  "executor": "planner-lead",
  "model": "<실측 모델 id>",
  "rubric_version": "v2",
  "max_n": 5,
  "input_hash": {"baseline": "sha256:...", "code": "sha256:..."},
  "draft_hash": "sha256:...",
  "deterministic_gate": {
    "완전성": "pass",
    "추적성": "pass",
    "iso_coverage": "fail",
    "na_reason": "pass",
    "정합성_결정론": "pass",
    "overall": "fail",
    "marker_counts": {"[추정]": 1, "[미확정]": 0, "[충돌]": 0},
    "unresolved_markers_total": 1,
    "clean_eligible": false
  },
  "critic_scores": {
    "정합성": {"score": 5, "evidence": "..."},
    "명료성": {"score": 3, "evidence": "..."},
    "코드정합성": {"score": 4, "evidence": "..."}
  },
  "failed_axes": ["iso_coverage", "명료성"],
  "fix_summary": "delta 2건 영문 약어 쉬운 말로 교체 예정",
  "timestamp": "2026-07-16T09:12:00+09:00"
}
```

### 2-2. terminal 레코드 (런 종료 시 1줄, 마지막)

```json
{
  "record_type": "terminal",
  "run_id": "session-timeout-20260716",
  "final_status": "flagged",
  "stop_reason": "max_n",
  "iterations_run": 5,
  "iso_triage_table": [
    {"delta_id": "FR-APP-001", "applicable": ["functional_suitability","usability","security"],
     "na": [{"characteristic":"performance_efficiency","reason":"..."}]}
  ],
  "unresolved_markers": {
    "[추정]": ["FR-APP-002 inputs"],
    "[미확정]": [],
    "[충돌]": ["FR-APP-005 ↔ baseline 승인정책"]
  },
  "timestamp": "2026-07-16T09:40:00+09:00"
}
```

### 2-3. 필드 규칙

| 필드 | 레코드 | 규칙 |
|---|---|---|
| `record_type` | 공통 | `iteration` 또는 `terminal` |
| `run_id` | 공통 | 전 레코드 동일 |
| `executor` | iteration | 저자 에이전트 id (예: planner-lead) |
| `mode` | iteration(선택) | `post`(본 플러그인 기본) / `pre`(`[후속]`). 검증기 필수 세트 밖(백워드 컴팻) |
| `model` | iteration | 실측 모델 id (추측 금지) |
| `input_hash` / `draft_hash` | iteration(필수) | 재현·위변조 탐지용. 검증기가 필드 존재 강제. POST는 `input_hash.code` 추가 |
| `deterministic_gate` | iteration | 축별 `pass`/`fail` + `overall` + `marker_counts` + `clean_eligible`. deterministic-gate.py 출력 그대로 |
| `critic_scores` | iteration(필수) | rubric 반환 그대로(v2 = 정합성·명료성·코드정합성, 점수+근거). 검증기가 필드 존재 강제 |
| `failed_axes` / `fix_summary` | iteration(필수) | 미달 축 목록 + 수정 요약. clean 반복이면 빈 값 허용(키는 존재) |
| `final_status` | terminal | `clean` / `flagged` / `blocked` |
| `stop_reason` | terminal | `gate_pass` / `max_n` / `no_progress` / `input_insufficient` |
| `unresolved_markers` | terminal | 3종 마커 세트 동일(gate-input.markers와 종류 일치 — 문서·로그·handoff 간 어긋남 금지) |

### 2-4. 상태 결정 규칙

```
clean   = 마지막 iteration의 deterministic_gate.clean_eligible == true
          (= 5축 overall pass AND 미해소 마커 0)
          AND critic pass(rubric 전 축 ≥4 — v2: 정합성·명료성·코드정합성)
          AND stop_reason == gate_pass
flagged = max_n 도달 또는 no_progress 2연속 또는 부분입력/충돌 잔존(미해소 마커 존재)
blocked = 입력 검증 실패로 저술 자체 미진입
          (iteration 레코드 0건 + stop_reason == input_insufficient, terminal 레코드만)
```

**검증기 강제**(`validate-audit-log.py`): 위 규칙은 문서 서술로 그치지 않고 검증기가 교차검사한다 — `final_status=clean`인데 마지막 clean_eligible≠true거나 마커 잔존거나 크리틱 <4(rubric v2면 코드정합성 포함)면 FAIL. false pass 차단.

---

## 3. 마커 세트 단일화

세 마커만 쓴다. gate-input `markers`, 문서 본문, terminal `unresolved_markers`가 **동일 세트**여야 한다.

| 마커 | 뜻 |
|---|---|
| `[추정]` | 추론(baseline·도메인·유사)으로 채운 값 |
| `[미확정]` | 정보 부재로 비운 값(입력 부분 결측) |
| `[충돌]` | POST: **구현이 요구사항/설계서와 다름**(코드 기준으로 기술 + 마커 병기 — handoff `implementation_conflicts:`로 격상). PRE(`[후속]`): 요구가 baseline과 모순 |

---

## 4. 변경 이력

| 버전 | 일자 | 변경 |
|---|---|---|
| plugin 0.1.0 | 2026-07-16 | 플러그인 이관 — 원본 schema v1.4에서 프로젝트 예시 중립화·내부 참조 자기완결화·`mode: post` 기본. 계약(필드·enum·검사·상태 규칙) 동일. §2-4 검증기 강제에 rubric v2 코드정합성 포함 명시 |
