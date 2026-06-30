import type { ReactNode } from "react";

export const metadata = {
  title: "Generative UI demo (Qwen + Vercel AI SDK)",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
