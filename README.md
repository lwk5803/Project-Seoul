# 여백 (Yeobaek)

현대 서울을 배경으로 한 **감정 서사 텍스트 RPG / 인터랙티브 에세이**입니다.
오늘의 나를 4가지로 정하면 AI가 그 하루를 단편 소설처럼 써 내려가고,
나는 순간마다 어떤 태도로 받아낼지를 고릅니다. 스스로 마침표를 찍으면 한 편의 이야기가 "여백의 서재"에 꽂힙니다.

(저장소 이름은 `Project-Seoul`입니다.)

## 기술 스택
- Frontend: Next.js 16 (App Router), TypeScript, Tailwind CSS + Shadcn UI
- Backend: Python 3.10+, FastAPI, LangChain & LangGraph, Pydantic v2
- DB & Auth: Supabase (PostgreSQL), Supabase Auth, pgvector
- Infra/DevOps: Vercel, Render/Railway, Git/GitHub, LangSmith

## 설계 문서
본격적인 개발에 앞서 정한 설계 약속은 [`docs/`](docs/README.md) 폴더에 있습니다.
- [게임 기획서](docs/GAME_CONCEPT.md) ← 모든 설계의 출발점
- [아키텍처 개요](docs/01-아키텍처-개요.md)
- [게임 도메인 규칙](docs/02-게임-도메인-규칙.md)
- [데이터베이스 스키마](docs/03-데이터베이스-스키마.md)
- [API 계약서](docs/04-API-계약서.md) ← 프론트/백엔드 공통 약속
- [AI 에이전트 설계](docs/05-에이전트-설계.md)
- [개발 로드맵](docs/06-개발-로드맵.md)
- [세션별 작업 지시서](docs/07-세션별-작업지시서.md)
- [결정사항 목록](docs/08-확정필요-결정사항.md)
- [UI 디자인 가이드](docs/09-UI-디자인-가이드.md)

## 개발 로그
작업 단계별 기록은 [`docs/devlog/`](docs/devlog/README.md)에 쌓이고,
이를 다듬은 글은 [티스토리 블로그](https://wongang.tistory.com/)에 정리합니다.
