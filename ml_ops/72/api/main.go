package main

import "fmt"
import "flag"                       // コマンドライン引数
import "net/http"					//

func main() {
    fmt.Printf("start main()")

    //-------------------------
    // コマンドライン引数
    //-------------------------
    host := flag.String("host", "0.0.0.0", "")
    port := flag.String("port", "5000", "")

    //-------------------------
    // net/http を使用した API
    //-------------------------
    // `http.ServeMux` オブジェクトを作成する
    mux := http.NewServeMux()

    // http:${IP_ADDRES}:${PORT}/health のエンドポイントにリクエスト時のコールバック関数（ハンドラー）を設定
    // http.HandlerFunc() : interface
    mux.Handle("/health", http.HandlerFunc(health))

    // http.ListenAndServe で API 起動
    http.ListenAndServe(":" + (*port), mux)
}

// http:${IP_ADDRES}:${PORT}/health アクセス時のハンドラー
func health(w http.ResponseWriter, _ *http.Request) {
    w.WriteHeader(http.StatusOK)
    fmt.Fprintf(w, "health ok")
}
