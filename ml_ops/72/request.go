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
	// 	Host string 	// ホスト情報 : ${IP_ADDRESS:${PORT} など
	// 	Path string 	// パス
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