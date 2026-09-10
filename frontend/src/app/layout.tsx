import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Project-Seoul",
  description: "현대판 대한민국(서울) 배경의 AI TRPG Game Master 서비스",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="ko" className="h-full antialiased">
      <body className="min-h-full flex flex-col font-sans">{children}</body>
    </html>
  );
}
