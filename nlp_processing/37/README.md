# GitHub MCP サーバーを使用して PR 作成や PR レビューなどの様々な GitHub 操作を行う

## 事前準備

1. GitHub トークンの取得

    1. GitHub の Settings > Developer settings > Personal access tokens > Tokens (classic) にアクセス
    2. "Generate new token (classic)" をクリック
    3. 必要な権限を選択（repo, user, workflow など）
    4. トークンを生成してコピー

## Claude Code CLI で使用する場合

1. GitHub MCP サーバーを登録する

    - CLI で登録する場合

        ```bash
        # MCPサーバーを登録
        claude mcp add --transport http github https://api.githubcopilot.com/mcp -H "Authorization: Bearer YOUR_GITHUB_PAT"

        # MCPサーバーを登録（プロジェクトスコープ）
        # claude mcp add --scope project --transport http github https://api.githubcopilot.com/mcp -H "Authorization: Bearer YOUR_GITHUB_PAT"
        ```

    - 設定ファイルで登録する場合

        プロジェクトスコープで使用する場合：Claude CLI が認識しているプロジェクトルートに `.mcp.json` ファイルを作成

        ```json
        {
            "servers": {
            "github": {
                "type": "http",
                "url": "https://api.githubcopilot.com/mcp/",
                "headers": {
                "Authorization": "Bearer ${input:github_mcp_pat}"
                }
            }
            },
            "inputs": [
            {
                "type": "promptString",
                "id": "github_mcp_pat",
                "description": "GitHub Personal Access Token",
                "password": true
            }
            ]
        }
        ```

        > 直接設定ファイルを作成する場合は、`claude` コマンドで Clade Code CLI を起動したあとに認識される

1. 登録されたMCPサーバーを確認する

    ```bash
    # 登録済みMCPサーバーの一覧を表示
    claude mcp list

    # 特定のサーバーの詳細を確認
    claude mcp get github
    ```

1. Claude Code CLI に接続する

    ```bash
    claude
    ```

1. （オプション）Claude Code CLI で登録されたMCPサーバーを確認する

    ```bash
    /mcp github
    ```

    ```bash
    > /mcp github 
    ╭────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
    │ Github MCP Server                                                                                                                      │
    │                                                                                                                                        │
    │ Status: ✔ connected                                                                                                                    │
    │ URL: https://api.githubcopilot.com/mcp                                                                                                 │
    │ Config location: /Users/yusukesakai/.claude.json [project: /Users/yusukesakai/personal/ai-product-dev-tips/nlp_processing/37]          │
    │ Capabilities: tools · prompts                                                                                                          │
    │ Tools: 104 tools                                                                                                                       │
    │                                                                                                                                        │
    │ ❯ 1. View tools                                                                                                                        │
    │   2. Authenticate                                                                                                                      │
    │   3. Reconnect                                                                                                                         │
    │   4. Disable 
    ```
    ```bash
    │ Tools for github (104 tools)                                                                                                           │
    │                                                                                                                                        │
    │ ❯ 1.   Add review comment to the requester's latest pending pull request review                                                        │
    │   2.   Add comment to issue                                                                                                            │
    │   3.   Add project item                                                                                                                │
    │   4.   Add sub-issue                                                                                                                   │
    │ ↓ 5.   Assign Copilot to issue   
    ```

