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
운영:  https://project-seoul-api.onrender.com  (배포 시 확정)
```
- 프론트엔드는 이 주소를 코드에 적지 않고 환경변수 `NEXT_PUBLIC_API_BASE_URL`로 읽습니다. (01번 문서 9장)
- **브라우저가 FastAPI를 직접 호출합니다.** (Next.js 서버를 중간에 거치지 않음)

### 모든 요청의 공통 헤더
```
Authorization: Bearer <Supabase access token>
Content-Type: application/json
```
(`/health` 만 예외 — 인증 불필요)

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
    "message": "게임 세션을 찾을 수 없습니다.",
    "detail": null
  }
}
```
- `code`: 아래 표의 값 중 하나 (영어 대문자)
- `message`: **유저에게 그대로 보여줘도 되는 한글 문장** (스택트레이스·SQL·영어 에러 원문 노출 금지)
- `detail`: 보통 `null`. `VALIDATION_ERROR`일 때만 `[{ "field": "stats", "message": "능력치 합계는 15여야 합니다." }]`

### 에러 코드 전체 목록 (이 표에 없는 code는 쓰지 않는다)

| code | HTTP | 언제 |
|---|---|---|
| `VALIDATION_ERROR` | 400 | 입력 형식·길이·규칙 위반 (합계 15 아님 등) |
| `UNAUTHORIZED` | 401 | 토큰 없음 / 만료 / 위조 |
| `NOT_FOUND` | 404 | 없는 주소로 요청 |
| `CHARACTER_NOT_FOUND` | 404 | 캐릭터가 없음 / 삭제됨 / **남의 것** |
| `SCENARIO_NOT_FOUND` | 404 | 시나리오가 없음 / 비공개 |
| `SESSION_NOT_FOUND` | 404 | 세션이 없음 / **남의 것** |
| `CHARACTER_IN_USE` | 409 | 진행 중인 세션이 있는 캐릭터를 삭제하거나 새 세션에 쓰려 함 |
| `TURN_IN_PROGRESS` | 409 | 이 세션에서 이미 턴이 처리 중 |
| `SESSION_ALREADY_ENDED` | 422 | 끝난 세션에 행동/종료 요청 |
| `RATE_LIMITED` | 429 | 너무 자주 요청 (배포 단계에서 도입) |
| `INTERNAL_ERROR` | 500 | 서버 내부 오류 |
| `LLM_UNAVAILABLE` | 503 | AI 응답 실패/타임아웃 (주로 SSE `error` 이벤트로 옴) |

> 💡 **남의 것에 접근하면 403이 아니라 404를 줍니다.**
> 403("권한 없음")을 주면 "그 번호의 세션이 존재는 한다"는 정보가 새어나갑니다.
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
- **유일한 예외**: `world_state.datetime_in_game` — 게임 속 시각이라 `"YYYY-MM-DD HH:mm"` 그대로 표시 (02번 문서 5장)

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

## 3. 게임 규칙표 (프론트가 표를 따로 들고 있지 않게)

```
GET /api/v1/meta/game-rules
→ 200  GameRules
{
  "stats": [
    { "code": "strength",   "label": "근력", "description": "몸싸움, 버티기, 힘쓰기" },
    { "code": "agility",    "label": "민첩", "description": "도주, 손재주, 회피" },
    { "code": "intellect",  "label": "지능", "description": "지식, 추리, 기계" },
    { "code": "perception", "label": "감각", "description": "관찰, 눈치, 직감" },
    { "code": "charm",      "label": "매력", "description": "설득, 협상, 호감" },
    { "code": "will",       "label": "의지", "description": "공포 저항, 집중, 인내" }
  ],
  "stat_allocation": { "min": 1, "max": 5, "total": 15 },
  "occupations": [
    { "code": "office_worker", "label": "회사원", "bonus_label": "소지금 +200,000원",
      "stat_bonus": {}, "money_bonus": 200000 },
    { "code": "journalist", "label": "기자", "bonus_label": "감각 +1",
      "stat_bonus": { "perception": 1 }, "money_bonus": 0 }
  ],
  "difficulties": [
    { "code": "easy", "label": "쉬움", "dc": 10 },
    { "code": "normal", "label": "보통", "dc": 14 },
    { "code": "hard", "label": "어려움", "dc": 18 },
    { "code": "extreme", "label": "극한", "dc": 22 }
  ],
  "resource_labels": { "hp": "체력", "mental": "멘탈", "money": "소지금" },
  "limits": { "character_name_max": 20, "background_max": 500, "action_content_max": 500 }
}
```
(`occupations`는 실제로 6개 전부 포함. 예시는 2개만 적음)

