# 【Elixlir】 Phoenix 版 Plug を使用して xxx

Elixlir における Plug とは、Webリクエストに対する処理を徹底的にシンプルにするためのライブラリで、特に Phoenix においては、エンドポイント・ルーター・コントローラーなどの Phoenix コアコンポーネントは、内部的にはすべて Plug を使用して実装されている

> [Plug](https://github.com/elixir-plug/plug) は、Phoenix の機能ではなく、Elixlir の１つのライブラリになっていることに注意

Plug には、関数 Plug とモジュール Plug の2つの種類が存在する

- 関数 Plug<br>
    ```ex
    # 関数 Plug の例
    # conn : HTTP 接続におけるリクエストとレスポンスに関しての情報を格納した `Plug.Conn` 構造体のオブジェクト
    def introspect(conn, _opts) do
      IO.puts """
      Verb: #{inspect(conn.method)}
      Host: #{inspect(conn.host)}
      Headers: #{inspect(conn.req_headers)}
      """

      conn
    end
    ```
    HTTP 接続におけるリクエストとレスポンスに関しての情報を格納した [`Plug.Conn`](https://hexdocs.pm/plug/Plug.Conn.html) 構造体を引数（`conn` の部分）にもつ関数を、関数 Plug という<br>
    関数 Plug は、`plug :introspect` のように関数名をアトムとして渡すことでエンドポイント `endpoint.ex` に組み込むことができる

- モジュール Plug<br>
    ```ex
    # モジュール Plug の例
    defmodule MyPlug do
      import Plug.Conn

      def init(options) do
        # optionsの初期化
        options
      end

      # 接続(Plug.Conn)と初期化されたオプション(_opts)を受け取って、新たな接続（Plug.Conn）にして返す
      # conn : Plug.Conn オブジェクト
      def call(conn, _opts) do
        # Plugモジュールは、データを処理するためにPlug.Connに定められた関数が使える。今回の例では、put_resp_content_type とsend_resp
        conn
        |> put_resp_content_type("text/plain")
        |> send_resp(200, "Hello world")
      end
    en
    ```
    `Plug.Conn`

## ■ 方法


## ■ 参考サイト

- https://zenn.dev/koga1020/books/phoenix-guide-ja-1-5/viewer/plug
- https://www.tech-note.info/entry/phoenix-5-plug
- https://blog.emattsan.org/entry/2018/08/21/215729