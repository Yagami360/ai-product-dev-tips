package main

import "fmt"

func main() {
	// channel を作成する
	ch1 := make(chan string)
	ch2 := make(chan string)

	// go 関数名() で、その関数（今回の場合は無名関数）を goroutine（別スレッド）で実行できる。
	// goroutine（スレッド） : Go におけるスレッド
	go func() {
		// channel への値の代入は、goroutine 内にて <- 演算子で行う
		ch1 <- "one"
	}()

	go func() {
		// channel への値の代入は、goroutine 内にて <- 演算子で行う
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
