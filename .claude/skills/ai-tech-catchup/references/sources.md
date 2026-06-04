# 調査対象キーワード・情報源・MCP 活用ガイド

このファイルは、レポート生成時の「何を・どこから調べるか」を定義する。`SKILL.md` の調査ステップから参照する。
全部を網羅する必要はない。レポート種別とトピックに応じて、関連性の高いものを優先的に調べればよい。

## AI 技術キーワード

レポートで拾うべき技術領域。トピック別レポートでは、この一覧に加えて指定トピック固有の用語も調べる。

- AGI, Artificial General Intelligence
- Generative AI, Multimodal AI, VLM (Vision-Language Models), VLA (Vision-Language-Action)
- LLM, ChatGPT, Claude, Gemini, Qwen, Llama, Local LLM
- AI Agent, Multi-Agent Systems, RAG (Retrieval-Augmented Generation), MCP server
- Vibe Coding, AI Code Generation
- MLOps, LLMOps, RoboOps
- Computer Vision
- Audio AI, Voice AI
- AI Safety, Explainable AI, AI Regulation, AI Governance, AI Policy
- AI in Healthcare, Medical AI, Material AI
- AI in Climate, Green AI, Sustainability AI
- Physical AI, Robotics, Humanoid Robots, Digital Twins, Simulation
- AI Hardware, AI Chips, Edge AI, GPU, TPU, NPU
- Synthetic Data
- NVIDIA, CUDA, Isaac
- Google, GCP, Vertex AI, Gemini
- Microsoft, Azure, Copilot
- OpenAI, ChatGPT, GPT
- Anthropic, Claude, Claude Code
- Chinese AI ventures: Baidu, DeepSeek, Tencent, Unitree
- Japanese AI ventures: NEDO（新エネルギー・産業技術総合開発機構）
- Open Source, OSS, GitHub, AI Community
- Hugging Face, Transformers, Gradio, Open Source Models, LeRobot
- SNS: Twitter / X, LinkedIn, Reddit
- Gartner, Gartner Hype Cycle

## 主要情報源 URL

WebSearch / WebFetch で優先的に当たる情報源。十分な情報が得られない場合はその他の関連 URL も調べてよい。

### AI 企業公式サイト
- OpenAI: https://openai.com/ja-JP/news/ , https://openai.com/ja-JP/research/
- Anthropic: https://www.anthropic.com/news
- Google AI: https://ai.google/research , https://blog.google/technology/ai
- Microsoft: https://blogs.microsoft.com/ai , https://azure.microsoft.com/en-us/blog
- NVIDIA: https://blogs.nvidia.com , https://developer.nvidia.com/blog

### 技術ニュース
- TechCrunch AI: https://techcrunch.com/category/artificial-intelligence
- VentureBeat AI: https://venturebeat.com/ai
- The Verge AI: https://www.theverge.com/ai-artificial-intelligence
- Qiita: https://qiita.com/trend
- note (npaka): https://note.com/npaka
- GIGAZINE: https://gigazine.net/news/C4/

### 学術論文
- arXiv 最新論文: https://arxiv.org/list/cs.AI/recent
- Papers with Code: https://paperswithcode.com

### GitHub・OSS
- GitHub Trending: https://github.com/trending
- Hugging Face Blog: https://huggingface.co/blog
- Hugging Face Papers (trending): https://huggingface.co/papers/trending
- Hugging Face Models (trending): https://huggingface.co/models?sort=trending
- Hugging Face Spaces (trending): https://huggingface.co/spaces?sort=trending
- LeRobot: https://huggingface.co/lerobot

### ソーシャルメディア
- X / Twitter: https://x.com/Gradio , https://x.com/_akhaliq , https://x.com/ImAI_Eruel , https://x.com/npaka123
- Reddit: https://www.reddit.com/r/artificial , https://www.reddit.com/r/MachineLearning
- LinkedIn: https://www.linkedin.com

### 勉強会
- Connpass: https://connpass.com/explore/ , https://connpass.com/search/?q=AI

## MCP サーバー活用ガイド

このセッションで GitHub / Hugging Face の MCP サーバーが使える場合は、Web 検索だけでなく以下の調査も行うと精度が上がる。使えない場合はスキップしてよい（無理に呼び出さない）。

### GitHub MCP サーバー
- 注目の AI/ML リポジトリの最新コミット・Issue・PR を確認
- GitHub Trending から人気急上昇中の AI プロジェクトを取得
- スター数の多いリポジトリの最新リリースノートを確認
- OpenAI / Anthropic / Google AI / Microsoft AI などの公式 Organization の最新活動を確認

### Hugging Face MCP サーバー
- キーワード／トピックに関連する最新モデルを検索し、ダウンロード数・いいね数・更新日から人気度を把握
- 最新の公開データセット・ベンチマークを検索
- 注目の Space（デモアプリ・実験的プロジェクト）を検索
- 最新論文を検索し、概要・先行研究との差分・技術領域の動向を確認
