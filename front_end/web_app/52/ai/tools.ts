import { tool } from "ai";
import type { InferUITools, UIDataTypes, UIMessage } from "ai";
import { z } from "zod";

// 天気カード UI を出すためのツール。
// LLM はユーザーの要求に応じてこのツールを呼び、返り値（props）が <Weather> に流し込まれる。
export const displayWeather = tool({
  description:
    "指定した地域の天気を「天気カード UI」で表示する。ユーザーが天気を尋ねたときに使う。",
  inputSchema: z.object({
    location: z.string().describe("天気を知りたい地域名（例: 東京）"),
  }),
  // 本来は天気 API を呼ぶ。ここではローカル PoC 用の固定ダミーデータを返す。
  execute: async ({ location }) => {
    return {
      location,
      temperature: 22,
      condition: "晴れ",
      weeklyForecast: [
        { day: "月", temperature: 22 },
        { day: "火", temperature: 24 },
        { day: "水", temperature: 19 },
        { day: "木", temperature: 21 },
        { day: "金", temperature: 25 },
      ],
    };
  },
});

// 比較表 UI を出すためのツール。天気カードとは別形状の UI を出し分けられることを示す。
export const compareProducts = tool({
  description:
    "複数のプランや製品を「比較表 UI」で表示する。ユーザーがプラン比較・違い・おすすめを尋ねたときに使う。",
  inputSchema: z.object({
    category: z.string().describe("比較する対象のカテゴリ（例: 料金プラン）"),
  }),
  execute: async ({ category }) => {
    return {
      category,
      items: [
        { name: "Free", price: "¥0", storage: "1 GB", support: "コミュニティ" },
        { name: "Pro", price: "¥1,200", storage: "100 GB", support: "メール" },
        {
          name: "Enterprise",
          price: "要問合せ",
          storage: "無制限",
          support: "24/365 専任",
        },
      ],
    };
  },
});

export const tools = { displayWeather, compareProducts };

// useChat / route 双方で共有する型。これにより message.parts の tool パーツの
// part.output がツールの返り値で型付けされる。
export type ChatTools = InferUITools<typeof tools>;
export type ChatMessage = UIMessage<never, UIDataTypes, ChatTools>;
