# Go 言語で Gin を使用して簡単な REST API を作成する

## ■ 方法

1. Go lang をインストールする
    - MacOS の場合
        ```sh
        brew install go
        ```

    - Linux の場合
        ```sh
        ```

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

1. Gin を使用した Go lang での REAT API のコードを作成する<br>
    ```go
    package main

    import "net/http"					//
    import "github.com/gin-gonic/gin"	// Web フレームワーク Gin


    func main() {
        engine := gin.Default()		// := は変数型をの省略して宣言する場合の Go 構文

        engine.GET("/", func(c *gin.Context) {
            c.JSON(http.StatusOK, gin.H{
                "message": "hello world",
            })
        })
        engine.Run(":3000")
    }
    ```

    ポイントは、以下の通り

    - xxx

1.  Go lang での REAT API のコードを実行し、サーバーを起動する
    - コンパイルなしで実行する場合
        ```sh
        # コンパイルして実行
        go build main.go

        # コンパイルされたファイルを実行
        .main
        ```

    - コンパイルありで実行する場合
        ```sh
        go run main.go
        ```

1. 起動したサーバーにブラウザアクセスする
    ```sh
    open https://localhost:3000
    ```

## ■ 参考サイト

- https://qiita.com/Syoitu/items/8e7e3215fb7ac9dabc3a