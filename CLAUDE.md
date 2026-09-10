# AI TRPG Game Master Project - Master Instructions

## 1. 프로젝트 개요 및 아키텍처
- **프로젝트 명:** AI TRPG Game Master (현대판 대한민국 배경)
- **목적:** LangGraph, FastAPI, Next.js, Supabase를 활용한 멀티 에이전트 텍스트 RPG 웹/앱 서비스 구축
- **핵심 기술 스택:**
  - Frontend: Next.js (App Router), TypeScript, Tailwind CSS + Shadcn UI, Vercel AI SDK
  - Backend: Python 3.10+, FastAPI, LangChain & LangGraph, Pydantic v2
  - DB & Auth: Supabase (PostgreSQL), Supabase Auth, pgvector
  - Infra/DevOps: Vercel, Render/Railway, Git/GitHub, LangSmith

## 2. 소통 및 설명 원칙 (비전공자 눈높이)
- 나는 비전공자 개발자이다. 복잡한 기술 용어나 코드를 다룰 때는 **일상적인 비유를 들어 아주 쉽게 설명**해 달라.
- 코드를 수정하거나 작성할 때는 **"왜 이 코드가 필요한지", "어떤 원리로 동작하는지"** 핵심 의미를 친절하게 설명해 달라.
- 답변은 불필요한 인사말이나 반복을 줄이고, **변경되는 핵심 코드 스니펫(Snippet) 위주로 간결하게 구성**하여 토큰을 효율적으로 사용해 달라.

## 3. 단계별 작업 및 개발 로그 규칙
- 작업을 한 번에 거대하게 처리하지 말고, **아주 작은 단계(Step-by-Step)**로 나누어 진행해 달라.
- 각 단계가 끝날 때는 티스토리 블로그(`https://wongang.tistory.com/`)나 학습용으로 바로 옮겨 적을 수 있도록 아래 포맷에 맞춰 **개발 로그(Dev Log)**를 출력해 달라.
  1. **현재 단계 목표:**
  2. **사용한 기술/핵심 개념 (비유 설명 포함):**
  3. **작성/수정된 핵심 코드:**
  4. **동작 확인 방법:**
  5. **오늘의 학습 포인트:**

## 4. Git 및 블로그 초안 관리 규칙
- 작업 내용이 바뀔 때마다 깃허브 커밋 메시지 규칙(Conventional Commits, 예: `feat:`, `fix:`)에 맞춰 깔끔한 커밋 메시지를 제안해 달라.
- 작업 마무리에 요청할 경우, 내 티스토리 블로그에 바로 활용할 수 있는 **마크다운 형식의 블로그 포스팅 초안**을 작성해 달라.