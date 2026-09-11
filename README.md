# Project-Seoul

현대판 대한민국(서울) 배경의 AI TRPG Game Master 멀티 에이전트 텍스트 RPG 서비스입니다.

## 기술 스택
- Frontend: Next.js (App Router), TypeScript, Tailwind CSS + Shadcn UI, Vercel AI SDK
- Backend: Python 3.10+, FastAPI, LangChain & LangGraph, Pydantic v2
- DB & Auth: Supabase (PostgreSQL), Supabase Auth, pgvector
- Infra/DevOps: Vercel, Render/Railway, Git/GitHub, LangSmith

## 설계 문서
본격적인 개발에 앞서 정한 설계 약속은 [`docs/`](docs/README.md) 폴더에 있습니다.
- [아키텍처 개요](docs/01-아키텍처-개요.md)
- [게임 도메인 규칙](docs/02-게임-도메인-규칙.md)
- [데이터베이스 스키마](docs/03-데이터베이스-스키마.md)
- [API 계약서](docs/04-API-계약서.md) ← 프론트/백엔드 공통 약속
- [AI 에이전트 설계](docs/05-에이전트-설계.md)
- [개발 로드맵](docs/06-개발-로드맵.md)

## 개발 로그
작업 단계별 진행 내용은 [티스토리 블로그](https://wongang.tistory.com/)에 정리합니다.
