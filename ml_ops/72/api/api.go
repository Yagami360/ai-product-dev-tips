package main

import "io"
import "encoding/json"
import "fmt"
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
    // ルーター機能を持つ `http.ServeMux` オブジェクトを作成する
    mux := http.NewServeMux()

    // http:${IP_ADDRES}:${PORT} のエンドポイントにリクエスト時のコールバック関数（ハンドラー）を設定
    mux.Handle("/", http.HandlerFunc(hello))
    mux.Handle("/health", http.HandlerFunc(health))

    // http.ListenAndServe で API 起動
    http.ListenAndServe((*host) + ":" + (*port), mux)
}

// http:${IP_ADDRES}:${PORT} アクセス時のハンドラー
func hello(w http.ResponseWriter, _ *http.Request) {
	// HTMLテキストをhttp.ResponseWriterへ書き込む
	io.WriteString(w, `
    <!DOCTYPE html>
    <html lang="ja">
    <head>
      <meta charset="UTF-8">
      <title>Go | net/httpパッケージ</title>
    </head>
    <body>
      <h1>Hello, World!</h1>
    </body>
    </html>
`)
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
