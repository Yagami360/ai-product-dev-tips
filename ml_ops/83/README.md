# Elixir 言語で Phoenix を使用して簡単な REST API を作成する（docker 使用）

## ■ 方法

1. Dockerfile を作成する<br>
    ```Dockerfile
    FROM elixir:1.13.1-slim

    RUN apt-get update && apt-get install -y \
        inotify-tools \
        git \
        npm \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

    # phoenix 関連のライブラリ更新
    RUN mix local.hex --force
    RUN mix local.rebar --force
    RUN mix archive.install hex phx_new --force

    WORKDIR /api
    ```

    ポイントは、以下の通り

    - phoenix では、アセットファイルのコンパイルに node.js 製ツールを使用するので、`apt-get install npm` で node.js もインストールしている

    - `mix do local.hex --force, mix local.rebar --force, archive.install hex phx_new --force` の部分で、phoenix をインストールしている

1. docker-compose.yml を作成する
    ```yml
    ```

    ポイントは、以下の通り

    - `mix phx.server` で、Web フレームワークである Phoenix のサーバーを起動している（`mix run` と同じようなもの）<br>
        この `mix phx.server` を実行する際には、他の mix コマンドと同様に `mix.exs` でプロジェクトが作成されている必要がある

1. `api/router.ex` に API のコード（ルーター）を作成する<br>
    ```ex
    ```

## ■ 参考サイト

- https://qiita.com/akameco/items/1920e351328b1cc0ace3
