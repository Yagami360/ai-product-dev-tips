"use client";

import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport } from "ai";
import { useState } from "react";
import type { ChatMessage } from "@/ai/tools";
import { Weather } from "@/components/weather";
import { Comparison } from "@/components/comparison";

export default function Page() {
  const [input, setInput] = useState("");
  const { messages, sendMessage, status } = useChat<ChatMessage>({
    transport: new DefaultChatTransport({ api: "/api/chat" }),
  });

  return (
    <main style={{ maxWidth: 680, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h1 style={{ fontSize: 20 }}>Generative UI demo（Qwen + Vercel AI SDK）</h1>
      <p style={{ color: "#666", fontSize: 13 }}>
        例: 「東京の天気は？」→ 天気カード / 「料金プランを比較して」→ 比較表
      </p>

      {messages.map((message) => (
        <div key={message.id} style={{ margin: "12px 0" }}>
          <strong>{message.role === "user" ? "You" : "AI"}: </strong>
          {message.parts.map((part, i) => {
            switch (part.type) {
              // 通常のテキスト応答
              case "text":
                return <span key={i}>{part.text}</span>;

              // displayWeather ツール → 天気カード UI
              case "tool-displayWeather":
                if (part.state === "output-available") {
                  return <Weather key={i} {...part.output} />;
                }
                return <div key={i}>天気 UI を生成中...</div>;

              // compareProducts ツール → 比較表 UI
              case "tool-compareProducts":
                if (part.state === "output-available") {
                  return <Comparison key={i} {...part.output} />;
                }
                return <div key={i}>比較表 UI を生成中...</div>;

              default:
                return null;
            }
          })}
        </div>
      ))}

      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (input.trim()) {
            sendMessage({ text: input });
            setInput("");
          }
        }}
        style={{ display: "flex", gap: 8, marginTop: 24 }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={status !== "ready"}
          placeholder="例: 東京の天気は？ / 料金プランを比較して"
          style={{ flex: 1, padding: 8 }}
        />
        <button type="submit" disabled={status !== "ready"}>
          送信
        </button>
      </form>
    </main>
  );
}
