# 【Go】 Go 言語の標準ライブラリ net/http を使用して簡単な REST API を作成する

## ■ 方法

### ◎ docker を使用する場合

1. Golang の Dockerfile を作成する<br>
    ```Dockerfile
    FROM golang:1.17-alpine

    # UNIX コマンドのインストール
    RUN apk update && apk add git

    # /api ディレクトリ以下にライブラリをインストール
    WORKDIR /api
    RUN go mod init api

    WORKDIR /api
    ```

    ポイントは以下の通り

    - 軽量 Linux であるの alpine の golang インストール済みイメージ `golang:1.17-alpine` をベースイメージにしている

    - alpine なので、`apk`　コマンドで各種 UNIX コマンドをインストールしている

    - `net/http` は標準ライブラリなので、`RUN go get` で追記のライブラリをインストールする必要はない

1. docker-compose を作成する<br>
    ```yml
    version: '3'
    services:
      go-gin-api-server:
        container_name: go-api-container
        image: go-api-image
        build:
          context: "api/"
          dockerfile: Dockerfile
        volumes:
          - ${PWD}/api:/api
        ports:
          - "3000:3000"
        tty: true
        environment:
          TZ: "Asia/Tokyo"
          LC_ALL: C.UTF-8
          LANG: C.UTF-8
        command: bash -c "go run main.go --host 0.0.0.0 --port 3000"
    ```

1. `net/http` を使用した Go lang での REAT API のコードを作成する<br>
  <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/176985744-1df0919a-8f99-4cd2-b97d-668d6ceacab8.png">

    > - `http.Server`<br>
    >   xxx

    > - `http.ServeMux`<br>
    >    HTTP リクエストが来た時に、そのエンドポイント URL にマッチしたハンドラを呼び出すルーター

    > - `ServeHTTP`<br>
    >    HTTP リクエストを受けて HTTP レスポンスを返す処理が記述されたメソッド

    > - `http.Handler`<br>
    > ServeHTTP メソッドを定義するインターフェイス。`http.ServeMux` の `Handle` メソッドの引数がこの interface型になっている
    >    ```go
    >    type Handler interface {
    >      ServeHTTP(ResponseWriter, *Request)
    >    }
    >    ```

    > - `http.HandlerFunc()`<br>
    >    リクエスト受付時のイベントハンドラを定義するときに、そのイベントハンドラが持つべき型を定義したインターフェイス

  ```go
  ```

  - `net/http` を使用した、実際のリクエスト＆レスポンス手順は、以下の通り
  
    1. リクエスト受付時のハンドラー（今回の場合は `health()` ）を定義する。このハンドラーの引数は `func health(w http.ResponseWriter, _ *http.Request)` のように interface `http.HandlerFunc` に従ったインターフェイス仕様になっている

    1. `http.NewServeMux()` で、`http.ServeMux` オブジェクトを作成する

    1. `http.ServeMux` オブジェクトの `Handle()` メソッドで、前述で定義したリクエスト時のコールバック関数（ハンドラー）`health` を設定する。この際ハンドラー `health` を interface `http.HandlerFunc` 型に変換したものを設定する。
    
        そして、`Handle()` メソッドにより、インターフェイス `http.Handler` 型のオブジェクトが作成され、HTTP リクエストを受けて HTTP レスポンスを返す処理が記述されたメソッドである `ServeHTTP()` メソッドが、`http.Server` に渡されてレスポンス処理が行われる動作になる 

    1. `http.ListenAndServe()` を使用して、API を起動する


1. API を起動する
    ```sh
    docker-compose -f docker-compose.yml stop
    docker-compose -f docker-compose.yml up -d
    ```

1. 起動した API サーバーにアクセスする
    ```sh
    curl http://localhost:${PORT}/health
    ```

## ■ 参考サイト

- https://journal.lampetty.net/entry/understanding-http-handler-in-go
- https://future-architect.github.io/articles/20210714a/