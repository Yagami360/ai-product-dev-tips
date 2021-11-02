import React, { useState } from 'react'
import './App.css'

function App() {
  // ステートフックの宣言
  // 第１戻り値 count には、state の値が入る。
  // 第２戻り値 setCount には、state の値を変更する関数が入る。
  // 引数には、state（今の場合 count）の初期値を設定
  const [countA, setCountA] = useState(0)

  // useState() メソッドを複数個使用すれば、複数のステートを作成することが出来る。
  const [countB, setCountB] = useState(0)

  // ボタンクリック時のイベントハンドラ
  // App コンポーネントは、関数コンポーネントなので、const 関数名 = () => {} で宣言する
  const clickFuncA = () => {
    // useState() で取得したstate の値を変更する関数 setCount() を呼び出す
    // 引数には、state の更新式を設定
    setCountA(countA + 1)
  }
  
  const clickFuncB = () => {
    // useState() で取得したstate の値を変更する関数 setCount() を呼び出す
    // 引数には、state の更新式を設定
    setCountB(countB + 1)
  }

  // useState() メソッドで取得した第１戻り値（＝state の値）`countA` は、`App` コンポーネントの return 分（JSX形式）の中で `{countA}` とすることで、表示させることが出来る
  return (
    <div>
      <h1>React Hook Sample App</h1>
      <div>
        <p>clickA: {countA} times!</p>
        <p>clickB: {countB} times!</p>
        <div>
          <button onClick={clickFuncA}>ClickA</button>
          <button onClick={clickFuncB}>ClickB</button>
        </div>
      </div>
    </div>
  )
}

export default App