> 💡 **왜 필요한가?** 캐릭터 생성 화면은 능력치 이름, 직업 목록, 보너스, 글자 수 제한을 알아야 합니다.
> 이걸 프론트가 코드에 따로 적으면, 백엔드에서 규칙을 바꿨을 때 **화면만 옛날 규칙**으로 남습니다.
> 규칙의 원본은 백엔드 한 곳(= 02번 문서를 옮긴 코드)이고, 프론트는 받아서 그리기만 합니다.

---

## 4. 캐릭터

### 4-1. 목록
```
GET /api/v1/characters
→ 200  Character[]   (삭제된 캐릭터 제외, 최신순)
[
  {
    "id": "uuid",
    "name": "박준서",
    "occupation": "journalist",
    "occupation_label": "기자",
    "background": "3년차 사회부 기자...",
    "stats":           { "strength":2, "agility":3, "intellect":4, "perception":4, "charm":1, "will":1 },
    "effective_stats": { "strength":2, "agility":3, "intellect":4, "perception":5, "charm":1, "will":1 },
    "has_active_session": false,
    "created_at": "2026-09-10T14:23:01Z"
  }
]
```
> 💡 `occupation`(코드)과 `occupation_label`(한글)을 **둘 다** 보냅니다.
> 프론트가 코드→한글 변환표를 따로 관리하면 두 곳이 어긋납니다.
> 💡 `stats`는 유저가 배분한 기본값(합계 15), `effective_stats`는 직업 보너스 적용값(최대 5). **화면의 능력치 표시는 `effective_stats`** 를 씁니다. (02번 문서 2장)
> 💡 `has_active_session`: 진행 중인 세션이 있으면 `true` → 프론트는 삭제 버튼을 비활성화하고 "이어하기"를 보여줄 수 있습니다.

### 4-2. 생성
```
POST /api/v1/characters
CharacterCreateRequest
{
  "name": "박준서",
  "occupation": "journalist",
  "background": "3년차 사회부 기자...",
  "stats": { "strength":2, "agility":3, "intellect":4, "perception":4, "charm":1, "will":1 }
}
→ 201  Character  (4-1과 같은 객체 1개)
```
**백엔드 검증 (실패 시 400 `VALIDATION_ERROR`)**
- `name`: 앞뒤 공백 제거 후 1~20자
- `background`: 0~500자
- `occupation`: 정해진 6개 중 하나
- `stats`: 6개 키 모두 존재(다른 키 없음), 각 1~5 정수, **합계 정확히 15** (보너스 적용 전 기준)

### 4-3. 삭제
```
DELETE /api/v1/characters/{id}
→ 204  (본문 없음)
```
- 실제로 지우지 않고 "삭제 표시"만 합니다. (03번 문서 2-2) → 지난 게임 기록은 그대로 남습니다.
- 진행 중(`active`/`processing`) 세션이 있으면 409 `CHARACTER_IN_USE`

---

## 5. 시나리오

```
GET /api/v1/scenarios
→ 200  Scenario[]   (is_public = true 인 것만)
[
  {
    "id": "uuid",
    "title": "을지로 3가의 실종자",
    "summary": "3주 전 사라진 동료의 마지막 문자가 도착한다.",
    "tags": ["미스터리", "도시"],
    "estimated_turns": 30,
    "difficulty": "normal",
    "difficulty_label": "보통"
  }
]
```
- `difficulty`: `easy` / `normal` / `hard` 중 하나
- ⚠️ `gm_guideline`, `goal_flags`, `opening_narration`은 이 목록에 **절대 포함하지 않습니다.** (스포일러)

---

## 6. 게임 세션

