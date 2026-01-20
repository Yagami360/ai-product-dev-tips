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

    ```bash
    ⏺ Available Skills

    Currently, there is 1 skill available in this project:

    📊 code-explanation-with-diagrams

    Description: 図を使ってコードを説明します。コードの動作を説明する時、コードベースについて教える時、
    または「これはどう動くの?」と聞かれた時に使用します。

    What it does:
    When explaining code, this skill ensures Claude will:
    1. Draw diagrams using ASCII art to show flows, structures, or relationships
    2. Walk through the code step-by-step
    3. Highlight common mistakes or misconceptions

    Located at: .claude/skills/code-explanation-with-diagrams/SKILL.md:1

    ---
    This is a project-level skill (stored in .claude/skills/), which means it's only active when
    working within this specific project directory. The skill automatically activates when you ask
    questions like "How does this work?" or request code explanations.
    ```

1. スキルをテストする

    プロジェクト内のファイルを開き、スキルの説明に一致する質問を Claude に尋ねます。

    ```
    How does this code work?
    ```

    Claude は `code-explanation-with-diagrams` スキルを適用し、図を使用してコードを説明します。

    ```bash
    ⏺ Looking at this project, it's a demonstration of Claude Code CLI's Agent Skills feature. Let me
    explain how it works:

    Architecture Overview

    ┌─────────────────────────────────────────────────────────────┐
    │                    Claude Code CLI                          │
    │                                                             │
    │  1. User asks question                                      │
    │     "How does this work?"                                   │
    │                    ↓                                        │
    │  2. CLI checks skill descriptions                           │
    │     Matches: "コードの動作を説明する時"                        │
    │                    ↓                                        │
    │  3. Loads SKILL.md as system prompt                         │
    │     .claude/skills/code-explanation-with-diagrams/SKILL.md  │
    │                    ↓                                        │
    │  4. Claude responds with skill instructions                 │
    │     - Draw ASCII diagrams                                   │
    │     - Walk through code step-by-step                        │
    │     - Highlight common mistakes                             │
    └─────────────────────────────────────────────────────────────┘

    How It Works Step-by-Step

    1. Skill Definition (.claude/skills/code-explanation-with-diagrams/SKILL.md:1)

    SKILL.md structure:
    ├── YAML Frontmatter (lines 1-4)
    │   ├── name: "code-explanation-with-diagrams"
    │   └── description: "図を使ってコードを説明..."  ← Trigger condition
    │
    └── Markdown Instructions (lines 6-12)
        └── Prompt that gets injected into Claude's system prompt

    2. Automatic Activation

    When you ask a question that matches the description field:
    - ✅ "この認証関数はどう動くの?" → Activates skill
    - ✅ "How does this work?" → Activates skill
    - ❌ "What's the weather?" → Doesn't activate skill

    3. Skill Injection Flow

    User Input → Claude Code CLI → Skill Matcher
                                        ↓
                                    Check description
                                        ↓
                            Match found? YES/NO
                                        ↓ YES
                            Load SKILL.md content
                                        ↓
                        Inject as system prompt
                                        ↓
                            Claude responds with:
                            - ASCII diagrams
                            - Step-by-step walkthrough
                            - Common pitfalls

    Key Components

    YAML Metadata (.claude/skills/code-explanation-with-diagrams/SKILL.md:1-4)

    - name: Identifier for the skill
    - description: Critical - Claude uses this to decide when to activate the skill

    Markdown Instructions (.claude/skills/code-explanation-with-diagrams/SKILL.md:6-12)

    - Becomes part of Claude's system prompt when skill is active
    - Defines specific behavior: must include diagrams, walkthroughs, and warnings

    Skill Types

    Personal Skills                Project Skills
    ~/.claude/skills/             .claude/skills/
    ├── Available everywhere      ├── Only in this project
    └── User-specific            └── Team-shareable (Git)

    Common Pitfalls & Best Practices

    ⚠️ Common Mistakes:
    1. Vague descriptions - Claude won't know when to activate the skill
    2. Missing SKILL.md - Skills require this exact filename
    3. No YAML frontmatter - Both name and description are required

    ✅ Best Practices:
    1. Specific descriptions - Clearly define when the skill should activate
    2. Clear instructions - The markdown content should be actionable
    3. Use either language - Japanese or English works fine
    4. Test activation - Ask questions that match your description

    Comparison with Alternatives

    | Feature    | Agent Skills          | Manual Prompts | MCP Servers         |
    |------------|-----------------------|----------------|---------------------|
    | Automation | Auto-applies          | Every time     | On request          |
    | Scope      | Behavior instructions | One-off        | External tools      |
    | Sharing    | Git-friendly          | Documentation  | Separate deployment |

    This skill system essentially lets you teach Claude custom behaviors that automatically activate
    based on context, without having to repeat yourself every time!
    ```

## 参考サイト

- https://code.claude.com/docs/ja/skills
- [MCP サーバーを自作して MCP クライアント（Claude Code CLI や Cursor など）で利用する](../36/README.md)
- https://tech.findy.co.jp/entry/2025/10/27/070000
