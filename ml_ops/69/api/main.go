package main

import "flag"                       // コマンドライン引数
import "net/http"					//
import "github.com/gin-gonic/gin"	// Web フレームワーク Gin


func main() {
    // コマンドライン引数
    host := flag.String("host", "0.0.0.0", "")
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
    engine.Run(*host+":" + *port)
}
