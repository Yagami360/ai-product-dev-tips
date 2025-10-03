# MCP サーバーを自作して MCP クライアント（Claude Code や Cursor など）で利用する

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

#### Calude Code で MCP サーバーを利用する場合

1. xxx

#### Cursor で MCP サーバーを利用する場合

1. Cursor の MCP 設定ファイルを作成する

    <img width="800" alt="Image" src="https://github.com/user-attachments/assets/88a9e535-2905-4007-a346-2b04ccd20235" />

    Cursor の MCP 設定ファイル `$(HOME)/.cursor/mcp_config.json` に自作した MCP サーバーの設定を追加する

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
