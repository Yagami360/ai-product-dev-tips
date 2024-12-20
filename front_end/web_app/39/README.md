# 【React】React Hooks でステートフックを永続化する

データの永続化を行っていないアプリでは、ブラウザでアプリのページをリロードすると、入力したデータなどがすべて消えてしまう。

React Hooks を利用した React アプリにおいては、ローカルストレージにアプリのデータを保存する方法が、最も手軽に永続化を行うことが出来る。

この際に、ローカルストレージにデータを保存する独自フックを作成しておけば、汎用性に使えて便利である

> Redux における Redux Persist のようなデータ永続化機能は、React Hooks にはないことに注意

## ■ 方法

1. npm をインストール
	- MacOS の場合
		```sh
		# Node.jsをインストール
		$ brew install node
		```
	> npm : Node.js のパッケージを管理するコマンド

1. React プロジェクトを作成する<br>
  Node.js に組み込まれている `npx` コマンドを用いて、Create React App で React プロジェクトを作成する

	```sh
	$ npx create-react-app ${PROJECT_NAME}
	```
	```sh
	# 強制 yes にする場合
	$ npx -y create-react-app ${PROJECT_NAME}
	```

1. `src/LocalPersist.js` を作成する<br>
  ローカルストレージにデータを保存する独自フックである `useLocalPersist()` を作成する<br>
  ```js
  import { useState } from 'react'

  // ローカルストレージでのデータの永続化を行う独自フック
  function useLocalPersist(key, initValue) {
    const _key = "hooks:" + key

    // ローカルディスクから key の value を取得する関数
    // 初回の書き込みで key がない場合は、初期値 initValue を返す
    const loadValueFromStorage = () => {
      try {
        const item = window.localStorage.getItem(_key)
        return item ? JSON.parse(item) : initValue
      }
      catch (err) {
        console.log(err)
        return initValue;
      }
    }

    // ローカルストレージから読み込んだ initVal
    const [savedValue, setSavedValue] = useState(loadValueFromStorage)

    // key の value を json 形式に変化してローカルストレージに保存する関数
    // この関数を第２戻り値として return し、state の値を更新する関数とする
    const saveValueToStorage = (value) => {
      try {
        setSavedValue(value)
        window.localStorage.setItem(_key, JSON.stringify(value))
      }
      catch (err) {
        console.log(err)
      }
    }

    // ローカルストレージから読み込んだ value と key の value をローカルストレージに保存する関数を return
    return [savedValue, saveValueToStorage]
  }

  export default useLocalPersist
  ```

  ポイントは、以下の通り

  - ローカルディスクから key の value を読み込む処理は、`window.localStorage.getItem()` メソッドで行っている

  - ローカルディスクから key の value を書き込む処理は、`window.localStorage.setItem()` メソッドで行っている

  - ローカルディスクから key の value を取得する関数 `loadValueFromStorage()` を定義し、これを `useState()` の引数に設定することで、ローカルディスクから key の value を初期値とする state `savedValue` を定義している

  - 更に、key の value を json 形式に変化してローカルストレージに保存する関数 `saveValueToStorage()` を定義している。この関数は return されるので、関数の引数 `value` には、この独自フックを使用する側で設定されたローカルストレージへの書き込み値が設定される。この value を `setSavedValue` で xxx

  - return 値には、ローカルストレージから読み込んだ value である `savedValue` と、key の value をローカルストレージに保存する関数である `saveValueToStorage` を設定している。この２つを return することにより、この独自フックの使用側でローカルストレージからの読み込むと書き込みが行えるようになる

  > この独自フックは使えれば良いので、あんま動作の詳細おっかけなくてよい


1. `src/App.js` を修正する<br>
  ```js
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
      // counter 値をローカルストレージに書き込む
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
  ```

  ポイントは、以下の通り

  - `const [savedData, setSavedData] = useLocalPersist("counter", 0)` の形式でローカルストレージにデータを保存する独自フックを宣言している。第１戻り値 `savedData` には、ストレージから読み込んだ値が入るので、これを counter 値をインクリメントする独自フック `useAddCounter` の引数に設定し、カウンター値を初期化している。
    この時、初回の動作としては `useLocalPersist("counter", 0)` の第２引数の値 `initValue=0` が `savedData["counter"]` に入るので、counter 値は 0 で初期化される。
    その後、一度でも save counter ボタンクリックされれば、後述のイベントハンドラ `onClickSaveCounter` 内にて、ローカルストレージへの counter 値の書き込み処理が行われるので、以降はローカルストレージに保存された counter 値で独自フック `useAddCounter` が初期化されるようになる
  
  - save counter ボタンクリック時のイベントハンドラ `onClickSaveCounter` 内にて、`setSavedData` を呼び出さし、counter 値の保存処理を行っている

1. 【オプション】プロジェクトをビルドする
	React を用いたアプリケーションを公開したい場合は、以下のコマンドでプロジェクトをビルドして公開する
	```sh
	$ npm run build
	```

	> ビルドしたプロジェクトは `${PROJECT_NAME}/build` ディレクトリに作成される。この build ディレクトリのファイルを全部アップロードすることで、アプリケーションを公開できる。

1. 作成した React のプロジェクトのサーバーを起動する
	```sh
	$ cd ${PROJECT_NAME}
	$ npm start
	```

	コマンド実行後、作成した React アプリの Web サイト（デフォルトでは http://localhost:3000）が自動的に開く