### 6-1. 시작
```
POST /api/v1/sessions
SessionCreateRequest
{ "character_id": "uuid", "scenario_id": "uuid" }
→ 201  SessionDetail
{
  "id": "uuid",
  "status": "active",
  "turn_count": 0,
  "max_turns": 100,
  "character": { ...4-1 Character 객체... },
  "scenario":  { ...5 Scenario 객체... },
  "resources": {
    "hp": 100, "max_hp": 100,
    "mental": 100, "max_mental": 100,
    "money": 300000,
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
  "last_narration": null,
  "last_suggestions": [],
  "created_at": "2026-09-10T14:23:01Z",
  "updated_at": "2026-09-10T14:23:01Z"
}
```
- 초기 `resources`는 02번 문서 3장 규칙대로 백엔드가 계산합니다. (예시는 기자 = 보너스 없음 → 300,000원)
- 에러: 캐릭터 없음/삭제/남의 것 → 404 `CHARACTER_NOT_FOUND`, 시나리오 없음/비공개 → 404 `SCENARIO_NOT_FOUND`,
  그 캐릭터가 이미 진행 중인 세션에 있음 → 409 `CHARACTER_IN_USE`

> ⚠️ **이 요청은 AI를 호출하지 않습니다.** `opening_narration`은 DB의 고정 텍스트입니다.
> → 즉시(1초 이내) 응답합니다.

### 6-2. 내 세션 목록
```
GET /api/v1/sessions?status=ongoing
→ 200  SessionListItem[]   (updated_at 최신순)
[
  {
    "id": "uuid",
    "status": "active",
    "turn_count": 14,
    "character_name": "박준서",
    "scenario_title": "을지로 3가의 실종자",
    "summary_so_far": "...",
    "updated_at": "2026-09-10T14:30:00Z"
  }
]
```
- `status` 파라미터: `ongoing`(= active + processing) / `ended`(= ended_* 4종) / `all`. 생략하면 `all`.

### 6-3. 세션 상세 (이어하기용)
```
GET /api/v1/sessions/{id}
→ 200  SessionDetail  (6-1과 같은 모양)
```
- `last_narration`: 가장 최근 턴의 서술. 턴이 하나도 없으면 `null` → 프론트는 `opening_narration`을 보여줌
- `last_suggestions`: 가장 최근 턴의 추천 행동. 없으면 `[]`
- 이전 대화 전체는 6-4로 따로 불러옵니다.

### 6-4. 턴 기록 (스크롤 히스토리)
```
GET /api/v1/sessions/{id}/turns?limit=20&before_turn=15
→ 200  TurnListResponse
{
  "turns": [
    {
      "id": "uuid",
      "turn_number": 14,
      "player_input": "알바생에게 사진을 보여준다",
      "dice_check": {
        "stat": "charm", "stat_label": "매력",
        "skill_label": "설득",
        "dice": 11, "modifier": 2, "total": 13,
        "difficulty": 14, "difficulty_label": "보통",
        "outcome": "failure", "outcome_label": "실패"
      },
      "narration": "알바생이 고개를 젓는다...",
      "state_patch": { ...7-5 ④ StatePatch 모양... },
      "suggestions": ["더 캐묻는다", "명함을 건넨다", "물러난다"],
      "created_at": "2026-09-10T14:30:00Z"
    }
  ],
  "has_more": true
}
```
- `limit`: 1~50, 생략 시 20
- `before_turn`: 이 번호 **미만**의 턴만. 생략하면 가장 최근 턴부터
- 배열은 **오래된 것 → 최신 순**입니다. (화면에 그리는 순서 그대로. 최신 턴이 마지막)
- `dice_check`가 `null`이면 판정 없는 턴입니다.
- `has_more`: 더 오래된 턴이 남아있으면 `true` → 프론트는 가장 앞 턴의 `turn_number`를 `before_turn`으로 다시 요청

### 6-5. 세션 종료
```
POST /api/v1/sessions/{id}/end
→ 200  SessionEndResponse
{ "id": "uuid", "status": "ended_by_user", "summary_so_far": "..." }
```
- 턴 처리 중이면 409 `TURN_IN_PROGRESS`, 이미 끝났으면 422 `SESSION_ALREADY_ENDED`

---

## 7. ⭐ 행동 전송 (SSE 스트리밍) — 가장 중요

```
POST /api/v1/sessions/{id}/actions
Accept: text/event-stream
ActionRequest
{
  "client_action_id": "브라우저가 만든 uuid",
  "content": "알바생에게 실종자 사진을 보여주며 본 적 있냐고 묻는다"
}
```

