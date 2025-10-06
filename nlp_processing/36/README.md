# MCP サーバーを自作して MCP クライアント（Claude Code CLI や Cursor など）で利用する

## 方法

### MCP サーバーを作成する

1. Python パッケージの `mcp` をインストールする

    ```bash
    pip install mcp
    ```

    MCP サーバーは、FastAPI などを利用して実装することもできるが、Python パッケージの `mcp` を利用すると実装が簡単

1. MCP サーバーの Python コードを実装する

    `mcp` を利用した MCP サーバーの Python コードを実装する

    [`mcp_server.py`](mcp_server.py)


### MCP クライアント側で MCP サーバーを利用する

#### Claude Code CLI で MCP サーバーを利用する場合

1. Claude Code CLI で MCP サーバーを登録する

    - 方法1: CLI で登録する場合

        ```bash
        # MCPサーバーを登録（プロジェクトスコープ）
        claude mcp add hello-world-mcp-server \
            --scope project \
            -- uv run --directory /Users/yusukesakai/personal/ai-product-dev-tips/nlp_processing/36 python mcp_server.py
        ```

        プロジェクトスコープで作成した場合は、コマンド実行可ディレクトリ以下に `.mcp.json` が作成される

    - 方法2: 設定ファイルで登録する場合

        Claude CLI が認識しているプロジェクトルート（今回のケースでは `ai-product-dev-tips` ディレクトリ）に `.mcp.json` ファイルを作成：

        ```json
        {
        "mcpServers": {
            "hello-world-mcp-server": {
              "type": "stdio",
                "command": "uv",
                "args": [
                    "run", 
                    "--directory", 
                    "/Users/yusukesakai/personal/ai-product-dev-tips/nlp_processing/36",
                    "python", 
                    "mcp_server.py"
                ]
                }
        }
        }
        ```

    その後、Claude Code CLIで自動認識されます。

1. 登録されたMCPサーバーを確認する

    ```bash
    # 登録済みMCPサーバーの一覧を表示
    claude mcp list

    # 特定のサーバーの詳細を確認
    claude mcp get hello-world-mcp-server
    ```

1. Claude Code CLI に接続する

    ```bash
    claude
    ```

1. （オプション）Claude Code CLI で登録されたMCPサーバーを確認する

    ```bash
    /mcp hello-world-mcp-server
    ```
    ```bash
    > /mcp hello-world-mcp-server 
    ╭────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
    │ Hello-world-mcp-server MCP Server                                                                          │
    │                                                                                                            │
    │ Status: ✔ connected                                                                                        │
    │ Command: uv                                                                                                │
    │ Args:run --directory /Users/yusukesakai/personal/ai-product-dev-tips/nlp_processing/36 python              │
    │      mcp_server.py --scope project                                                                         │
    │ Config location: /Users/yusukesakai/.claude.json [project:                                                 │
    │                  /Users/yusukesakai/personal/ai-product-dev-tips/nlp_processing/36]                        │
    │ Capabilities: tools                                                                                        │
    │ Tools: 2 tools                                                                                             │
    │                                                                                                            │
    │ ❯ 1. View tools                                                                                            │
    │   2. Reconnect
    ```

    ```bash
    /mcp hello-world-mcp-server get_current_time
    ```
    ```bash
    ╭────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
    │ get_current_time (hello-world-mcp-server)                                                                  │
    │                                                                                                            │
    │ Tool name: get_current_time                                                                                │
    │ Full name: mcp__hello-world-mcp-server__get_current_time                                                   │
    │                                                                                                            │
    │ Description:                                                                                               │
    │ 現在の日時を取得します                                                                                     │
    │                                                                                                            │
    │ Parameters:                                                                                                │
    │   • format: string - 日時のフォーマット(デフォルト: '%Y-%m-%d %H:%M:%S')
    ```

    Full name で MCP サーバーを使用可能