1. Claude Code CLI で GitHub MCP サーバーの各種ツールを使用する

    - PR作成

        ```bash
        mcp__github__create_pull_request
        ```

    - PR レビュー => 投稿

        ```bash
        ```

    - PR 取得 => ローカルでレビュー

        ** PR 取得 **

        ```bash
        mcp__github__get_pull_request
        ```

        ```bash
        ⏺ I'll help you get information about a pull request. However, I need some details to proceed:

        1. Repository owner (e.g., username or organization)
        2. Repository name
        3. Pull request number

        Could you provide these details? For example:
        - owner/repo #123
        - Or just the pull request number if you want to check a specific repo

        Alternatively, if you have a GitHub URL for the pull request, you can share that and I'll extract the necessary information.
        ```

        ```bash
        > Yagami360/ai-tech-catchup-agent #44 
        ```

        ```bash
        PR #44: Add slack notification

        Status: Open (Draft)Title: [WIP] Add slack notificationDescription: Slack 通知機能の追加

        Changes:
        - 1 commit
        - 8 files changed
        - +352 additions, -8 deletions

        Branch: feature/slack-notification-20250930 → master

        Merge Status: ❌ Not mergeable (conflicts with base)
        - mergeable: false
        - mergeable_state: "dirty"

        Created: 2025-09-30Last updated: 2025-09-30

        PR URL: https://github.com/Yagami360/ai-tech-catchup-agent/pull/44
        ```

        ** PR レビュー **

        ```bash
        > このPRをレビューして
        ```
        
        ```bash
        ⏺ PR #44 レビュー結果

        📊 概要

        Slack通知機能を追加する良い実装です。全体的にコードは整理されていますが、いくつか改善点があります。

        ---
        ✅ 良い点

        1. オプショナル設計: --slackフラグでオン/オフ可能
        2. 適切なエラーハンドリング: 例外処理が各所に実装されている
        3. ドキュメント充実: README.mdにセットアップ手順を詳細に記載
        4. レポートタイプ別のカスタマイズ: アイコンと色を使い分け

        ---
        ⚠️ 重要な問題

        1. Makefileのデフォルト動作変更 (重大)

        # Makefile - src/client/slack_client.py:89-96
        -     uv run python -m src.main
        +     uv run python -m src.main --slack

        問題: デフォルトでSlack通知が有効になっています。Webhook URLが未設定の場合、毎回警告が出る可能性があります。

        推奨修正:
        # デフォルトはSlack通知なし
        run: install
                uv run python -m src.main

        # Slack通知版は別コマンドに
        run-with-slack: install
                uv run python -m src.main --slack

        2. GitHub Issue URLの重複フィールド (src/client/slack_client.py:89-96)

        if issue_url:
            payload["attachments"][0]["fields"].append({
                "title": "GitHub Issue",
                "value": f"<{issue_url}|Issueを確認>",
                "short": True,
            })

        問題: title_linkで既にURLがリンクされているのに、さらにフィールドとして追加しています。

        推奨修正: このフィールドを削除するか、別の情報（例：Issue番号）を表示

        ---
        🔧 改善提案

        3. Markdown変換の問題 (src/client/slack_client.py:163-183)

        content = content.replace("**", "*")
        content = content.replace("##", "*")
        content = content.replace("###", "*")

        問題:
        - ##を*に置換すると、見出しが強調テキストになってしまう
        - 順序を考慮していないため、###が正しく変換されない可能性

        推奨修正:
        # 見出しの変換（長い方から処理）
        content = content.replace("### ", "*")
        content = content.replace("## ", "*")
        content = content.replace("# ", "*")
        # 太字の変換
        content = content.replace("**", "*")

        4. 型ヒントの互換性 (src/client/slack_client.py:129)

        def _get_report_style(self, report_type: str) -> tuple[str, str]:

        問題: tuple[str, str]はPython 3.9+の構文。古いバージョンでは動作しません。

        推奨修正:
        from typing import Tuple

        def _get_report_style(self, report_type: str) -> Tuple[str, str]:

        5. エラーレスポンスの改善 (src/client/slack_client.py:114-119)

        logger.error(f"Slack通知送信エラー: {response.status_code} - {response.text}")
        return {
            "status": "error",
            "message": f"Slack通知送信エラー: {response.status_code}",
            ...
        }

        問題: response.textをログには出すが、返り値には含めていない。デバッグ時に情報が不足する可能性があります。

        推奨修正:
        error_msg = f"Slack通知送信エラー: {response.status_code} - {response.text[:100]}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            ...
        }

        6. 依存関係の管理

        requestsライブラリを使用していますが、requirements.txtやpyproject.tomlへの追加は確認できません。

        推奨: 依存関係ファイルにrequestsを追加

        ---
        💡 その他の提案

        7. テストコードの追加

        test_connection()メソッドがありますが、実際に使用されていません。

        推奨:
        - CLIから--test-slackフラグでテスト実行できるようにする
        - ユニットテストを追加

        8. Slack通知の内容最適化

        現在は2000文字でカットしていますが、Slackの制限は40,000文字です。

        推奨:
        - より長い内容を送信可能にする
        - または要約機能を追加

        ---
        📋 マージ前のチェックリスト

        - マージコンフリクトの解決 (mergeable: false)
        - Makefileのデフォルト動作を修正
        - 型ヒントをTupleに修正
        - Markdown変換ロジックを改善
        - requestsを依存関係に追加
        - GitHub Issue URLフィールドの重複を修正

        ---
        📝 総評

        良い機能追加ですが、上記の問題を修正してからマージすることを推奨します。特にMakefileのデフォルト動作変更は、既存ユーザーに影響を与え
        る可能性があります。
        ```

## Cursor で使用する場合

xxx

## 参考サイト

- https://github.com/github/github-mcp-server/blob/main/docs/installation-guides/install-claude.md
- https://github.com/github/github-mcp-server/blob/main/docs/installation-guides/install-cursor.md