### 7-1. 요청 검증과 응답 방식

**검사 순서 (백엔드는 이 순서를 지킵니다)**
1. 인증 + 세션 소유 확인 → 실패 시 401 / 404
2. `content` 1~500자(앞뒤 공백 제거 후), `client_action_id` uuid 형식 → 실패 시 400
3. **같은 `client_action_id`로 이미 저장된 턴이 있나?** → 있으면 **재생**(7-3). 아래 검사 생략
4. 세션이 종료 상태 → 422 `SESSION_ALREADY_ENDED`
5. 턴 잠금 획득 실패 → 409 `TURN_IN_PROGRESS`
6. 통과 → HTTP 200 + SSE 스트림 시작

> ⚠️ **1~5에서 거절되면 SSE가 아니라 일반 JSON 에러 응답**(0장 모양)이 옵니다.
> 프론트는 `response.ok`를 먼저 확인하고, `true`일 때만 스트림을 읽습니다.

### 7-2. `client_action_id` 규칙 (중복 방지)

**`client_action_id` 1개 = 유저가 전송 버튼을 1번 누른 것.**
- 네트워크 문제로 **같은 클릭을 자동 재전송**할 때 → 같은 id
- 유저가 **다시 전송 버튼을 누르면** → 새 id

| 상황 | 결과 |
|---|---|
| 처음 보는 id + 세션 `active` | 새 턴 처리 (SSE) |
| 이 id로 **저장된 턴이 있음** | 새로 처리하지 않고 **저장된 결과를 재생** (7-3) |
| 이 id가 **아직 처리 중** (또는 다른 턴이 처리 중) | 409 `TURN_IN_PROGRESS` |
| 이 id의 이전 시도가 **실패해서 저장 안 됨** | 저장된 게 없으므로 새 턴으로 처리 (재시도 허용) |

- 브라우저에서 uuid는 `crypto.randomUUID()`로 만듭니다.
  ⚠️ 이 함수는 **https 또는 localhost에서만** 동작합니다. 휴대폰으로 `http://192.168.x.x:3000` 에 접속해 테스트하면 에러가 납니다.
  → 프론트는 `crypto.randomUUID`가 없을 때 쓸 대체 함수를 함께 둡니다.

### 7-3. 재생(replay) 스트림
저장된 턴을 다시 보낼 때도 **같은 이벤트 순서**를 씁니다. 차이점은 두 가지뿐입니다.
- `narration_delta`가 **전체 서술을 담아 1번만** 옵니다.
- `turn_completed`의 `resources`/`world_state`는 **지금 이 순간의 세션 상태**입니다.

### 7-4. SSE 전송 형식 (양쪽 공통)

```
event: <이벤트이름>\n
data: <한 줄짜리 JSON>\n
\n
```
- `data`는 **항상 한 줄의 JSON**입니다. (서술 속 줄바꿈은 JSON 안에서 `\n`으로 이스케이프되어 옴)
- 이벤트와 이벤트 사이는 **빈 줄**로 구분합니다. 프론트 파서는 `\r\n`도 `\n`과 똑같이 처리합니다.
- **`:`로 시작하는 줄은 주석(heartbeat)** 입니다. 프론트 파서는 무시합니다. (7-6)
- 응답 헤더: `Content-Type: text/event-stream`, `Cache-Control: no-cache`, `X-Accel-Buffering: no`
- 한글이 청크 경계에서 잘릴 수 있으므로 프론트는 `new TextDecoder("utf-8")`의 `decode(chunk, { stream: true })`로 읽습니다.

### 7-5. 이벤트 순서 (이 순서가 보장됩니다)

```
turn_started → [dice_roll]? → narration_delta × N(1번 이상) → [state_patch]? → [suggestions]? → turn_completed
                                           (어느 시점이든 실패하면) → error  (그리고 스트림 종료)
```
(`[ ]?` 표시는 "있을 수도, 없을 수도 있음"이라는 뜻입니다.)

#### ① turn_started — `TurnStartedData`
```
event: turn_started
data: {"turn_id":"uuid","turn_number":15}
```
> ⚠️ 이 `turn_id`는 **아직 DB에 저장되지 않은 번호**입니다. 턴이 끝까지 성공해야 저장됩니다.

