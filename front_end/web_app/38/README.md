# 【React】React Hooks で独自フックを使用する

以下の形式で関数を定義することで、独自のフックを定義することが出来る。関数名の先頭には use を付与する必要があることに注意

```js
import React, { useState } from 'react'

function useフック名 () {
  const [ステート名, ステートを更新する関数名] = useState(ステートの初期値)
  const 独自フックの処理を行う関数名 = () => {...}
  return [ステート名, 独自フックの処理を行う関数名]
}
```

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

1. `src/App.js` を修正する<br>
  ```js
  import React, { useState } from 'react'
  import './App.css';

  // 以下の形式で独自フックを定義
  // function useフック名 () {
  //   const [ステート名, ステートを更新する関数名] = useState(ステートの初期値)
  //   const 独自フックの処理を行う関数名 = () => {...}
  //   return [ステート名, 独自フックの処理を行う関数名]
  // }
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
    const [counter, addCounter] = useAddCounter(0)

    // 入力ボタンクリック時のイベントハンドラ
    // 関数コンポーネント内なので、const 関数名 = () => {} の形式でイベントハンドラを定義する
    const onClickCounter = ()=>{
      addCounter()
    }

    // 関数コンポーネントでも（クラスコンポーネントのときと同じように）<コンポーネント名 args1="" args2="" ... /> の形式ででタグ属性を指定出来る
    // useState() メソッドで取得した第１戻り値（＝state の値）を、別の関数コンポーネントのタグ属性に指定にて渡す
    return (
      <div className="App">
        <header className="App-header">
          <h1>React Hook Sample App</h1>
          <Counter counter={counter} />
          <button onClick={onClickCounter} className="btn btn-primary">add counter</button>
        </header>
      </div>
    );
  }

  export default App;
  ```

  ポイントは、以下の通り

  - `function useフック名 () {...}` の形式で、独自のフック `useAddCounter`（counter値をインクリメントするフック）を定義している。

  - 独自フック `useAddCounter()` 内では、まず `useState()` を使用して、state `counter` とこの state を更新する関数 `setCounter` を定義している。その後、この独自フックで行う処理（＝counter値をインクリメント）を定義した関数 `addCounter` を定義している。最後に、state `counter` と独自フックで行う処理（＝counter値をインクリメント）を定義した関数 `addCounter` を return している。

  - 独自フックを使用する側では、まず、通常のステートフックと同じように、`const [counter, addCounter] = useAddCounter(0)` の形式で独自フックを宣言し、ボタンクリック時のイベントハンドラ `onClickCounter` 内にて、独自フックのステートを更新する関数 `addCounter` をそのまま呼び出している。`addCounter` を呼び出すと、内部でステート `counter` の値がインクリメントされるので、`{counter}` で渡した値も更新され、画面上に反映される


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
