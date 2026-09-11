# 04. API 계약서 ⭐ 가장 중요한 문서

> 🎯 **이 문서는 프론트엔드 세션과 백엔드 세션 사이의 "계약서"입니다.**
> 두 세션은 서로의 코드를 볼 수 없습니다. 이 문서만 봅니다.
> 💡 **여기 없는 API는 존재하지 않는 것입니다.**
> 필요하면 아키텍처 세션에 요청해서 이 문서에 먼저 추가하세요.
> 용어와 규칙(글자 수, 범위)은 [02번 룰북](02-게임-도메인-규칙.md)을 그대로 따릅니다.

---

## 0. 공통 규칙

### 기본 주소
```
개발:  http://localhost:8000
운영:  https://<배포 주소>  (배포 시 확정)
```
- 프론트엔드는 이 주소를 코드에 적지 않고 환경변수 `NEXT_PUBLIC_API_BASE_URL`로 읽습니다. (01번 문서 9장)
- **브라우저가 FastAPI를 직접 호출합니다.** (Next.js 서버를 중간에 거치지 않음)

### 모든 요청의 공통 헤더
```
Authorization: Bearer <Supabase access token>
Content-Type: application/json
```
(`/health`, `/api/v1/_schema/sse-events` 만 예외 — 인증 불필요)

### 성공 응답
HTTP 200 / 201 / 204. 본문은 각 API에 정의된 객체 그대로.
(`{ "data": ... }` 같은 껍데기로 감싸지 **않습니다**. 불필요한 한 겹입니다.)

**응답 JSON의 키는 빼먹지 않습니다.** 값이 없으면 키를 생략하지 않고 `null`(또는 빈 배열 `[]`)로 보냅니다.
→ 프론트는 "이 키가 있나 없나"를 검사할 필요 없이 "null인가"만 보면 됩니다.

### 실패 응답 (모든 실패는 이 모양)
```json
{
  "error": {
    "code": "SESSION_NOT_FOUND",
    "message": "이야기를 찾을 수 없어요.",
    "detail": null
  }
}
```
- `code`: 아래 표의 값 중 하나 (영어 대문자)
- `message`: **유저에게 그대로 보여줘도 되는 한글 문장** (스택트레이스·SQL·영어 에러 원문 노출 금지). 게임 톤에 맞게 부드러운 말투
- `detail`: 보통 `null`. `VALIDATION_ERROR`일 때만 `[{ "field": "persona.text", "message": "40자 이내로 적어주세요." }]`

### 에러 코드 전체 목록 (이 표에 없는 code는 쓰지 않는다)

| code | HTTP | 언제 |
|---|---|---|
| `VALIDATION_ERROR` | 400 | 입력 형식·길이 위반, 없는 선택지 번호 등 |
| `CONTENT_NOT_ALLOWED` | 400 | 온보딩·직접 입력에 쓸 수 없는 내용 (02번 문서 3장·9장) |
| `UNAUTHORIZED` | 401 | 토큰 없음 / 만료 / 위조 |
| `NOT_FOUND` | 404 | 없는 주소로 요청 |
| `SESSION_NOT_FOUND` | 404 | 이야기가 없음 / 지워짐 / **남의 것** |
| `TURN_IN_PROGRESS` | 409 | 이 이야기에서 이미 턴을 쓰는 중 |
| `PROLOGUE_REQUIRED` | 409 | 프롤로그가 아직 없는데 행동·에필로그를 요청 |
| `SESSION_ALREADY_COMPLETED` | 422 | 완성된 이야기에 행동·에필로그 요청 |
| `TURN_LIMIT_REACHED` | 422 | 최대 턴(40)에 닿아 더 이어 쓸 수 없음 → 에필로그만 가능 |
| `EPILOGUE_NOT_ALLOWED_YET` | 422 | 본문 턴이 하나도 없는데 에필로그 요청 |
| `RATE_LIMITED` | 429 | 너무 자주 요청 (배포 단계에서 도입) |
| `INTERNAL_ERROR` | 500 | 서버 내부 오류 |
| `LLM_UNAVAILABLE` | 503 | AI 응답 실패/타임아웃 (주로 SSE `error` 이벤트로 옴) |

