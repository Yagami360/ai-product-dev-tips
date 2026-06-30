import {
  convertToModelMessages,
  createUIMessageStreamResponse,
  streamText,
  toUIMessageStream,
} from "ai";
import { createOpenAICompatible } from "@ai-sdk/openai-compatible";
import { tools, type ChatMessage } from "@/ai/tools";

// ローカルの Ollama を OpenAI 互換エンドポイント（/v1）として叩くプロバイダ。
// Ollama は http://localhost:11434/v1 で OpenAI 互換 API を提供し、tool calling にも対応する。
const ollama = createOpenAICompatible({
  name: "ollama",
  baseURL: "http://localhost:11434/v1",
});

// 使用する Qwen モデル。OLLAMA_MODEL で上書き可（例: qwen3.5:9b）。
const MODEL = process.env.OLLAMA_MODEL ?? "qwen3.5:4b";

// ストリーミング応答の最大実行時間（秒）
export const maxDuration = 30;

export async function POST(req: Request) {
  const { messages }: { messages: ChatMessage[] } = await req.json();

  const result = streamText({
    // provider 非依存。ここを @ai-sdk/openai / @ai-sdk/anthropic 等に差し替えれば
    // 同じツール定義のままクラウド LLM へ切り替えられる。
    model: ollama(MODEL),
    system:
      "あなたは UI を生成するアシスタントです。ユーザーの要求に最も合うツールを 1 つ呼び出してください。" +
      "天気の質問には displayWeather、プラン/製品の比較には compareProducts を使います。" +
      "ツールの返り値は対応する UI コンポーネントとして自動表示されるため、数値や表をテキストで再記述する必要はありません。",
    messages: await convertToModelMessages(messages),
    tools,
  });

  return createUIMessageStreamResponse({
    stream: toUIMessageStream({ stream: result.stream }),
  });
}
