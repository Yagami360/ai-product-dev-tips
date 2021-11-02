# 【React】React Hooks を使用して値の状態管理を行う

> Redux との比較の説明分追加


- ステートフック<br>
  React における state（値を更新すると即座に画面に反映される変数）に対してのフック。<br>
  ステートフックは、以下の形式で定義する。
  ```js
  import { useState } from 'react'

  // 変数 A : state の値
  // 変数 B : state の値を変更する関数
  const [変数A, 変数B] = useState(初期値) 
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

1. `src/App.js` を修正する
	```js
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
  ```

  ポイントは、以下の通り

  - Hook を使用する場合は、各コンポーネントをクラスコンポーネントではなく、関数コンポーネントで定義する必要がある

  - `useState()` メソッドで、ステートフックを宣言する。このとき、第１戻り値 `countA` には、state の値が入る。第２戻り値 `setCountA` には、state の値を変更する関数が入る。引数には、state（今の場合 count）の初期値を設定する

  - `useState()` メソッドで取得した第１戻り値（＝state の値）`countA` は、`App` コンポーネントの return 分（JSX形式）の中で `{countA}` とすることで、表示させることが出来る

  - `useState()` メソッドで取得した第２戻り値（=state の値を変更する関数）`setCountA` は、ボタンクリック時のイベントハンドラ `clickFuncA` 内で呼び出している。このとき `setCountA` の引数には、state の更新式を設定する

  - 尚、このイベントハンドラ `clickFuncA` は、`App` コンポーネントがクラスコンポーネントではなく関数コンポーネントなので、`const 関数名 = () => {}` の形式で定義している

  - `useState()` メソッドを複数個使用すれば、複数のステートを作成することが出来る。この例では、`countA` と `countB` が該当する

  - クラスコンポーネントでは、画面表示される値のみを state として定義するようしていた。**一方で、関数コンポーネントでは内部で宣言した変数の値が保持されない（＝関数スコープを抜けるとメモリが開放される）ので、関数コンポーネントを使用する Hook での状態管理では、例え画面表示に関連しない変数であっても、内部で値を保持したい変数に関しては、全て state で定義する必要があることに注意。**

  - Redux を使用した状態管理に比べて、非常にシンプルな構成になっていることに注目。

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