1. Claude Code CLI でMCPサーバーのツールを使用する

    ```bash
    mcp__hello-world-mcp-server__get_current_time
    ```
    ```bash
    > mcp__hello-world-mcp-server__get_current_time 
    ⎿  ⧉ Selected 1 lines from README.md in Cursor

    ⏺ It looks like you're trying to use an MCP (Model Context Protocol) tool. The mcp__hello-world-mcp-server__get_current_time function is available as a
    tool, not a slash command.

    Let me call it for you:

    ╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
    │ Tool use                                                                                                                                                     │
    │                                                                                                                                                              │
    │   hello-world-mcp-server - get_current_time() (MCP)                                                                                                          │
    │   現在の日時を取得します                                                                                                                                     │
    │                                                                                                                                                              │
    │ Do you want to proceed?                                                                                                                                      │
    │ ❯ 1. Yes                                                                                                                                                     │
    │   2. Yes, and don't ask again for hello-world-mcp-server - get_current_time commands in /Users/yusukesakai/personal/ai-product-dev-tips/nlp_processing/36    │
    │   3. No, and tell Claude what to do differently (esc)                                                                                                        │
    │                                                                                                                                                              │
    ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

      Let me call it for you:
    ⎿  現在の時刻: 2025-10-06 10:52:44                                                                                                                       

    ⏺ 現在の時刻: 2025-10-06 10:52:44
    ```

1. MCPサーバーの管理コマンド

    ```bash
    # MCPサーバーを削除
    claude mcp remove hello-world-mcp-server

    # MCPサーバーを一時的に無効化
    claude mcp disable hello-world-mcp-server

    # MCPサーバーを有効化
    claude mcp enable hello-world-mcp-server
    ```

#### Cursor で MCP サーバーを利用する場合

1. Cursor の MCP 設定ファイルを作成する

    - グローバル設定にする場合

        <img width="800" alt="Image" src="https://github.com/user-attachments/assets/88a9e535-2905-4007-a346-2b04ccd20235" />

        Cursor の MCP 設定ファイル `$(HOME)/.cursor/mcp_config.json` に自作した MCP サーバーの設定を追加する

    - プロジェクト設定にする場合

        `~/プロジェクトルート/.cursor/mcp.json`

    ```json
    {
        "mcpServers": {
            "hello-world-mcp-server": {
                "command": "uv",
                "args": [
                    "run", 
                    "--directory", 
                    "/Users/yusukesakai/personal/ai-product-dev-tips/nlp_processing/36",
                    "python", 
                    "mcp_server.py"
                ],
                "alwaysAllow": [
                    "add",
                    "get_current_time",
                    "echo"
                ],
                "disabled": false,
                "env": {}
            }
        }
    }
    ```

    - `alwaysAllow.add`: MCPサーバーが提供するツールを自動的に追加・利用可能にする権限

    - `alwaysAllow.get_current_time`, `alwaysAllow.echo` : 自作 MCP サーバーの `list_tools()` メソッドで定義したツール名

1. Cursor を再起動する

    <img width="800" alt="Image" src="https://github.com/user-attachments/assets/5df8bd14-3e35-4336-a06b-a09367d495e4" />

    再起動後に、自作した MCP サーバーが有効化される（緑の丸が表示されていれば正常動作）

1. Cursor の UI から自作 MCP サーバーを利用する

    Cursor の UI から「hello-world-mcp-server」や「"Hello World!" をエコーして」のような文章を入力する

    > Cursor 側で MCP サーバーを起動するので、予め MCP サーバーを起動させておく必要はなし

    <img width="800" alt="Image" src="https://github.com/user-attachments/assets/2cc0eb64-fc8b-4f9a-b885-7c40e95fbb4f" />

    <img width="800" alt="Image" src="https://github.com/user-attachments/assets/d058dfce-e76c-4080-b59c-20f9a36310bb" />

## 参考サイト

- https://docs.claude.com/ja/docs/claude-code/mcp