#### ② dice_roll (판정이 있을 때만) — `DiceCheck`
```
event: dice_roll
data: {"stat":"charm","stat_label":"매력","skill_label":"설득","dice":11,"modifier":2,"total":13,"difficulty":14,"difficulty_label":"보통","outcome":"failure","outcome_label":"실패"}
```
- `modifier` = 실제 능력치(`effective_stats`) × 2, `total` = `dice` + `modifier`
- `outcome`: `critical_failure` / `failure` / `success` / `critical_success`
> 💡 프론트는 이 이벤트를 받으면 **주사위 굴리는 연출**을 보여줍니다.
> 서술보다 먼저 오므로 "굴린다 → 결과 → 이야기" 순서가 자연스럽습니다.
> 💡 이 모양은 6-4 턴 기록의 `dice_check`와 **완전히 같은 모델**(`DiceCheck`)입니다.

#### ③ narration_delta (1번 이상) — `NarrationDeltaData`
```
event: narration_delta
data: {"text":"알바생의 "}

event: narration_delta
data: {"text":"표정이 굳는다."}
```
> ⚠️ `text`를 **그대로 이어붙이면** 전체 서술이 됩니다. 공백과 줄바꿈도 이미 포함돼 있습니다.
> 프론트가 임의로 공백을 넣거나 trim 하면 안 됩니다.
> ⚠️ 몇 번 나눠 올지는 정해져 있지 않습니다. **전체가 1번에 올 수도 있습니다.** (Step 6과 재생 시)

#### ④ state_patch (변화가 있을 때만) — `StatePatch`
```
event: state_patch
data: {"resources":{"hp":0,"mental":-3,"money":0},"inventory":{"added":[{"name":"낡은 명함","quantity":1,"description":"을지로 인쇄소 명함"}],"removed":[]},"world_state":{"location":null,"datetime_in_game":null,"weather":null,"present_npcs":["김수진"],"flags":{"met_sujin":true}}}
```
**`StatePatch` 읽는 법 (키는 항상 3개 다 있음)**

| 부분 | 의미 | 변화 없음 표시 |
|---|---|---|
| `resources.hp` / `mental` / `money` | **변화량(델타)**. `-3` = 3 감소 | `0` |
| `inventory.added` | 추가된 아이템 (같은 이름이면 수량 합산) | `[]` |
| `inventory.removed` | 제거된 아이템 `{ "name", "quantity" }` | `[]` |
| `world_state.location` 등 일반 칸 | **새 값으로 덮어쓰기** | `null` |
| `world_state.present_npcs` | **목록 전체를 이 값으로 교체** | `null` |
| `world_state.flags` | **키 단위로 병합**(여기 있는 키만 갱신, 나머지 유지) | `{}` |

- 여기 담긴 값은 AI의 원래 제안이 아니라 **상한(clamp)까지 적용해 실제로 반영된 값**입니다.
- 이 모양은 6-4 턴 기록의 `state_patch`와 **완전히 같은 모델**입니다.

#### ⑤ suggestions (선택) — `SuggestionsData`
```
event: suggestions
data: {"items":["더 캐묻는다","명함을 건넨다","물러난다"]}
```
- 0~3개. 기록원 AI가 실패하면 이 이벤트는 오지 않습니다.

#### ⑥ turn_completed (성공 시 반드시 마지막에 1번) — `TurnCompletedData`
```
event: turn_completed
data: {"turn_id":"uuid","turn_number":15,"session_status":"active","resources":{"hp":100,"max_hp":100,"mental":97,"max_mental":100,"money":300000,"inventory":[{"name":"휴대폰","quantity":1,"description":"배터리 60%"},{"name":"낡은 명함","quantity":1,"description":"을지로 인쇄소 명함"}]},"world_state":{"location":"을지로3가 편의점","datetime_in_game":"2026-03-14 22:55","weather":"비","present_npcs":["김수진"],"flags":{"met_sujin":true}}}
```
> 🚨 **여기 담긴 값은 "변화량"이 아니라 "최종 전체 상태"입니다.**
> 프론트는 `state_patch`로 부드러운 증감 애니메이션을 주되,
> **최종 화면 값은 반드시 `turn_completed`의 값으로 덮어씁니다.**
> → 중간 이벤트를 하나 놓쳐도 화면이 DB와 어긋나지 않게 하는 안전장치입니다.
- `session_status`가 `ended_`로 시작하면 이 턴으로 게임이 끝난 것 → 프론트는 결과 화면(승리/패배/시간초과)을 보여줍니다.

