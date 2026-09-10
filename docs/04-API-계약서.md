# 04. API 계약서 ⭐ 가장 중요한 문서

> 🎯 **이 문서는 프론트엔드 세션과 백엔드 세션 사이의 "계약서"입니다.**
> 두 세션은 서로의 코드를 볼 수 없습니다. 이 문서만 봅니다.
> 💡 **여기 없는 API는 존재하지 않는 것입니다.**
> 필요하면 아키텍처 세션에 요청해서 이 문서에 먼저 추가하세요.

---

## 0. 공통 규칙

### 기본 주소
```
개발:  http://localhost:8000
운영:  https://project-seoul-api.onrender.com  (Step 11에서 확정)
```

### 모든 요청의 공통 헤더
```
Authorization: Bearer <Supabase access token>
Content-Type: application/json
```
(`/health` 만 예외 — 인증 불필요)

### 성공 응답
HTTP 200 또는 201. 본문은 각 API에 정의된 객체 그대로.
(`{ "data": ... }` 같은 껍데기로 감싸지 **않습니다**. 불필요한 한 겹입니다.)

### 실패 응답 (모든 실패는 이 모양)
```json
{
  "error": {
    "code": "SESSION_NOT_FOUND",
    "message": "게임 세션을 찾을 수 없습니다.",
    "detail": null
  }
}
```

| HTTP | 언제 | 대표 code |
|---|---|---|
| 400 | 입력값이 규칙에 안 맞음 | `VALIDATION_ERROR` |
| 401 | 토큰 없음/만료 | `UNAUTHORIZED` |
| 403 | 남의 것에 접근 | `FORBIDDEN` |
| 404 | 없는 리소스 | `*_NOT_FOUND` |
| 409 | 이미 처리 중 | `TURN_IN_PROGRESS` |
| 422 | 게임 규칙 위반 | `SESSION_ALREADY_ENDED` |
| 429 | 너무 자주 요청 | `RATE_LIMITED` |
| 500 | 서버 잘못 | `INTERNAL_ERROR` |
| 503 | AI 응답 실패/타임아웃 | `LLM_UNAVAILABLE` |

**프론트엔드는 `error.code`로 분기하고, `error.message`를 그대로 화면에 띄웁니다.**
백엔드는 `message`를 항상 **유저에게 보여줘도 되는 한글 문장**으로 씁니다. (스택트레이스 노출 금지)

### 시간 형식
모든 시각은 **ISO 8601 UTC** 문자열: `"2026-09-10T14:23:01Z"`
(한국 시간 변환은 프론트엔드가 표시할 때 합니다.)

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
→ 200
{
  "id": "uuid",
  "nickname": "원강",
  "created_at": "2026-09-10T14:23:01Z"
}
```
- 프로필이 아직 없으면 **자동 생성**해서 돌려줍니다. (프론트가 별도 처리 안 하게)

---

## 3. 캐릭터

### 3-1. 목록
```
GET /api/v1/characters
→ 200
[
  {
    "id": "uuid",
    "name": "박준서",
    "occupation": "journalist",
    "occupation_label": "기자",
    "background": "3년차 사회부 기자...",
    "stats": { "strength":2, "agility":3, "intellect":4,
               "perception":4, "charm":2, "will":1 },
    "created_at": "2026-09-10T14:23:01Z"
  }
]
```
> 💡 `occupation`(코드)과 `occupation_label`(한글)을 **둘 다** 보냅니다.
> 프론트가 코드→한글 변환표를 따로 관리하면 두 곳이 어긋납니다.

### 3-2. 생성
```
POST /api/v1/characters
{
  "name": "박준서",
  "occupation": "journalist",
  "background": "3년차 사회부 기자...",
  "stats": { "strength":2, "agility":3, "intellect":4,
             "perception":4, "charm":2, "will":1 }
}
→ 201  (3-1과 같은 객체 1개)
```
**백엔드 검증 (실패 시 400 `VALIDATION_ERROR`)**
- `name`: 1~20자
- `background`: 0~500자
- `occupation`: 정해진 6개 중 하나
- `stats`: 6개 키 모두 존재, 각 1~5, **합계 정확히 15**

### 3-3. 삭제
```
DELETE /api/v1/characters/{id}
→ 204
```
- 진행 중(`active`)인 세션이 있으면 409 `CHARACTER_IN_USE`

---

## 4. 시나리오

```
GET /api/v1/scenarios
→ 200
[
  {
    "id": "uuid",
    "title": "을지로 3가의 실종자",
    "summary": "3주 전 사라진 동료의 마지막 문자가 도착한다.",
    "tags": ["미스터리", "도시"],
    "estimated_turns": 30,
    "difficulty": "normal"
  }
]
```

---

## 5. 게임 세션

### 5-1. 시작
```
POST /api/v1/sessions
{ "character_id": "uuid", "scenario_id": "uuid" }
→ 201
{
  "id": "uuid",
  "status": "active",
  "turn_count": 0,
  "character": { ...3-1 객체... },
  "scenario": { ...4번 객체... },
  "resources": {
    "hp": 100, "max_hp": 100,
    "mental": 100, "max_mental": 100,
    "money": 500000,
    "inventory": [{ "name":"휴대폰", "quantity":1, "description":"배터리 62%" }]
  },
  "world_state": {
    "location": "을지로3가역 1번 출구",
    "datetime_in_game": "2026-03-14 22:40",
    "weather": "비",
    "present_npcs": [],
    "flags": {}
  },
  "opening_narration": "빗줄기가 굵어진다. 당신은...",
  "created_at": "2026-09-10T14:23:01Z"
}
```
> ⚠️ **이 요청은 AI를 호출하지 않습니다.** `opening_narration`은 DB의 고정 텍스트입니다.
> → 즉시(1초 이내) 응답합니다.

### 5-2. 내 세션 목록
```
GET /api/v1/sessions?status=active
→ 200  [ { "id", "status", "turn_count", "character_name",
           "scenario_title", "summary_so_far", "updated_at" } ]
