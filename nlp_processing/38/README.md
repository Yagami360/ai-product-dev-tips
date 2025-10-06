# Claude Code CLI MCP サーバーを使用して Cursor から Claude Code を使用する

## 方法

1. Cursor の MCP 設定ファイルを作成する

    - グローバル設定にする場合

        Cursor の MCP 設定ファイル `$(HOME)/.cursor/mcp.json` に自作した MCP サーバーの設定を追加する

        ```json
        {
          "mcpServers": {
            "claude_code": {
              "command": "claude",
              "args": ["mcp", "serve"],
              "env": {}
            }
          }
        }
        ```

1. Cursor を再起動する

  > TODO: なぜか tools を認識しない

      > `"command":` " に `claude` コマンドのフルパス（`which claude` で確認可能）を指定しても tools を認識しない

1. Cursor の UI から Claude Code MCP サーバーを利用する

    Cursor の UI から「Claude Code の MCP サーバーを使用したいです」のような文章を入力する

## 参考サイト

- https://dev.classmethod.jp/articles/cursor-claudecode/