#### ⑦ error (실패 시. 이 이벤트 뒤 스트림 종료) — `SseErrorData`
```
event: error
data: {"code":"LLM_UNAVAILABLE","message":"AI 응답에 실패했습니다. 잠시 후 다시 시도해주세요."}
```
- `code`: `LLM_UNAVAILABLE` 또는 `INTERNAL_ERROR`
> ⚠️ 스트림이 이미 시작된 뒤에는 HTTP 상태코드를 바꿀 수 없습니다.
> 그래서 **에러도 SSE 이벤트로** 보냅니다. 프론트는 두 가지 실패를 모두 처리해야 합니다.
> (① 요청 자체가 거부된 4xx 응답 ② 스트림 도중의 `error` 이벤트)

🚨 **`error`가 온 턴은 DB에 저장되지 않았습니다.** (`turn_started`에서 받은 `turn_id`는 없던 번호가 됩니다)
→ 프론트는 화면에서 그 턴(유저가 친 문장 + 중간까지 나온 서술)을 **지우고**,
   유저가 친 문장을 **입력창에 되돌려** 다시 보낼 수 있게 합니다. 세션 상태도 바뀌지 않았습니다.

### 7-6. heartbeat (연결 유지 신호)
판정·기억검색이 오래 걸리면 첫 글자가 나오기 전에 한참 조용할 수 있습니다.
백엔드는 스트림이 열려 있는 동안 **15초마다** 아래 한 줄을 보냅니다.
```
: ping\n
\n
```
- 프론트는 이 줄을 화면에 쓰지 않고 무시하되, **"아직 살아있음"으로 보고 타임아웃 시계를 다시 0부터** 셉니다.

### 7-7. 연결이 끊겼을 때
- 유저가 페이지를 떠나 **프론트가 연결을 끊으면**(AbortController), 백엔드는 처리를 멈춥니다.
  - 아직 DB 저장 전이었다면 → 아무것도 저장되지 않음, 잠금 해제
  - 이미 저장이 끝난 뒤였다면 → 턴은 저장되어 있음
- 그래서 프론트는 **`turn_completed`를 못 받고 끊긴 모든 경우**에 `GET /sessions/{id}`와 `GET /sessions/{id}/turns`로 화면을 다시 맞춥니다.

### 7-8. 프론트엔드 처리 체크리스트
- [ ] `EventSource`는 헤더를 못 붙이므로 쓰지 않는다. `fetch` + `ReadableStream`으로 직접 파싱한다
- [ ] `response.ok`가 아니면 0장 JSON 에러로 처리한다
- [ ] 스트림 도중 유저가 페이지를 떠나면 `AbortController`로 연결 종료
- [ ] 30초 동안 아무 데이터(heartbeat 포함)도 안 오면 타임아웃 처리
- [ ] `turn_completed` 없이 스트림이 끊기면 → "다시 불러오기" 버튼 노출 후 7-7 방식으로 복구
- [ ] `error` 이벤트면 해당 턴을 화면에서 지우고 입력 문장을 입력창에 되돌린다
- [ ] 전송 중에는 입력창·전송 버튼 비활성화 (연타 방지)

---

## 8. 타입 자동 생성 파이프라인 (Step 3에서 구축)

```
백엔드                                      프론트엔드
Pydantic 모델                               src/types/api.ts (자동 생성, 손대지 않음)
   │                                              ▲
   └─ FastAPI가 /openapi.json 생성 ────────────────┘
        (npx openapi-typescript 로 변환 → npm run gen:api)
```

```bash
# frontend/package.json 의 scripts 에 등록해서 씀
"gen:api": "openapi-typescript http://localhost:8000/openapi.json -o src/types/api.ts"
```

> 🚨 **`src/types/api.ts`는 절대 손으로 고치지 않습니다.**
> 고쳐야 한다면 백엔드의 Pydantic 모델을 고치고 위 명령을 다시 실행합니다.
> (자동 생성된 타입에 짧은 별명을 붙이는 파일 `src/types/index.ts`는 손으로 써도 됩니다.
>  예: `export type Character = components["schemas"]["Character"]` — **모양을 새로 정의하는 것은 금지**)