```

### 5-3. 세션 상세 (이어하기용)
```
GET /api/v1/sessions/{id}
→ 200  (5-1과 같은 객체 + "last_narration": "...")
```

### 5-4. 턴 기록 (스크롤 히스토리)
```
GET /api/v1/sessions/{id}/turns?limit=20&before_turn=15
→ 200
{
  "turns": [
    {
      "id": "uuid",
      "turn_number": 14,
      "player_input": "알바생에게 사진을 보여준다",
      "dice_check": {
        "stat": "charm", "stat_label": "매력",
        "skill_label": "설득",
        "dice": 11, "modifier": 4, "total": 15,
        "difficulty": 14, "difficulty_label": "보통",
        "outcome": "success", "outcome_label": "성공"
      },
      "narration": "알바생의 표정이 굳는다...",
      "state_patch": { "resources": { "mental": -3 },
                       "world_state": { "flags": { "met_sujin": true } } },
      "suggestions": ["더 캐묻는다", "명함을 건넨다", "물러난다"],
      "created_at": "2026-09-10T14:30:00Z"
    }
  ],
  "has_more": true
}
```
- 최신 턴이 배열의 **마지막**입니다. (화면에 그리는 순서 그대로)
- `dice_check`가 `null`이면 판정 없는 턴입니다.

### 5-5. 세션 종료
```
POST /api/v1/sessions/{id}/end
→ 200 { "id", "status": "ended_by_user", "summary_so_far": "..." }
```

---

## 6. ⭐ 행동 전송 (SSE 스트리밍) — 가장 중요

```
POST /api/v1/sessions/{id}/actions
Accept: text/event-stream

{
  "client_action_id": "브라우저가 만든 uuid",
  "content": "알바생에게 실종자 사진을 보여주며 본 적 있냐고 묻는다"
}
```

### 요청 검증
- `content`: 1~500자 (초과 시 400)
- `client_action_id`: uuid 형식. **같은 값이 다시 오면 새 턴을 만들지 않고 기존 결과를 다시 스트리밍**
- 세션이 `processing` 이면 409 `TURN_IN_PROGRESS`
- 세션이 종료 상태면 422 `SESSION_ALREADY_ENDED`

### 응답: SSE 이벤트 순서 (이 순서가 보장됩니다)

```
turn_started → [dice_roll]? → narration_delta × N → [state_patch]? → [suggestions]? → turn_completed
```
(`[ ]?` 표시는 "있을 수도, 없을 수도 있음"이라는 뜻입니다.)

#### ① turn_started
```
event: turn_started
data: {"turn_id":"uuid","turn_number":15}
```

#### ② dice_roll (판정이 있을 때만)
```
event: dice_roll
data: {"stat":"charm","stat_label":"매력","skill_label":"설득",
       "dice":11,"modifier":4,"total":15,
       "difficulty":14,"difficulty_label":"보통",
       "outcome":"success","outcome_label":"성공"}
