# CLAUDE.md により Claude Code でのコード生成品質を向上させる

## 方法

1. Claude Code をインストールする

1. Claude Code を起動する

    ```bash
    claude
    ```
    ```bash
    (base) yusukesakai@YusukenoMacBook-Pro ai-product-dev-tips % claude
    ╭─────────────────────────────────────────────────────────╮
    │ ✻ Welcome to Claude Code!                               │
    │                                                         │
    │   /help for help, /status for your current setup        │
    │                                                         │
    │   cwd: /Users/yusukesakai/personal/ai-product-dev-tips  │
    ╰─────────────────────────────────────────────────────────╯

    Tips for getting started:

    1. Run /init to create a CLAUDE.md file with instructions for Claude
    2. Use Claude to help with file analysis, editing, bash commands and git
    3. Be as specific as you would with another engineer for the best results
    4. ✔ Run /terminal-setup to set up terminal integration
    ```

1. `/init` を実行する

    実行するとプロジェクトを解析する

    ```bash
    > /init is analyzing your codebase… 

    ⏺ I'll analyze your codebase and create a CLAUDE.md file. Let me start by exploring the repository
    structure and understanding the codebase.

    ⏺ Update Todos
    ⎿  ☐ Analyze repository structure and contents                     
        ☐ Check if CLAUDE.md already exists
        ☐ Create comprehensive CLAUDE.md file
        ☐ Examine package.json, requirements.txt, and other config files
        ☐ Read README.md for important information
        ☐ Check for .cursor/rules or .cursorrules files

    ⏺ List(.)
    ⎿  Listed 1408 paths (ctrl+r to expand)

    ⏺ Search(pattern: "CLAUDE.md")
    ⎿  Found 0 files 

    ⏺ Search(pattern: ".cursor/rules/**")
    ⎿  Found 0 files 

    ⏺ Search(pattern: ".cursorrules")
    ⎿  Found 0 files 

    ⏺ Search(pattern: ".github/copilot-instructions.md")
    ⎿  Found 0 files 

    ⏺ Update Todos
    ⎿  ☒ Analyze repository structure and contents                     
        ☒ Check if CLAUDE.md already exists
        ☒ Check for .cursor/rules or .cursorrules files
        ☐ Examine package.json, requirements.txt, and other config files
        ☐ Create comprehensive CLAUDE.md file
        ☐ Read README.md for important information

    ⏺ Read(README.md)
    ⎿  Error: File content (28720 tokens) exceeds maximum allowed tokens (25000). Please use offset and 
        limit parameters to read specific portions of the file, or use the GrepTool to search for specific
        content.

    ⏺ Search(pattern: "package.json")
    ⎿  Found 0 files 

    ⏺ Search(pattern: "requirements.txt")
    ⎿  Found 0 files 

    ⏺ Search(pattern: "Dockerfile")
    ⎿  Found 0 files 

    ⏺ Search(pattern: "**/Makefile")
    ⎿  Found 20 files (ctrl+r to expand)

    ⏺ Read(README.md)
    ⎿  Read 100 lines (ctrl+r to expand)

    ⏺ Read(ml_ops/108/Makefile)
    ⎿  Read 15 lines (ctrl+r to expand)

    ⏺ Read(ml_ops/113/Makefile)
    ⎿  Read 11 lines (ctrl+r to expand)

    ⏺ Task(Sample project configurations)
    ⎿  Found 100 files (ctrl+r to expand)
        Read(ml_ops/107/demo-app/requirements.txt)
        +6 more tool uses

    ✶ Navigating… (62s · ⚒ 778 tokens · esc to interrupt)
    ```

    実行完了すると、[`CLAUDE.md`](../../CLAUDE.md) が自動作成される

    CLAUDE.mdファイルは、Claude API のメモリ機能として動作し、AIモデルが理解しやすい形式で情報を構造化したものになっており、`CLAUDE.md` を作成することで一貫性のある高品質な出力を実現する

1. 指定のディレクトリ以下に `CLAUDE.md` を配置する

    - ./CLAUDE.md（プロジェクトルート）に配置した場合：対象
    - ~/.claude/CLAUDE.md（ホームディレクトリ） に配置：ユーザー固有の設定（複数のプロジェクトに影響）