### SSE 이벤트 타입도 자동 생성한다
SSE 이벤트는 원래 OpenAPI 문서에 나타나지 않습니다. 그래서 **문서 전용 엔드포인트**를 하나 둡니다.
```
GET /api/v1/_schema/sse-events   (인증 불필요, 실제 화면에서 호출하지 않음)
→ 200  SseEventCatalog
{
  "turn_started":    TurnStartedData,
  "dice_roll":       DiceCheck,
  "narration_delta": NarrationDeltaData,
  "state_patch":     StatePatch,
  "suggestions":     SuggestionsData,
  "turn_completed":  TurnCompletedData,
  "error":           SseErrorData
}
```
→ 이 엔드포인트의 `response_model`로 등록된 모델들이 `/openapi.json`에 포함되어, **SSE 데이터 타입도 `api.ts`에 자동으로 생깁니다.**
→ 프론트/백엔드가 손으로 맞추는 지점이 **0개**가 됩니다. (이벤트 **이름** 7개만 이 문서를 보고 맞춤)

### 백엔드 모델 이름표 (⚠️ 이 이름 그대로. 이름이 곧 프론트의 타입 이름)

| 용도 | Pydantic 클래스 이름 |
|---|---|
| 공통 | `Stats`, `InventoryItem`, `Resources`, `WorldState`, `DiceCheck`, `StatePatch`, `ErrorResponse` |
| 2~3장 | `Me`, `GameRules` |
| 4장 | `Character`, `CharacterCreateRequest` |
| 5장 | `Scenario` |
| 6장 | `SessionCreateRequest`, `SessionDetail`, `SessionListItem`, `Turn`, `TurnListResponse`, `SessionEndResponse` |
| 7장 | `ActionRequest`, `TurnStartedData`, `NarrationDeltaData`, `SuggestionsData`, `TurnCompletedData`, `SseErrorData`, `SseEventCatalog` |

- 코드값(능력치·직업·난이도·결과·세션 상태)은 `Literal[...]`로 정의합니다. → 프론트에서 `"charm" | "will" | ...` 같은 정확한 타입이 됩니다.
- `FastAPI(..., separate_input_output_schemas=False)`로 생성합니다.
  (안 하면 같은 모델이 `Character-Input` / `Character-Output` 두 개로 쪼개져 이름표가 깨질 수 있음)

---

## 9. CORS 설정 (백엔드)

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
- 2026-09-10: 최초 작성 (아키텍처 세션)
- 2026-09-11: 설계 보완 (아키텍처 세션)
  - 추가: 에러 코드 전체 목록, 남의 리소스는 404 규칙, FastAPI 전역 예외 처리기 필수, 응답 키 생략 금지 규칙
  - 추가: `GET /api/v1/meta/game-rules`, 캐릭터 `effective_stats`·`has_active_session`, `/me`의 `email`
  - 추가: 세션 `max_turns`·`last_suggestions`·`updated_at`, 세션 목록 `status` 필터 값(ongoing/ended/all), 턴 기록 페이지 규칙
  - 변경: 캐릭터 삭제 → soft delete, 캐릭터 1명당 진행 중 세션 1개(409 `CHARACTER_IN_USE`), 초기 소지금 예시 500,000 → 300,000(02번 문서와 일치)
  - 추가(7장): 검사 순서, `client_action_id` 상황표, 재생 스트림, SSE 전송 형식, heartbeat, 실패 턴 처리, 연결 끊김 처리
  - 변경(7장): `state_patch`를 `StatePatch` 고정 모양으로 확정(인벤토리 변화 포함), `dice_roll`·`state_patch`를 턴 기록과 같은 모델로 통일
  - 추가(8장): SSE 타입 자동 생성(문서 전용 엔드포인트), 모델 이름표, `separate_input_output_schemas=False`, `gen:api` 스크립트
  - 변경(9장): CORS 허용 주소를 환경변수로, `allow_credentials=False`
  - 목차 번호 변경: 3장(게임 규칙표) 신설로 캐릭터 3→4장, 시나리오 4→5장, 세션 5→6장, 행동 6→7장, 타입 7→8장, CORS 8→9장
