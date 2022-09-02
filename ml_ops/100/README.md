# 【Golang】goroutine と Channel を使用してマルチスレッド処理を行う

- goroutine<br>
  Go lang におけるスレッド。複数の goroutine を実行することでマルチスレッド処理を行うことができる<br>
  `go 関数名()` で、その関数を goroutine（別スレッド）で実行できる。

- Channel<br>
  ある goroutine（スレッド）から別の goroutine（スレッド）へ値を渡すための機能。<br>

## ■ 方法

1. Go lang をインストールする
    - MacOS の場合
        ```sh
        brew install go
        ```

    - Linux の場合
        ```sh
        ```

1. Channel を使用した Go lang コードを作成する<br>

    - 例１：シングルスレッド
        ```go
        package main

        import "fmt"

        func main() {
          // channel を作成する
          ch := make(chan int)

          // go 関数名() で、その関数（今回の場合は無名関数）を goroutine（別スレッド）で実行できる。
          // goroutine（スレッド） : Go におけるスレッド
          go func() {
            // channel への値の代入は、goroutine 内にて <- 演算子で行う
            ch <- 1
          }()

          // channel からの取り出しは <-ch で行う
          result := <-ch
          fmt.Println("[main_1.go]", result)
        }
        ```

        ポイントは、以下の通り

        - Channel は Go lang にデフォルト組み込まれているライブラリなので、インストールは不要

        - xxx


    - 例２：マルチスレッド
        ```go
        ```

    - 例３：Select
        ```go
        package main

        import "fmt"

        func main() {
          // channel を作成する
          ch1 := make(chan string)
          ch2 := make(chan string)

          // go func() で無名関数を goroutine（ゴルーチン）で実行
          // goroutine（ゴルーチン） : Go のランタイムに管理される軽量なスレッド（一連のプログラムの流れ）
          go func() {
            // channel への値の代入は <- 演算子で行う
            ch1 <- "one"
          }()

          go func() {
            // channel への値の代入は <- 演算子で行う
            ch2 <- "two"
          }()

          // 無限ループ
          for i := 0; i < 2; i++ {
            // select 文でチャネルの送受信操作を多重化できる。
            select {
            case msg1 := <-ch1: // ch1 から受信したときに実行される処理
              fmt.Println("[main_2.go] received", msg1)
            case msg2 := <-ch2: // ch1 から受信したときに実行される処理
              fmt.Println("[main_2.go] received", msg2)
            }
          }
        }
        ```

        ポイントは、以下の通り

        - xxx

    - 例４：Ticker を使用した定期処理
        ```go
        package main

        import (
          "fmt"
          "time"  // Ticker は time パッケージに含まれる
        )

        func main() {
          // 引数はインターバル時間
          ticker := time.NewTicker(100 * time.Millisecond)

          // タイマーを止めるための Channel
          ch_done := make(chan bool)

          // go 関数名で無名関数（func(){...}()）を goroutine（ゴルーチン）で実行
          go func() {
            // 無限ループ
            for {
              select {
              case <-ch_done: // ch_done から受信したときに実行される処理
                fmt.Println("Ticker stopped")
                return
              case t := <-ticker.C: // ticker.C はチャンネルなので <- で値を取りだせる
                fmt.Println("Tick at", t)
              }
            }
          }()

          // 1000 msec 待つ
          time.Sleep(1000 * time.Millisecond)

          // ticker.C の更新を停止
          ticker.Stop()

          // タイマー停止用のチャンネルに値を代入
          ch_done <- true
        }
        ```

        ポイントは、以下の通り

        - Ticker は time パッケージに含まれる

        - xxx


1. Go lang での REAT API のコードを実行し、サーバーを起動する
    - コンパイルなしで実行する場合
        ```sh
        # コンパイルして実行
        go build main_1.go
        go build main_2.go
        go build main_3.go

        # コンパイルされたファイルを実行
        ./main_1
        ./main_2
        ./main_3
        ```

    - コンパイルありで実行する場合
        ```sh
        go run main_1.go
        go run main_2.go
        go run main_3.go
        ```


## ■ 参考サイト

- https://selfnote.work/20201110/programming/how-to-use-channel-on-golang/
- https://qiita.com/taigamikami/items/fc798cdd6a4eaf9a7d5e