> 💡 **남의 이야기에 접근하면 403이 아니라 404를 줍니다.**
> 403("권한 없음")을 주면 "그 번호의 이야기가 존재는 한다"는 정보가 새어나갑니다.
> 404("없음")로 통일하면 존재 여부 자체를 숨길 수 있고, 프론트도 처리할 경우가 하나 줄어듭니다.

**프론트엔드**: `error.code`로 분기하고 `error.message`를 그대로 화면에 띄웁니다. `401`이면 로그인 화면으로 보냅니다.

**백엔드 (⚠️ 필수 구현)**: FastAPI는 기본적으로 에러를 `{"detail": ...}` 모양, 입력 검증 실패를 **422**로 보냅니다. 계약서와 다릅니다.
→ 전역 예외 처리기 3개를 반드시 등록합니다. (Step 3)
1. `RequestValidationError` → **400** `VALIDATION_ERROR` (필드별 사유를 `detail`에 한글로)
2. `HTTPException` / 우리가 만든 게임 예외 → 위 모양
3. 그 밖의 모든 예외 → 500 `INTERNAL_ERROR` (원문은 서버 로그에만)

### 시간 형식
모든 시각은 **ISO 8601 UTC** 문자열: `"2026-09-10T14:23:01Z"`
(한국 시간 변환은 프론트엔드가 표시할 때 합니다.)
- **유일한 예외**: `story_state.time` — 게임 속 시각이라 자연어 문자열 그대로 표시 (02번 문서 5장)

---

## 1. 헬스체크

```
GET /health          (인증 불필요)
→ 200 { "status": "ok" }
```

---

## 2. 내 정보

```
GET /api/v1/me
→ 200  Me
{
  "id": "uuid",
  "email": "user@example.com",
  "nickname": "원강",
  "created_at": "2026-09-10T14:23:01Z"
}
```
- 프로필은 가입 시 DB 트리거가 자동 생성합니다. (03번 문서 2-1)
- 혹시 프로필이 없으면 이 API가 생성해서 돌려줍니다. (보조 안전장치)

---

## 3. 온보딩 옵션 (프론트가 표를 따로 들고 있지 않게)

```
GET /api/v1/meta/onboarding-options
→ 200  OnboardingOptions
{
  "fields": [
    {
      "key": "persona", "label": "대상", "question": "오늘의 나는 누구인가요?",
      "max_length": 40,
      "presets": [
        { "id": "persona_office_3y", "text": "3년 차 회사원" },
        { "id": "persona_job_seeker", "text": "취업준비생" }
      ]
    },
    { "key": "emotion",   "label": "감정",     "question": "오늘 마음은 어떤가요?",    "max_length": 40, "presets": [ ... ] },
    { "key": "situation", "label": "상황",     "question": "지금 어디에 있나요?",     "max_length": 40, "presets": [ ... ] },
    { "key": "flavor",    "label": "장르의 결", "question": "어떤 결의 이야기일까요?", "max_length": 40, "presets": [ ... ] }
  ],
  "attitudes": [
    { "code": "endure",   "label": "참아내기",   "description": "감정을 누르고 버틴다" },
    { "code": "avoid",    "label": "피하기",     "description": "한발 물러서거나 외면한다" },
    { "code": "confront", "label": "받아치기",   "description": "뾰족하게 맞선다" },
    { "code": "open_up",  "label": "털어놓기",   "description": "솔직하게 마음을 드러낸다" },
    { "code": "let_go",   "label": "흘려보내기", "description": "대수롭지 않게 넘기거나 받아들인다" }
  ],
  "limits": { "premise_text_max": 40, "free_text_max": 200 }
}
```
- `fields`는 **항상 이 순서**(persona → emotion → situation → flavor)로 옵니다. 화면도 이 순서로 그립니다.
- 칩 문구·질문 문장·태도 표는 백엔드 `app/game/rules.py`가 원본입니다. (02번 문서 3장·6장)

> 💡 **왜 필요한가?** 칩 목록을 프론트 코드에 적어두면, 백엔드에서 칩을 바꿨을 때 **화면만 옛날 칩**으로 남습니다.
> 게다가 칩을 고르면 백엔드가 `preset_id`로 문구를 찾아야 하므로, 두 쪽이 같은 표를 봐야 합니다.

---

## 4. 이야기 (session)

