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
