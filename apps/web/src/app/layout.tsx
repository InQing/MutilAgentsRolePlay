import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "MutilAgentsRolePlay",
  description: "Multi-AI roleplay and social simulation world"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>
        <div className="shell">
          <header className="mb-10 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="eyebrow">V1 Prototype</p>
              <h1 className="text-4xl font-semibold tracking-tight text-ink">
                MutilAgentsRolePlay
              </h1>
              <p className="muted mt-3 max-w-2xl text-sm leading-6">
                单用户单世界的多 AI 社交模拟项目。当前仓库已完成前后端基础骨架，
                下一步将逐步接入世界内核、角色运行时与导演面板。
              </p>
            </div>
            <nav className="glass flex items-center gap-3 px-4 py-3 text-sm font-medium">
              <Link href="/">世界概览</Link>
              <Link href="/director">导演面板</Link>
            </nav>
          </header>
          {children}
        </div>
      </body>
    </html>
  );
}

