package main

import (
	"fmt"
	"time" // Ticker は time パッケージに含まれる
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
