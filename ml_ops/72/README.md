# net/http を使用して簡単な REST API を作成する

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

1. `net/http` を使用した Go lang での REST API のコードを作成する<br>
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
		package main

		import "fmt"
    import "encoding/json"
		import "flag"                       // コマンドライン引数
		import "net/http"					//

		func main() {
				fmt.Printf("start main()")

				//-------------------------
				// コマンドライン引数
				//-------------------------
				host := flag.String("host", "0.0.0.0", "")
				port := flag.String("port", "5001", "")

				//-------------------------
				// net/http を使用した API
				//-------------------------
				// `http.ServeMux` オブジェクトを作成する
				mux := http.NewServeMux()

				// http:${IP_ADDRES}:${PORT} のエンドポイントにリクエスト時のコールバック関数（ハンドラー）を設定
        mux.Handle("/health", http.HandlerFunc(health))

				// http.ListenAndServe で API 起動
				http.ListenAndServe((*host) + ":" + (*port), mux)
		}

    // http:${IP_ADDRES}:${PORT}/health アクセス時のハンドラー
    func health(w http.ResponseWriter, _ *http.Request) {
        //w.WriteHeader(http.StatusOK)
        w.Header().Set("Content-Type", "application/json")
    
      // json 形式でのレスポンスの内容を構造体で定義
      // `json:"status"` で json 出力時のキー名を指定できる
      type Responce struct {
        Status int `json:"status"`
        Health string `json:"health"`
      }	

      // 初期化
      responce := Responce{http.StatusOK, "ok"}

      // json.Marshal() で json 形式に変換
      responce_json, _ := json.Marshal(responce)

      // 
      w.Write(responce_json)
    }
    ```

    - `net/http` を使用した、実際のリクエスト＆レスポンス手順は、以下の通り
  
      1. リクエスト受付時のハンドラー（今回の場合は `health()` ）を定義する。このハンドラーの引数は `func health(w http.ResponseWriter, _ *http.Request)` のように interface `http.HandlerFunc` に従ったインターフェイス仕様になっている

      1. `http.NewServeMux()` で、`http.ServeMux` オブジェクトを作成する

      1. `http.ServeMux` オブジェクトの `Handle()` メソッドで、前述で定義したリクエスト時のコールバック関数（ハンドラー）`health` を設定する。この際ハンドラー `health` を interface `http.HandlerFunc` 型に変換したものを設定する。<br>
          そして、`Handle()` メソッドにより、インターフェイス `http.Handler` 型のオブジェクトが作成され、HTTP リクエストを受けて HTTP レスポンスを返す処理が記述されたメソッドである `ServeHTTP()` メソッドが、`http.Server` に渡されてレスポンス処理が行われる動作になる 

      1. `http.ListenAndServe()` を使用して、Web サーバーを起動する

1. API サーバーを起動する
    ```sh
    docker-compose -f docker-compose.yml stop
    docker-compose -f docker-compose.yml up -d
    ```

1. 起動した API サーバーに GET リクエストする

    - `curl` コマンドを使用する場合
      ```sh
      curl http://localhost:${PORT}/health
      ```

    - Go lang でのリクエストスクリプトを使用する場合<br>

      1. `net/http` や `net/url` を使用して GET リクエストのスクリプトを作成する
          ```go
          package main

          import "io/ioutil"
          //import "encoding/json"
          import "fmt"
          import "flag"                       // コマンドライン引数
          import "net/http"					//
          import "net/url"

          func main() {
              //-------------------------
              // コマンドライン引数
              //-------------------------
              host := flag.String("host", "0.0.0.0", "")
              port := flag.String("port", "5001", "")

              //-------------------------
              // net/http & net/url を使用したリクエスト処理
              //-------------------------		
              // url.URL 構造体を作成し、API のエンドポイント（URL）に関しての値を設定する
              // type URL struct {
              // 	Scheme string 	// スキーム : http など
              // 	Opaque string 	// 不透明URL
              // 	User *Userinfo 	// ユーザー名とパスワード
              // 	Host string 	  // ホスト情報 : ${IP_ADDRESS:${PORT} など
              // 	Path string 	  // パス
              // 	RawPath string 	// エンコードされたパスのヒント
              // 	ForceQuery bool // クエリパラメータ
              // 	RawQuery string // クエリ値 ※?は除外
              // 	Fragment string // URLフラグメント
              // }
              url := &url.URL{}		// & : 構造体へのポインタの参照で宣言
              url.Scheme = "http"
              url.Host = (*host) + ":" + (*port)
              url.Path = "health"
              urlStr := url.String()	// url文字列に変換
              fmt.Println("urlStr : ", urlStr)

              // GETリクエスト発行
              responce, error := http.Get(urlStr)
              if error != nil {
                  fmt.Println(error)
                  return
              }	

              // 関数を抜ける際に必ず response を close するように defer で close を呼ぶ
              // defer : python でいうところの finally に対応するもので、関数の return 前にコードを遅延実行する go 構文（実態は defer 構造体）
              defer responce.Body.Close()

              // レスポンスを取得し出力
              body, _ := ioutil.ReadAll(responce.Body)
              fmt.Println(string(body))
          }
          ```

          ポイントは、以下の通り

          - `net/url` ライブラリの `url.URL` 構造体を作成し、API のエンドポイント（URL）に関しての値を設定する<br>
            `url.URL` 構造体は、以下のような定義になっており、API のエンドポイント（URL）に関しての情報を集約した構造体になっている。
            ```go
            type URL struct {
              Scheme string   // スキーム : http など
              Opaque string   // 不透明URL
              User *Userinfo  // ユーザー名とパスワード
              Host string     // ホスト情報 : ${IP_ADDRESS:${PORT} など
              Path string     // パス
              RawPath string  // エンコードされたパスのヒント
              ForceQuery bool // クエリパラメータ
              RawQuery string // クエリ値 ※?は除外
              Fragment string // URLフラグメント
            }
            ```

          - `net/http` ライブラリの `http.Get()` を使用して、API に対して GET リクエストを行う。この際の引数には、上記 `url.URL` 構造体を `url.String()` で文字列（`"http://0.0.0.0:5001/health/?query=hoge"` のように文字列になる）に変換した URL を設定する

          - 関数を抜ける際に必ず `http.Get()` で取得した `response` を `defer responce.Body.Close()` のように `Close()` メソッド遅延実行する

            > `defer` : python でいうところの `finally` 構文に対応するもので、関数の return 前にコードを遅延実行する go 構文（実態は defer 構造体）

            > `responce.Body.Close()` しないと、TCPコネクションがクローズされないために、そのまま続けて http リクエストを発行され続けて、ファイルディスクリプタが枯渇してしまう

          - API からのレスポンスデータは、`http.Get()` の戻り値 `responce` の `responce.Body` プロパティに格納されている

      1. リクエストスクリプトを実行し、API に GET リクエストする
          ```sh
          go run request.go --host 0.0.0.0 --port 5001
          ```

## ■ 参考サイト

- https://journal.lampetty.net/entry/understanding-http-handler-in-go
- https://future-architect.github.io/articles/20210714a/
- https://leben.mobi/go/server_and_handler/practice/web/
- https://konboi.hatenablog.com/entry/2014/09/23/172756