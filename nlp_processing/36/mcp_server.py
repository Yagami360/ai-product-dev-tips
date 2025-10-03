#!/usr/bin/env python3
"""
Hello World MCPサーバー

このサーバーは以下の基本的なツールを提供します：
- get_current_time: 現在の時刻を取得
- echo: 文字列をそのまま返す
"""

import asyncio
from datetime import datetime
from typing import Any, Dict

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

# MCPサーバーの初期化
server = Server("hello-world-mcp-server")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """利用可能なツールの一覧を返す"""
    return [
        Tool(
            name="get_current_time",
            description="現在の日時を取得します",
            inputSchema={
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "description": "日時のフォーマット（デフォルト: '%Y-%m-%d %H:%M:%S'）",
                        "default": "%Y-%m-%d %H:%M:%S",
                    }
                },
                "required": [],
            },
        ),
        Tool(
            name="echo",
            description="入力された文字列をそのまま返します",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "エコーする文字列"}
                },
                "required": ["message"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> list[Any]:
    """ツールを実行する"""

    if name == "get_current_time":
        # 現在時刻の取得
        format_str = arguments.get("format", "%Y-%m-%d %H:%M:%S")
        try:
            current_time = datetime.now().strftime(format_str)
            return [{"type": "text", "text": f"現在の時刻: {current_time}"}]
        except ValueError as e:
            return [{"type": "text", "text": f"フォーマットエラー: {str(e)}"}]

    elif name == "echo":
        # エコー機能
        message = arguments.get("message", "")
        return [{"type": "text", "text": f"エコー: {message}"}]

    else:
        return [{"type": "text", "text": f"不明なツール: {name}"}]


async def main():
    """メイン関数 - stdio経由でMCPサーバーを起動"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    # サーバーの起動
    asyncio.run(main())
