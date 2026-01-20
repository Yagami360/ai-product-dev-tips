# Cursor で Agent Skills を使用して簡単なスキルを作成＆利用する

> **注意**: エージェントスキルは、Cursor の **Nightly リリースチャネル**でのみ利用できます。チャネルを切り替えるには、Cursor の設定（`Cmd+Shift+J`）を開き、**Beta** を選択し、更新チャネルを **Nightly** に設定します。

Cursor でも Claude Code CLI と同様に Agent Skills を使用できます。Agent Skills は、AIエージェントに専門的な機能を追加するためのオープンな標準で、ドメイン固有の知識やワークフローをパッケージ化したものです。

| 項目 | Cursor の Agent Skills | Claude Code CLI の Agent Skills |
|------|----------------------|-------------------------------|
| **配置場所** | `.cursor/skills/` または `.claude/skills/` | `.claude/skills/` |
| **ファイル名** | `SKILL.md` (固定) | `SKILL.md` (固定) |
| **メタデータ** | YAML フロントマター必須 | YAML フロントマター必須 |
| **適用方法** | Agent が自動判断 または `/` で手動呼び出し | `description` に一致すると自動適用 |
| **スコープ** | プロジェクト・ユーザーレベル | プロジェクト・個人スキル |
| **標準** | Agent Skills オープンスタンダード | Agent Skills オープンスタンダード |

## 方法

1. スキルディレクトリを作成する

    プロジェクトレベル（特定プロジェクトのみ）の場合：

    ```bash
    mkdir -p .cursor/skills/code-explanation-with-diagrams
    ```

    ユーザーレベル（グローバル）の場合：

    ```bash
    mkdir -p ~/.cursor/skills/code-explanation-with-diagrams
    ```

    > **互換性**: `.claude/skills/` も使用可能（Claude Code CLI との互換性のため）

1. `SKILL.md` を作成する

    各スキルは、YAML フロントマター付きの `SKILL.md` ファイルで定義されます。

    [.cursor/skills/code-explanation-with-diagrams/SKILL.md](.cursor/skills/code-explanation-with-diagrams/SKILL.md)

    ```markdown
    ---
    name: code-explanation-with-diagrams
    description: 図を使ってコードを説明します。コードの動作を説明する時、コードベースについて教える時、または「これはどう動くの？」と聞かれた時に使用します。
    ---

    # コード説明（図付き）

    コードを説明する際は、必ず以下を含めてください：

    ## 使用するタイミング

    - コードの動作を説明する時
    - コードベースについて教える時
    - 「これはどう動くの？」と聞かれた時

    ## 指示

    1. **図を描く**: ASCII アートを使って、フロー、構造、または関係性を視覚的に示す
    2. **コードをウォークスルーする**: 何が起こるかをステップバイステップで説明する
    3. **注意点を強調する**: よくある間違いや誤解は何か？

    説明は会話調に保ってください。複雑な処理には、複数の図を使って段階的に説明してください。
    ```

    ポイントは、以下の通り

    - **YAML フロントマター必須**
        - `description`: メニューに表示される短い説明。エージェントがそのスキルをいつ適用すべきか判断するために使われる（必須）
        - `name`: 人間が読めるわかりやすい名前（省略可。省略した場合は親フォルダー名が使用される）
    - マークダウン形式で詳細な指示を記述する
    - スキルは Cursor 起動時に自動的に検出される

1. スキルを確認する

    Cursor Settings を開く（Mac は `Cmd+Shift+J`、Windows/Linux は `Ctrl+Shift+J`）

    **Rules** に移動すると、スキルは **Agent Decides** セクションに表示されます。

1. スキルを使用する

    - **自動適用**: Agent がコンテキストに応じてどのスキルを使うかを判断します

        ```
        この認証関数はどう動くの？
        ```

    - **手動呼び出し**: Agent チャットで `/` を入力し、スキル名を検索して手動で呼び出すこともできます

        ```
        /code-explanation-with-diagrams
        ```

## GitHub からスキルをインストールする

GitHub リポジトリからスキルをインポートできます。

1. **Cursor Settings → Rules** を開く
2. **Project Rules** セクションで **Add Rule** をクリック
3. **Remote Rule (Github)** を選択
4. GitHub リポジトリの URL を入力

## 参考サイト

- https://cursor.com/ja/docs/context/skills
- https://agentskills.io （Agent Skills オープンスタンダード）
- [Claude Code CLI の Agent Skills を使用して簡単なスキルを作成１利用する](../55/README.md)
