import React, { useState } from 'react'
import './App.css';
import useLocalPersist from './LocalPersist';

// カウンター値をインクリメントする独自フック
function useAddCounter(init_counter) {
  // const ステート名
  const [counter, setCounter] = useState(init_counter)

  // const ステートを更新する関数名
  const addCounter = () => {
    setCounter(counter+1)
  }

  // return [ステート名, ステートを更新する関数名]
  return [counter, addCounter]
}

function Counter(props) {
  return (
    <div>
      <p>total counter : {props.counter}</p>
    </div>
  )
}

function App() {
  // 独自フックの使用
  // 第１戻り値には、state の値が入る。
  // 第２戻り値には、state の値を変更する関数が入る。
  // 引数には、state の初期値を設定
  const [savedData, setSavedData] = useLocalPersist("counter", 0)
  const [counter, addCounter] = useAddCounter(savedData["counter"])   // ローカルストレージに保存されたデータ savedData["counter"] で初期化
  //console.log("savedData : ", savedData)

  // 入力ボタンクリック時のイベントハンドラ
  // 関数コンポーネント内なので、const 関数名 = () => {} の形式でイベントハンドラを定義する
  const onClickAddCounter = ()=>{
    addCounter()
  }

  const onClickSaveCounter = ()=>{
    const data = {
      counter: counter,
    }
    setSavedData(data)    
  }

  // 関数コンポーネントでも（クラスコンポーネントのときと同じように）<コンポーネント名 args1="" args2="" ... /> の形式ででタグ属性を指定出来る
  // useState() メソッドで取得した第１戻り値（＝state の値）を、別の関数コンポーネントのタグ属性に指定にて渡す
  return (
    <div className="App">
      <header className="App-header">
        <h1>React Hook Sample App</h1>
        <Counter counter={counter} />
        <button onClick={onClickAddCounter} className="btn btn-primary">add counter</button>
        <button onClick={onClickSaveCounter} className="btn btn-primary">save counter</button>
      </header>
    </div>
  );
}

export default App;
