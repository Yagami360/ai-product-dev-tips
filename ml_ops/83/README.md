# Elixir 言語で Phoenix を使用して簡単な REST API を作成する（docker 使用）

## ■ 方法

1. Dockerfile を作成する
    ```Dockerfile
    ```

1. docker-compose.yml を作成する
    ```yml
    ```

    ポイントは、以下の通り

    - `mix`　コマンドは、コンパイル＆テスト＆特定のコマンド実行などを複合的に行うコマンドで、以下のようなコマンドがある
        - `mix new ${PROJECT_NAME}` : プロジェクトを作成する
        - `mix compile` : プロジェクトのコンパイルを行う
        - `mix test` : プロジェクトのテストを実行
        - `mix run` : プロジェクト内の特定のコマンドを実行

        > ここでいうプロジェクトとは、`mix.exs` という名前のファイルに配置されたモジュール

    - `mix phx.server` で、Web フレームワークである Phoenix のサーバーを起動している（`mix run` と同じようなもの）<br>
        この `mix phx.server` を実行する際には、他の mix コマンドと同様に `mix.exs` でプロジェクトが作成されている必要がある

1. `mix.exs` ファイルを作成する<br>
    Elixir の Mix におけるプロジェクトとは、`mix.exs` という名前のファイルに配置されたモジュールで `Mix.Project` を使用して定義する。<br>
    ```ex
    defmodule MyApp.MixProject do
        use Mix.Project

        def project do
            [
                app: :my_app,
                version: "1.0.0"
            ]
        end
    end
    ```

1. `api/router.ex` に API のコード（ルーター）を作成する<br>
    ```ex
    ```

## ■ 参考サイト

- https://qiita.com/akameco/items/1920e351328b1cc0ace3
- https://qiita.com/nishiuchikazuma/items/be911dd1d202c1227d19