```
> 💡 프론트는 이 이벤트를 받으면 **주사위 굴리는 연출**을 보여줍니다.
> 서술보다 먼저 오므로 "굴린다 → 결과 → 이야기" 순서가 자연스럽습니다.

#### ③ narration_delta (여러 번 옴)
```
event: narration_delta
data: {"text":"알바생의 "}

event: narration_delta
data: {"text":"표정이 굳는다."}
```
> ⚠️ `text`를 **그대로 이어붙이면** 전체 서술이 됩니다. 공백과 줄바꿈도 이미 포함돼 있습니다.
> 프론트가 임의로 공백을 넣거나 trim 하면 안 됩니다.

#### ④ state_patch (변화가 있을 때만)
```
event: state_patch
data: {"resources":{"mental":-3},
       "world_state":{"present_npcs":["김수진"],"flags":{"met_sujin":true}}}
```
> ⚠️ `resources`의 숫자는 **변화량(델타)**입니다. `mental: -3` = 3 감소.
> `world_state`의 값은 **덮어쓸 값**이고, 그 안의 `flags`만 병합(merge)입니다.

#### ⑤ suggestions (선택)
```
event: suggestions
data: {"items":["더 캐묻는다","명함을 건넨다","물러난다"]}
```

#### ⑥ turn_completed (반드시 마지막에 1번)
```
event: turn_completed
data: {"turn_id":"uuid","turn_number":15,
       "session_status":"active",
       "resources":{"hp":100,"max_hp":100,"mental":97,"max_mental":100,
                    "money":500000,"inventory":[]},
       "world_state":{}}
```
> 🚨 **여기 담긴 값은 "변화량"이 아니라 "최종 전체 상태"입니다.**
> 프론트는 `state_patch`로 부드러운 증감 애니메이션을 주되,
> **최종 화면 값은 반드시 `turn_completed`의 값으로 덮어씁니다.**
> → 중간 이벤트를 하나 놓쳐도 화면이 DB와 어긋나지 않게 하는 안전장치입니다.

#### ⑦ error (실패 시. 이 이벤트 뒤 스트림 종료)
```
event: error
data: {"code":"LLM_UNAVAILABLE","message":"AI 응답에 실패했습니다. 잠시 후 다시 시도해주세요."}
```
> ⚠️ 스트림이 이미 시작된 뒤에는 HTTP 상태코드를 바꿀 수 없습니다.
> 그래서 **에러도 SSE 이벤트로** 보냅니다. 프론트는 두 가지 실패를 모두 처리해야 합니다.
> (① 요청 자체가 거부된 4xx 응답 ② 스트림 도중의 `error` 이벤트)

### 프론트엔드 처리 체크리스트
- [ ] 스트림 도중 유저가 페이지를 떠나면 `AbortController`로 연결 종료
- [ ] 30초 동안 아무 이벤트도 안 오면 타임아웃 처리
- [ ] `turn_completed` 없이 스트림이 끊기면 → "다시 불러오기" 버튼 노출 후 `GET /sessions/{id}`로 복구
- [ ] 전송 중에는 입력창 비활성화 (연타 방지)

---

## 7. 타입 자동 생성 파이프라인 (Step 3에서 구축)

```
백엔드                                      프론트엔드
Pydantic 모델                               src/types/api.ts (자동 생성, 손대지 않음)
   │                                              ▲
   └─ FastAPI가 /openapi.json 생성 ────────────────┘
        (npx openapi-typescript 로 변환)
```

```bash
npx openapi-typescript http://localhost:8000/openapi.json -o src/types/api.ts
```

> 🚨 **`src/types/api.ts`는 절대 손으로 고치지 않습니다.**
> 고쳐야 한다면 백엔드의 Pydantic 모델을 고치고 위 명령을 다시 실행합니다.

⚠️ **SSE 이벤트는 OpenAPI 문서로 표현되지 않습니다.**
→ SSE 이벤트 타입만은 프론트/백엔드가 각자 손으로 정의하되,
   **6장의 정의를 그대로** 옮깁니다. 여기가 유일한 수동 동기화 지점입니다.

---

## 8. CORS 설정 (백엔드)

```python
allow_origins = [
    "http://localhost:3000",        # 로컬 개발
    "https://<vercel-도메인>",       # 운영 (Step 11에서 추가)
]
allow_credentials = True
allow_methods = ["*"]
allow_headers = ["*"]
```
> ⚠️ `allow_origins=["*"]`는 쓰지 않습니다. 인증 토큰을 쓰는 API에서는 브라우저가 거부합니다.

---

## 변경 이력
- 2026-09-10: 최초 작성 (아키텍처 세션)