### 4-1. 이야기 만들기 (온보딩 제출)
```
POST /api/v1/sessions
SessionCreateRequest
{
  "persona":   { "text": "3년 차 회사원",       "preset_id": "persona_office_3y" },
  "emotion":   { "text": "지독한 권태와 짜증",   "preset_id": null },
  "situation": { "text": "월요일 아침 출근길",   "preset_id": "situation_monday_commute" },
  "flavor":    { "text": "일상/드라마",         "preset_id": "flavor_daily_drama" }
}
→ 201  SessionDetail  (4-3과 같은 모양. has_prologue = false)
```
**백엔드 검사**
- 각 `text`: 앞뒤 공백 제거 후 1~40자 → 실패 시 400 `VALIDATION_ERROR`
- `preset_id`가 있으면: 존재하는 칩인지 확인하고 **칩의 문구로 덮어씀** (보낸 `text`는 무시). 없는 id면 400
- 금지어 검사 → 400 `CONTENT_NOT_ALLOWED` (Step 9부터 AI 의미 검사 추가, 02번 문서 3장)
- `flavor_code`, 시작 `mood`는 백엔드가 정함 (02번 문서 3장·4장)

> ⚠️ Step 4~8에서는 AI를 호출하지 않아 즉시 응답합니다. **Step 9부터 AI 입력 해석기가 붙어 1~3초 걸릴 수 있고,
> 503 `LLM_UNAVAILABLE`도 올 수 있습니다.** 프론트는 처음부터 "이야기를 준비하는 중..." 대기 표시를 넣어둡니다.

**만든 뒤 흐름**: 응답의 `id`로 읽기 화면(`/story/{id}`)으로 이동 → `has_prologue`가 `false`면 5-2 프롤로그 스트림을 부른다.

### 4-2. 이야기 목록 (이어 쓰는 중 / 여백의 서재)
```
GET /api/v1/sessions?status=completed
→ 200  SessionListItem[]
[
  {
    "id": "uuid",
    "status": "completed",
    "title": "손잡이를 놓지 못한 월요일",
    "premise": { ...4-3의 premise와 같은 모양... },
    "turn_count": 12,
    "mood": { "label": "안도", "valence": 1, "intensity": 2, "note": "..." },
    "mood_valences": [-1, -1, -2, -1, 0, 0, 1, 1],
    "attitude_counts": [
      { "attitude": "endure", "label": "참아내기", "count": 5 },
      { "attitude": "confront", "label": "받아치기", "count": 1 }
    ],
    "updated_at": "2026-09-10T14:30:00Z",
    "completed_at": "2026-09-10T14:30:00Z"
  }
]
```
- `status` 파라미터: `ongoing`(= active + processing) / `completed`(= **여백의 서재**) / `all`. 생략하면 `all`
- 정렬: `ongoing`은 `updated_at` 최신순, `completed`는 `completed_at` 최신순, `all`은 `updated_at` 최신순
- `mood_valences`: 턴 순서대로의 `valence` 목록 → 서재 카드의 **작은 감정 파동 선**
- `attitude_counts`: 개수가 0인 태도는 빼고, 많은 순
- 진행 중인 이야기는 `title`이 `null`

