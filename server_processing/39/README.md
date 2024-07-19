# 【Elixir】 Phoenix + PlugCowboy + WebSockex での Websocket サーバーを構築する

## ■ 方法

1. 「[【Elixir】Phoenix を使用して簡単な REST API を作成する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/86)」記載の方法に従って、Phoenix プロジェクトを作成する

1. プロジェクトディレクトリに移動する
    ```sh
    cd ${PROJECT_NAME}
    ```

1. PlugCowboy と WebSockex を追加する<br>
    `${PROJECT_NAME}/mix.exs` に PlugCowboy と WebSockex を追加し、インストールする

    ```elixir
    # mix.exs
    defp deps do
        [
            {:plug_cowboy, "~> 2.1"},
            {:websockex, "~> 0.4.0"},
        ]
    end
    ```

    ```sh
    mix deps.get
    ```

1. API のルーターのコードを修正する<br>
    API のルーターを定義しているコード `${PROJECT_NAME}/lib/phoenix_websoket_api_web/router.ex` を修正する

    ```elixir
    ```

1. Phoenix サーバーを起動する<br>
    ```sh
    mix phx.server
    ```

1. API にリクエストを出す
    ```sh
    # health check
    echo "[GET method] ヘルスチェック\n"
    curl http://0.0.0.0:4000/api/health
    echo "\n"
    ```
