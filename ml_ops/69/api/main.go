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