### 4-3. 이야기 상세
```
GET /api/v1/sessions/{id}
→ 200  SessionDetail
{
  "id": "uuid",
  "status": "active",
  "title": null,
  "premise": {
    "persona":   { "text": "3년 차 회사원",     "preset_id": "persona_office_3y" },
    "emotion":   { "text": "지독한 권태와 짜증", "preset_id": null },
    "situation": { "text": "월요일 아침 출근길", "preset_id": "situation_monday_commute" },
    "flavor":    { "text": "일상/드라마",       "preset_id": "flavor_daily_drama" },
    "flavor_code": "daily_drama"
  },
  "mood": { "label": "짜증", "valence": -1, "intensity": 4, "note": "어깨를 부딪친 사람이 사과도 없이 내렸다" },
  "story_state": {
    "location": "2호선 합정역 승강장", "time": "월요일 오전 8시 20분", "weather": "흐림",
    "people": [], "threads": ["어젯밤 팀장의 메시지에 아직 답하지 않았다"]
  },
  "turn_count": 3,
  "soft_turn_limit": 30,
  "max_turns": 40,
  "has_prologue": true,
  "can_close": true,
  "turn_limit_reached": false,
  "last_choices": [
    { "index": 0, "text": "“괜찮습니다.” 웃으며 삼킨다", "attitude": "endure", "attitude_label": "참아내기" },
    { "index": 1, "text": "대답 대신 이어폰을 꽂는다", "attitude": "avoid", "attitude_label": "피하기" }
  ],
  "last_closure_suggested": false,
  "mood_history": [
    { "turn_number": 0, "turn_type": "prologue", "label": "권태", "valence": -1, "intensity": 3 },
    { "turn_number": 1, "turn_type": "action",   "label": "짜증", "valence": -1, "intensity": 4 }
  ],
  "attitude_counts": [ { "attitude": "endure", "label": "참아내기", "count": 2 } ],
  "created_at": "2026-09-10T14:23:01Z",
  "updated_at": "2026-09-10T14:30:00Z",
  "completed_at": null
}
```
| 칸 | 뜻 |
|---|---|
| `has_prologue` | 프롤로그가 저장됐는가. `false`면 프론트는 5-2를 부른다 |
| `can_close` | "여기서 맺기" 버튼을 켤지. `status = active` 이고 `turn_count ≥ 1` |
| `turn_limit_reached` | `turn_count ≥ max_turns`. `true`면 선택지·입력창을 숨기고 맺기만 보여준다 |
| `last_choices` | 가장 최근 턴의 선택지 (이어하기 할 때 바로 그림). 없으면 `[]` |
| `last_closure_suggested` | 가장 최근 턴이 "맺기 좋은 순간"이었는가 |
| `mood_history` | 턴별 `mood_after` (프롤로그 포함, 에필로그 포함). **감정의 파동** 그래프용 |

- 이야기 본문(서술)은 여기 없습니다. 4-4로 따로 불러옵니다.

### 4-4. 턴 기록 (책 본문)
```
GET /api/v1/sessions/{id}/turns?limit=20&before_turn=15
→ 200  TurnListResponse
{
  "turns": [
    {
      "id": "uuid",
      "turn_number": 14,
      "turn_type": "action",
      "input_kind": "choice",
      "player_input": "“괜찮습니다.” 웃으며 삼킨다",
      "attitude": "endure",
      "attitude_label": "참아내기",
      "narration": "입꼬리를 올리는 데에도 힘이 든다는 걸 처음 알았다...",
      "choices": [
        { "index": 0, "text": "화장실 거울 앞에서 한숨을 쉰다", "attitude": "let_go", "attitude_label": "흘려보내기" },
        { "index": 1, "text": "수진에게 메시지를 보낸다", "attitude": "open_up", "attitude_label": "털어놓기" }
      ],
      "closure_suggested": false,
      "mood_after": { "label": "서글픔", "valence": -1, "intensity": 3, "note": "..." },
      "safety_notice": false,
      "created_at": "2026-09-10T14:30:00Z"
    }
  ],
  "has_more": true
}
```
- `limit`: 1~50, 생략 시 20
- `before_turn`: 이 번호 **미만**의 턴만. 생략하면 가장 최근 턴부터
- 배열은 **오래된 것 → 최신 순**입니다. (책 읽는 순서 그대로. 최신 턴이 마지막)
- 프롤로그(0번)와 에필로그도 같은 목록에 들어 있습니다. `turn_type`으로 구분해서 그립니다.
  (프롤로그·에필로그는 `input_kind`, `player_input`, `attitude`가 `null`)
- `has_more`: 더 오래된 턴이 남아있으면 `true` → 가장 앞 턴의 `turn_number`를 `before_turn`으로 다시 요청
- 이 `Turn` 모양은 5장 `turn_completed` 이벤트 안의 `turn`과 **완전히 같은 모델**입니다.

### 4-5. 이야기 지우기
```
DELETE /api/v1/sessions/{id}
→ 204  (본문 없음)
```
- 실제로 지우지 않고 "삭제 표시"(`deleted_at`)만 합니다. 이후 목록·상세·턴 조회에서 404
- 턴을 쓰는 중이면 409 `TURN_IN_PROGRESS`

---

## 5. ⭐ 이야기 쓰기 (SSE 스트리밍) — 가장 중요

AI가 글을 쓰는 요청은 **3가지**이고, 셋 다 **같은 SSE 규칙**을 씁니다.

