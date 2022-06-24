# Go 言語で Gin を使用して簡単な REST API を作成する

## ■ 方法

### ◎ Docker を使用しない場合

1. Go lang をインストールする
    - MacOS の場合
        ```sh
        brew install go
        ```

    - Linux の場合
        ```sh
        ```

<a id="Ginをインストールする"></a>

1. Gin をインストールする<br>
    - `go get` でインストールする場合
        ```sh
        mkdir api
        cd api
        go mod init api
        go get -u github.com/gin-gonic/gin
        ```

        > `go get` でインストールする場合は、ローカル環境 `${PWD}/${go mod init で指定したディレクトリ}` 以下にパッケージがインストールされる

    - `go install` でインストールする場合
        ```sh
        go install github.com/gin-gonic/gin@latest
        ```

        > `go install` でインストールした場合は、グローバル環境 `$GOPATH/bin` 以下にパッケージがインストールされる

        > `go install` は、Go lang のバージョン `go1.16` 以降に追加されたコマンド

<a id="Ginを使用したGolangでのREATAPIのコードを作成する"></a>

1. Gin を使用した Go lang での REAT API のコードを作成する<br>
    ```go
    package main

    import "flag"                       // コマンドライン引数
    import "net/http"					//
    import "github.com/gin-gonic/gin"	// Web フレームワーク Gin


    func main() {
        // コマンドライン引数
        port := flag.String("port", "3000", "")

        // gin の Engine オブジェクトを作成
        // := は変数型をの省略して宣言する場合の Go 構文
        engine := gin.Default()

        // GET リクエストに対してのレスポンス処理
        // 第１引数 : `https://${IP_ADDRESS}:${PORT}` に続くエンドポイントの URL を示す。
        // 第２引数 : 第１引数で指定したエンドポイントにリクエストされたときのレスポンス処理を定義したメソッドが入る
        engine.GET("/health", func(c *gin.Context) {
            // 無名関数の引数 `*gin.Context` の `*` は（ポインタの）参照渡しの Go 構文なので、型 `gin.Context` の変数のポインタ `c` を引数で渡している
            c.JSON(
                http.StatusOK, 
                gin.H{ "health": "ok" },
            )
        })

        // PORT=3000 で API 起動
        engine.Run(":" + *port)
    }
    ```

    ポイントは、以下の通り

    - `engine := gin.Default()` で gin の Engine オブジェクトを作成している。Engine オブジェクトには API のエンドポイント、Middleware（Endpoint処理を実行する前後に共通の処理）、その他 Web ページ用の Template やそこで使われる funcMap（html側で使用できる関数）など様々なものを登録しておくことができる

        > `:=` は変数型をの省略して宣言する場合の Go 構文

    - `engine.GET(第１引数, 第２引数)` で、Engine を介して、GET リクエストに対してのエンドポイントを登録する<br>
        - 第１引数 : `https://${IP_ADDRESS}:${PORT}` に続くエンドポイントの URL を示す。<br>

            > 今回の例では `"health"` であるので、API のエンドポイントは `https://${IP_ADDRESS}:${PORT}/health` になる

        - 第２引数 : 第１引数で指定したエンドポイントにリクエストされたときのレスポンス処理を定義したメソッドが入る

            > 今回の例では、無名関数 `func(c *gin.Context) {...}` を設定している

            > 無名関数の引数 `*gin.Context` の `*` は（ポインタの）参照渡しの Go 構文なので、型 `gin.Context` の変数のポインタ `c` を引数で渡していることになる。そして、`gin.Context` オブジェクトを使うことで、URL に付随したパラメータの取得や POST で送信されたデータの取得などを行うことができる。

    - `flag` ライブラリを import し、`port := flag.String("port", "3000", "")` のような形式で引数定義することで、コマンドライン引数を利用できるようになる

1.  Go lang での REAT API のコードを実行し、サーバーを起動する
    - コンパイルなしで実行する場合
        ```sh
        # コンパイルして実行
        go build main.go --port ${PORT}

        # コンパイルされたファイルを実行
        .main
        ```

    - コンパイルありで実行する場合
        ```sh
        go run main.go --port ${PORT}
        ```

1. 起動した API サーバーにアクセスする
    ```sh
    curl http://localhost:${PORT}/health
    ```

### ◎ Docker を使用する場合

1. Golang + Gin 環境の Dockerfile を作成する<br>
    ```Dockerfile
    FROM golang:1.17-alpine

    # UNIX コマンドのインストール
    RUN apk update && apk add git

    # /api ディレクトリ以下に Go ライブラリをインストール
    WORKDIR /api
    RUN go mod init api
    RUN go get -u github.com/gin-gonic/gin

    WORKDIR /api
    ```

    ポイントは以下の通り

    - 軽量 Linux であるの alpine の golang インストール済みイメージ `golang:1.17-alpine` をベースイメージにしている

    - alpine なので、`apk`　コマンドで各種 UNIX コマンドをインストールしている

    - 「[Gin をインストールする](#Ginをインストールする)」と同様の方法で、`/api` ディレクトリ以下に Go ライブラリをインストールしている

1. docker-compose を作成する<br>
    ```yml
    version: '3'
    services:
      go-gin-api-server:
        container_name: go-gin-api-container
        image: go-gin-api-image
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

1. API のコードを作成する
    「[Gin を使用した Go lang での REAT API のコードを作成する](#Ginを使用したGolangでのREATAPIのコードを作成する)」と同様に、Gin を使用した Golang での API のコードを作成する

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

- https://qiita.com/Syoitu/items/8e7e3215fb7ac9dabc3a
- https://zenn.dev/ajapa/articles/6471ac0c612fda