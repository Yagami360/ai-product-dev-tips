# MCP サーバーの概要

LLM の分野における MCP [Motion Control Protocol] とは、Claude、ChatGPTなどの AIアシスタント（MCP クライアント）が外部のツールやデータソースと効果的に連携するための Anthropic が提唱したオープンなプロトコル。

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Claude        │◄──►│   MCP Server    │◄──►│  External APIs  │
│  (MCPクライアント)│    │ (Protocol)      │    │   (Tools)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

> Anthropic が提唱したオープンなプロトコルであるが、MCPサーバーは Claude モデルだけでなく、他のAIモデルでも利用可能

> MCP [Motion Control Protocol] サーバーという用語自体は、1980 年頃に工場自動化の技術分野で出てきた用語

- MCP クライアント / MCP ホスト
    - Claude, Cursor などの MCP サーバーを利用して回答を行うクライアント

- MCP サーバー

    - 自身のローカル環境や特定ので動き、「ローカル上でのデータ取得」「SQLiteにアクセスする」「YouTubeを検索する」「天気APIを叩く」などの特定のタスク（tools）を実行するプログラム

        > LLM に特定のタスク（tools）を実行させる仕組みに、Function calling がある。Function calling では、開発者が直接AIモデルに関数定義を渡すが、MCP では、共通のプロトコルに基づき MCP サーバーが tools の定義を動的に提供し管理する違いがあるが、Function calling と MCP サーバーにける各 tools は本質的には同じようなもの

    - また、MCPはオープンプロトコルなので、Claude専用、ChatGPT専用といった縛りがない。

    - MCP サーバーの例

        - GitHub MCP サーバー

        - Slack MCP サーバー