| 요청 | 주소 | 결과로 저장되는 턴 |
|---|---|---|
| 프롤로그 | `POST /api/v1/sessions/{id}/prologue` | `turn_type = prologue` (0번) |
| 행동 | `POST /api/v1/sessions/{id}/actions` | `turn_type = action` |
| 에필로그 | `POST /api/v1/sessions/{id}/epilogue` | `turn_type = epilogue` → 이야기 **완성** |

모든 요청에 `Accept: text/event-stream` 헤더를 붙입니다.

### 5-1. 요청 본문

```jsonc
// 프롤로그: PrologueRequest
{ "client_action_id": "브라우저가 만든 uuid" }

// 행동 — 선택지를 눌렀을 때: ActionRequest
{ "client_action_id": "uuid", "input_kind": "choice", "choice_index": 1, "content": null }

// 행동 — 직접 입력했을 때: ActionRequest
{ "client_action_id": "uuid", "input_kind": "free_text", "choice_index": null, "content": "그냥 오늘은 좀 힘들다고 말해버린다" }

// 에필로그: EpilogueRequest
{ "client_action_id": "uuid" }
```
- `input_kind = choice`: `choice_index` 필수(직전 턴 선택지 번호), `content`는 `null`
- `input_kind = free_text`: `content` 필수(앞뒤 공백 제거 후 1~200자), `choice_index`는 `null`
- 규칙에 안 맞으면 400 `VALIDATION_ERROR` (예: 선택지가 2개인데 `choice_index: 2`)

### 5-2. 검사 순서와 응답 방식 (백엔드는 이 순서를 지킵니다)

1. 인증 + 이야기 소유 확인 → 401 / 404
2. 요청 본문 검사 → 400
3. **재생 확인**: 아래에 해당하면 새로 쓰지 않고 **저장된 턴을 재생**(5-4). 아래 검사 생략
   - 같은 `client_action_id`로 저장된 턴이 있다
   - (프롤로그 요청인데) 이미 프롤로그가 있다 / (에필로그 요청인데) 이미 에필로그가 있다
4. 이야기가 완성됨 → 422 `SESSION_ALREADY_COMPLETED`
5. 요청별 조건
   - 행동·에필로그인데 프롤로그가 없다 → 409 `PROLOGUE_REQUIRED`
   - 행동인데 `turn_count ≥ max_turns` → 422 `TURN_LIMIT_REACHED`
   - 에필로그인데 `turn_count = 0` → 422 `EPILOGUE_NOT_ALLOWED_YET`
6. 턴 잠금 획득 실패 → 409 `TURN_IN_PROGRESS`
7. 통과 → HTTP 200 + SSE 스트림 시작

> ⚠️ **1~6에서 거절되면 SSE가 아니라 일반 JSON 에러 응답**(0장 모양)이 옵니다.
> 프론트는 `response.ok`를 먼저 확인하고, `true`일 때만 스트림을 읽습니다.

### 5-3. `client_action_id` 규칙 (중복 방지)

**`client_action_id` 1개 = 유저가 버튼을 1번 누른 것** (선택지 클릭, 전송, "여기서 맺기", 프롤로그 시작).
- 네트워크 문제로 **같은 클릭을 자동 재전송**할 때 → 같은 id
- 유저가 **다시 버튼을 누르면** → 새 id

| 상황 | 결과 |
|---|---|
| 처음 보는 id + 조건 통과 | 새 턴을 씀 (SSE) |
| 이 id로 **저장된 턴이 있음** | 새로 쓰지 않고 **저장된 결과를 재생** |
| 이 id가 **아직 처리 중** (또는 다른 턴이 처리 중) | 409 `TURN_IN_PROGRESS` |
| 이 id의 이전 시도가 **실패해서 저장 안 됨** | 저장된 게 없으므로 새로 씀 (재시도 허용) |

- 프롤로그·에필로그는 이야기마다 하나뿐이라, **id가 달라도 이미 있으면 재생**합니다. (새로고침해도 안전)
- 브라우저에서 uuid는 `crypto.randomUUID()`로 만듭니다.
  ⚠️ 이 함수는 **https 또는 localhost에서만** 동작합니다. 휴대폰으로 `http://192.168.x.x:3000` 에 접속해 테스트하면 에러가 납니다.
  → 프론트는 `crypto.randomUUID`가 없을 때 쓸 대체 함수를 함께 둡니다.

