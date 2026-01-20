# Claude Code CLI の Agent Skills を使用して簡単なスキルを作成＆利用する

Agent Skills は、Claude Code CLI で特定のタスクを実行する方法を教えるマークダウンファイルです。`SKILL.md` に記述した内容は、**条件に一致した場合にシステムプロンプトとして Claude に渡されます**。これにより、チーム標準を使用した PR レビュー、好みの形式でのコミット メッセージ生成、またはコードの説明など、Claude に特定の方法で動作するように指示できます。

| 項目 | Agent Skills | 直接プロンプト指示 | MCP サーバー |
|------|-------------|-----------------|-------------|
| **実装方法** | マークダウンファイル（`SKILL.md`） | 毎回手動で入力 | Python/Node.js でサーバー実装 |
| **目的** | Claude の動作方法を指示 | その場限りの指示 | 外部ツール・データソース連携 |
| **再利用性** | 自動的に適用される | 毎回入力が必要 | 常時起動で利用可能 |
| **共有** | Git 管理可能 | 口頭・ドキュメント共有 | 複数クライアントで利用可能 |
| **適用タイミング** | 条件一致で自動 | 手動で毎回 | リクエストに応じて |
| **用途例** | コーディング規約、レビュー基準 | 一時的な指示 | API 呼び出し、DB アクセス |

## 方法

1. スキルディレクトリを作成する

    個人スキル（全プロジェクトで利用可能）の場合：

    ```bash
    mkdir -p ~/.claude/skills/code-explanation-with-diagrams
    ```

    プロジェクトスキル（特定プロジェクトのみ）の場合：

    ```bash
    mkdir -p .claude/skills/code-explanation-with-diagrams
    ```

1. スキルのプロンプトを定義した `SKILL.md` を作成する

    すべてのスキルには `SKILL.md` ファイルが必要です。ファイルは `---` マーカー間の YAML メタデータで始まり、`name` と `description` を含む必要があり、その後に Claude がスキルがアクティブな場合に従うマークダウン命令が続きます。

    > **注意**: `SKILL.md` は英語でも日本語でも記述可能です。Claude は多言語に対応しています。

    [.claude/skills/code-explanation-with-diagrams/SKILL.md](.claude/skills/code-explanation-with-diagrams/SKILL.md)

    ```markdown
    ---
    name: code-explanation-with-diagrams
    description: 図を使ってコードを説明します。コードの動作を説明する時、コードベースについて教える時、または「これはどう動くの？」と聞かれた時に使用します。
    ---

    コードを説明する際は、必ず以下を含めてください：

    1. **図を描く**: ASCII アートを使って、フロー、構造、または関係性を視覚的に示す
    2. **コードをウォークスルーする**: 何が起こるかをステップバイステップで説明する
    3. **注意点を強調する**: よくある間違いや誤解は何か？

    説明は会話調に保ってください。複雑な処理には、複数の図を使って段階的に説明してください。
    ```

    ポイントは、以下の通り

    - **`SKILL.md` の内容はモデルへのプロンプト指示になる**
        - `description` に一致する質問やタスクが来た場合、`SKILL.md` の内容がシステムプロンプトとして Claude に渡される
        - マークダウン部分に記述した指示に従って Claude が動作する
    - `description` は特に重要。Claude はそれを使用してスキルを適用するかどうかを決定する
    - スキルは作成または変更時に自動的に読み込まれる

1. スキルを確認する

    ```bash
    claude
    ```

    Claude Code CLI を起動後、以下のコマンドでスキルを確認：

    ```
    What Skills are available?
    ```

1. スキルをテストする

    プロジェクト内のファイルを開き、スキルの説明に一致する質問を Claude に尋ねます。

    ```
    この認証関数はどう動くの？
    ```

    Claude は `code-explanation-with-diagrams` スキルを適用し、図を使用してコードを説明します。

## 参考サイト

- https://code.claude.com/docs/ja/skills
- [MCP サーバーを自作して MCP クライアント（Claude Code CLI や Cursor など）で利用する](../36/README.md)
- https://tech.findy.co.jp/entry/2025/10/27/070000
