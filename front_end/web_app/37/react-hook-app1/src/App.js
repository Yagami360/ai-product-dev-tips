import React, { useState, useEffect } from 'react'
import './App.css';

// 関数コンポーネントにおいても、コンポーネントの呼び出し側で <コンポーネント名 args1="" args2="" ... /> で指定されたタグ属性の値は、props 引数で取得出来る
function Message(props) {
  return (
    <div>
      <p>{props.msg}</p>
    </div>
  )
}

function App() {
  // ステートフックの宣言
  // 第１戻り値には、state の値が入る。
  // 第２戻り値には、state の値を変更する関数が入る。
  // 引数には、state の初期値を設定
  const [counter, setCounter] = useState(0)
  const [msg, setMsg] = useState("sum : 0")

  // 入力ボタンクリック時のイベントハンドラ
  // 関数コンポーネント内なので、const 関数名 = () => {} の形式でイベントハンドラを定義する
  const onChangeCounter = (event)=>{
    setCounter(event.target.value)
  }

  // 副作用フックで実際の更新処理を定義
  // この副作用フックは、state 更新時に自動的に呼び出される
  useEffect(() => {
    let sum = 0
    for (let i = 0;i <= counter;i++) {
      sum += i
    }
    setMsg("sum : " + sum)
  })

  // 関数コンポーネントでも（クラスコンポーネントのときと同じように）<コンポーネント名 args1="" args2="" ... /> の形式ででタグ属性を指定出来る
  // useState() メソッドで取得した第１戻り値（＝state の値）を、別の関数コンポーネントのタグ属性に指定にて渡す
  return (
    <div className="App">
      <header className="App-header">
        <h1>React Hook Sample App</h1>
        <Message msg={msg} />
        <div className="form-group">
          <input type="number" className="form-control" onChange={onChangeCounter} />
        </div>
      </header>
    </div>
  );
}

export default App;