### 5-4. 재생(replay) 스트림
저장된 턴을 다시 보낼 때도 **같은 이벤트 순서**를 씁니다. 차이점은 두 가지뿐입니다.
- `narration_delta`가 **전체 서술을 담아 1번만** 옵니다.
- `turn_completed`의 `session`은 **지금 이 순간의 이야기 상태**입니다.

### 5-5. SSE 전송 형식 (양쪽 공통)

```
event: <이벤트이름>\n
data: <한 줄짜리 JSON>\n
\n
```
- `data`는 **항상 한 줄의 JSON**입니다. (서술 속 줄바꿈은 JSON 안에서 `\n`으로 이스케이프되어 옴)
- 이벤트와 이벤트 사이는 **빈 줄**로 구분합니다. 프론트 파서는 `\r\n`도 `\n`과 똑같이 처리합니다.
- **`:`로 시작하는 줄은 주석(heartbeat)** 입니다. 프론트 파서는 무시합니다. (5-7)
- 응답 헤더: `Content-Type: text/event-stream`, `Cache-Control: no-cache`, `X-Accel-Buffering: no`
- 한글이 청크 경계에서 잘릴 수 있으므로 프론트는 `new TextDecoder("utf-8")`의 `decode(chunk, { stream: true })`로 읽습니다.

### 5-6. 이벤트 (4종뿐)

```
turn_started → narration_delta × N(1번 이상) → turn_completed
                     (어느 시점이든 실패하면) → error  (그리고 스트림 종료)
```

> 💡 **이벤트를 4개로 줄인 이유**: 이벤트 종류가 많을수록 "중간 이벤트를 놓쳤을 때" 경우의 수가 늘어납니다.
> 선택지·감정·이야기 상태는 전부 **마지막 `turn_completed` 하나에 담아** 보냅니다.
> 프론트는 "서술은 흘려 받고, 나머지는 끝에 한 번에 받는다"만 기억하면 됩니다.

#### ① turn_started — `TurnStartedData`
```
event: turn_started
data: {"turn_id":"uuid","turn_number":15,"turn_type":"action"}
```
> ⚠️ 이 `turn_id`는 **아직 DB에 저장되지 않은 번호**입니다. 턴이 끝까지 성공해야 저장됩니다.

#### ② narration_delta (1번 이상) — `NarrationDeltaData`
```
event: narration_delta
data: {"text":"입꼬리를 올리는 데에도 "}

event: narration_delta
data: {"text":"힘이 든다는 걸 처음 알았다."}
```
> ⚠️ `text`를 **그대로 이어붙이면** 전체 서술이 됩니다. 공백과 줄바꿈도 이미 포함돼 있습니다.
> 프론트가 임의로 공백을 넣거나 trim 하면 안 됩니다.
> ⚠️ 몇 번 나눠 올지는 정해져 있지 않습니다. **전체가 1번에 올 수도 있습니다.** (Step 5~6과 재생 시)

#### ③ turn_completed (성공 시 반드시 마지막에 1번) — `TurnCompletedData`
```
event: turn_completed
data: {"turn":{ ...4-4의 Turn 객체 그대로... },"session":{"status":"active","title":null,"mood":{...},"story_state":{...},"turn_count":15,"can_close":true,"turn_limit_reached":false}}
```
| 부분 | 모델 | 뜻 |
|---|---|---|
| `turn` | `Turn` | **방금 저장된 턴 전체** (서술 전체, 선택지, 태도, `mood_after`, `safety_notice` 포함). 4-4 목록의 항목과 같은 모양 |
| `session` | `SessionState` | 턴이 끝난 뒤의 이야기 상태 (`status`, `title`, `mood`, `story_state`, `turn_count`, `can_close`, `turn_limit_reached`) |

> 🚨 **화면의 최종 값은 반드시 `turn_completed`로 덮어씁니다.**
> 스트리밍으로 이어붙인 서술도 `turn.narration`으로 **교체**합니다. (중간 조각을 하나 놓쳐도 화면이 DB와 같아지는 안전장치)
- 프롤로그·행동: `turn.choices`를 선택지로 그리고, `turn.closure_suggested`가 `true`면 "여기서 맺기"를 은은하게 강조
- 에필로그: `session.status = "completed"`, `session.title`에 제목 → 프론트는 **마지막 페이지 화면**(제목 + 감정의 파동 + 오늘의 태도)으로 전환
- `turn.safety_notice`가 `true`면 도움 안내를 조용히 함께 보여줌 (02번 문서 9장, 09번 문서)

