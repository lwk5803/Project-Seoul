# Project-Seoul 프론트엔드

[Next.js](https://nextjs.org)(App Router) + TypeScript + Tailwind CSS 기반으로 만든 프론트엔드 프로젝트입니다. `create-next-app`으로 초기 골격을 생성했습니다.

## 시작하기

개발 서버 실행:

```bash
npm run dev
```

브라우저에서 [http://localhost:3000](http://localhost:3000) 접속하면 결과를 확인할 수 있습니다.

`src/app/page.tsx` 파일을 수정하면 저장할 때마다 화면이 자동으로 갱신됩니다.

## 빌드 확인

```bash
npm run build
```

정상적으로 빌드가 되는지 확인할 때 사용합니다.

## 폴더 구조 (초기 상태)

- `src/app/` — 라우트(페이지) 및 레이아웃
- `public/` — 정적 파일(이미지, 아이콘 등)

## 참고

- 폰트는 외부(구글 폰트) 요청 없이 시스템 폰트를 사용하도록 설정되어 있습니다 (네트워크 제한 환경에서도 빌드가 안정적으로 되도록 하기 위함).
