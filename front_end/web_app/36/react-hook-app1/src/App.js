import React, { useState } from 'react'
import './App.css';

// 関数コンポーネントにおいても、コンポーネントの呼び出し側で <コンポーネント名 args1="" args2="" ... /> で指定されたタグ属性の値は、props 引数で取得出来る
function User(props) {
  return (
    <div>
      <p>id:{props.id}, name:{props.name}</p>
    </div>
  )
}

function App() {
  // ステートフックの宣言
  // 第１戻り値には、state の値が入る。
  // 第２戻り値には、state の値を変更する関数が入る。
  // 引数には、state の初期値を設定
  const [id, setId] = useState(1)
  const [name, setName] = useState("Yagami")

  // 名前入力ボタンクリック時のイベントハンドラ
  // 関数コンポーネント内なので、const 関数名 = () => {} の形式でイベントハンドラを定義する
  const onClickId = ()=>{
    let res = window.prompt('type your id')
    setId(res)
  }
  const onClickName = ()=>{
    let res = window.prompt('type your name')
    setName(res)
  }

  // 関数コンポーネントでも（クラスコンポーネントのときと同じように）<コンポーネント名 args1="" args2="" ... /> の形式ででタグ属性を指定出来る
  // useState() メソッドで取得した第１戻り値（＝state の値）を、別の関数コンポーネントのタグ属性に指定にて渡す
  return (
    <div className="App">
      <header className="App-header">
        <h1>React Hook Sample App1</h1>
        <User id={id} name={name} />
        <button onClick={onClickId} className="btn btn-primary">input your id</button>
        <button onClick={onClickName} className="btn btn-primary">input your name</button>
      </header>
    </div>
  );
}

export default App;