#### ④ error (실패 시. 이 이벤트 뒤 스트림 종료) — `SseErrorData`
```
event: error
data: {"code":"LLM_UNAVAILABLE","message":"잠시 이야기가 끊겼어요. 조금 뒤에 다시 이어 써볼까요?"}
```
- `code`: `LLM_UNAVAILABLE` 또는 `INTERNAL_ERROR`
> ⚠️ 스트림이 이미 시작된 뒤에는 HTTP 상태코드를 바꿀 수 없습니다. 그래서 **에러도 SSE 이벤트로** 보냅니다.
> 프론트는 두 가지 실패를 모두 처리해야 합니다. (① 요청 자체가 거부된 4xx 응답 ② 스트림 도중의 `error` 이벤트)

🚨 **`error`가 온 턴은 DB에 저장되지 않았습니다.** (`turn_started`에서 받은 `turn_id`는 없던 번호가 됩니다)
→ 프론트는 중간까지 나온 서술을 **지우고**, 직접 입력이었다면 그 문장을 **입력창에 되돌려** 다시 보낼 수 있게 합니다. 이야기 상태도 바뀌지 않았습니다.

### 5-7. heartbeat (연결 유지 신호)
AI가 생각하는 동안 첫 글자가 나오기 전에 한참 조용할 수 있습니다.
백엔드는 스트림이 열려 있는 동안 **15초마다** 아래 한 줄을 보냅니다.
```
: ping\n
\n
```
- 프론트는 이 줄을 화면에 쓰지 않고 무시하되, **"아직 살아있음"으로 보고 타임아웃 시계를 다시 0부터** 셉니다.

### 5-8. 연결이 끊겼을 때
- 유저가 페이지를 떠나 **프론트가 연결을 끊으면**(AbortController), 백엔드는 처리를 멈춥니다.
  - 아직 DB 저장 전이었다면 → 아무것도 저장되지 않음, 잠금 해제
  - 이미 저장이 끝난 뒤였다면 → 턴은 저장되어 있음
- 그래서 프론트는 **`turn_completed`를 못 받고 끊긴 모든 경우**에 `GET /sessions/{id}`와 `GET /sessions/{id}/turns`로 화면을 다시 맞춥니다.

### 5-9. 프론트엔드 처리 체크리스트
- [ ] `EventSource`는 헤더를 못 붙이므로 쓰지 않는다. `fetch` + `ReadableStream`으로 직접 파싱한다
- [ ] 세 요청(프롤로그·행동·에필로그)은 **같은 스트림 처리 함수 하나**로 다룬다
- [ ] `response.ok`가 아니면 0장 JSON 에러로 처리한다
- [ ] 스트림 도중 유저가 페이지를 떠나면 `AbortController`로 연결 종료
- [ ] 30초 동안 아무 데이터(heartbeat 포함)도 안 오면 타임아웃 처리
- [ ] `turn_completed` 없이 스트림이 끊기면 → "다시 불러오기" 안내 후 5-8 방식으로 복구
- [ ] `error` 이벤트면 중간 서술을 지우고, 직접 입력 문장을 입력창에 되돌린다
- [ ] 쓰는 중에는 선택지·입력창·맺기 버튼 비활성화 (연타 방지)

---

## 6. 타입 자동 생성 파이프라인 (Step 3에서 구축)

```
백엔드                                      프론트엔드
Pydantic 모델                               src/types/api.ts (자동 생성, 손대지 않음)
   │                                              ▲
   └─ FastAPI가 /openapi.json 생성 ────────────────┘
        (openapi-typescript 로 변환 → npm run gen:api)
```

```bash
# frontend/package.json 의 scripts 에 등록해서 씀
"gen:api": "openapi-typescript http://localhost:8000/openapi.json -o src/types/api.ts"
```

> 🚨 **`src/types/api.ts`는 절대 손으로 고치지 않습니다.**
> 고쳐야 한다면 백엔드의 Pydantic 모델을 고치고 위 명령을 다시 실행합니다.
> (자동 생성된 타입에 짧은 별명을 붙이는 파일 `src/types/index.ts`는 손으로 써도 됩니다.
>  예: `export type Turn = components["schemas"]["Turn"]` — **모양을 새로 정의하는 것은 금지**)

### SSE 이벤트 타입도 자동 생성한다
SSE 이벤트는 원래 OpenAPI 문서에 나타나지 않습니다. 그래서 **문서 전용 엔드포인트**를 하나 둡니다.
```
GET /api/v1/_schema/sse-events   (인증 불필요, 실제 화면에서 호출하지 않음)
→ 200  SseEventCatalog
{
  "turn_started":    TurnStartedData,
  "narration_delta": NarrationDeltaData,
  "turn_completed":  TurnCompletedData,
  "error":           SseErrorData
}
```
→ 이 엔드포인트의 `response_model`로 등록된 모델들이 `/openapi.json`에 포함되어, **SSE 데이터 타입도 `api.ts`에 자동으로 생깁니다.**
→ 프론트/백엔드가 손으로 맞추는 지점이 **0개**가 됩니다. (이벤트 **이름** 4개만 이 문서를 보고 맞춤)

### 백엔드 모델 이름표 (⚠️ 이 이름 그대로. 이름이 곧 프론트의 타입 이름)

| 용도 | Pydantic 클래스 이름 |
|---|---|
| 공통 | `PremiseItem`, `Premise`, `Mood`, `MoodPoint`, `Person`, `StoryState`, `Choice`, `AttitudeCount`, `ErrorResponse` |
| 2~3장 | `Me`, `OnboardingOptions`, `OnboardingField`, `OnboardingPreset`, `AttitudeInfo` |
| 4장 | `SessionCreateRequest`, `SessionDetail`, `SessionListItem`, `Turn`, `TurnListResponse` |
| 5장 | `PrologueRequest`, `ActionRequest`, `EpilogueRequest`, `SessionState`, `TurnStartedData`, `NarrationDeltaData`, `TurnCompletedData`, `SseErrorData`, `SseEventCatalog` |

- 코드값(태도·턴 종류·입력 방식·이야기 상태·`flavor_code`)은 `Literal[...]`로 정의합니다. → 프론트에서 `"endure" | "avoid" | ...` 같은 정확한 타입이 됩니다.
- `FastAPI(..., separate_input_output_schemas=False)`로 생성합니다.
  (안 하면 같은 모델이 `Premise-Input` / `Premise-Output` 두 개로 쪼개져 이름표가 깨질 수 있음)

---

## 7. CORS 설정 (백엔드)

```python
allow_origins = settings.cors_origins   # 환경변수 CORS_ORIGINS (쉼표로 구분)
# 개발: "http://localhost:3000"
# 운영: "http://localhost:3000,https://<vercel-도메인>"  (배포 시 추가)
allow_credentials = False   # 쿠키가 아니라 Authorization 헤더를 쓰므로 필요 없음
allow_methods = ["*"]
allow_headers = ["*"]
```
> ⚠️ `allow_origins=["*"]`는 쓰지 않습니다. 허용 주소는 항상 명시 목록으로 제한합니다.

---

## 변경 이력
- 2026-09-10: 최초 작성 (아키텍처 세션) — 주사위 TRPG 기준
- 2026-09-11: 설계 보완 (아키텍처 세션) — 에러 코드 목록, 멱등성 상황표, heartbeat, SSE 타입 자동 생성 등
- 2026-09-11: **전면 재작성** (아키텍처 세션) — `GAME_CONCEPT.md`(여백) 반영
  - 제거: 캐릭터·시나리오·게임 규칙표 API, 주사위·상태 패치 이벤트
  - 추가: 온보딩 옵션 API, 이야기 만들기(온보딩 제출), 목록(이어 쓰는 중 / 여백의 서재), 이야기 지우기
  - 변경: AI 글쓰기를 프롤로그 / 행동(선택지·직접 입력) / 에필로그 3개 스트림으로. 공통 SSE 이벤트를 4종(turn_started, narration_delta, turn_completed, error)으로 축소하고 `turn_completed`에 저장된 턴 전체 + 이야기 상태를 담음
  - 에러 코드 정리: `CONTENT_NOT_ALLOWED`, `PROLOGUE_REQUIRED`, `SESSION_ALREADY_COMPLETED`, `TURN_LIMIT_REACHED`, `EPILOGUE_NOT_ALLOWED_YET` 추가
