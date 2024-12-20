# 【React】React Hooks で副作用フックを使用する


React Hooks における副作用フックとは、関数コンポーネント内のステートの値が更新されたときに、実行される関数のフックである。

副作用フックは、以下の形式で定義する。
```js
import { useEffect } from 'react'

// 関数名 : コンポーネント更新時に実行される関数を指定
useEffect(関数名) 
```

副作用フックを使用すれば、例えば、トップページにアクセスして表示が更新された直後の処理を定義したりすることが出来る。

> イベントハンドラでも同様のことは行える。但し、副作用フックを使用する場合は、イベントハンドラ内では state の更新処理のみを行い、実際の処理は副作用フック内で定義する形式になるので、state の更新処理と実際のイベント処理を切り分けることが出来るメリットがある


# ■ React Hooks で副作用フックを使用する（最もシンプルな構成）

### ◎ 方法

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

		// 入力フォーム更新時のイベントハンドラ
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
  ```

  ポイントは、以下の通り

  - 入力フォーム更新時のイベントハンドラ `onChangeCounter` では、`const [counter, setCounter] = useState(0)` で宣言した state `counter` の更新処理のみ行っており、本来の処理（＝この例では、counter 値のサム値を計算する処理）は行っていない。

	- 本来の処理（この例では、counter 値のサム値を計算する処理）は、`useEffect(()=>{...})` で定義した副作用フック内で行っている。
	
	- 副作用フック内では、処理結果（＝counter 値のサム値を計算する結果）を state `msg` に保存し、この `msg` を関数コンポーネント `Message` のタグ属性 `{msg}` で渡し、関数コンポーネント内で表示を行うようにしている

	- このように、副作用フックを使用すれば、state の更新処理と実際のイベント処理を切り分けることが出来るメリットがある

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


## ■ 副作用フックをスキップする（＝自身の副作用フック再呼び出しによる無限ループを回避する）

副作用フック内で、state の値を更新するために `useState()` の第２戻り値（＝state を更新する関数）を呼び出すと、（state の値が更新するために）再度同じ副作用フックが呼び出され、無限ループになってしまうケースがある。

このような場合は、副作用フックが呼び出されるステートを限定することで回避できる。

副作用フックが呼び出されるステートを限定する場合は、以下の形式で副作用フック定義する。
この時、`[副作用フックが呼び出されるステート１, 副作用フックが呼び出されるステート２, ...]` に指定しなかったステートは、ステートの値が更新されても副作用フックの処理が行われなくなる。

```js
import { useEffect } from 'react'

// 関数名 : コンポーネント更新時に実行される関数を指定
useEffect((event)=>{...}, [副作用フックが呼び出されるステート１, 副作用フックが呼び出されるステート２, ...]) 
```

### ◎ 方法

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

	- OK 例
		```js
		import React, { useState, useEffect } from 'react'
		import './App.css';

		// 関数コンポーネントにおいても、コンポーネントの呼び出し側で <コンポーネント名 args1="" args2="" ... /> で指定されたタグ属性の値は、props 引数で取得出来る
		function Counter(props) {
			return (
				<div>
					<p>total counter : {props.counter}</p>
				</div>
			)
		}

		function App() {
			// ステートフックの宣言
			// 第１戻り値には、state の値が入る。
			// 第２戻り値には、state の値を変更する関数が入る。
			// 引数には、state の初期値を設定
			const [counter, setCounter] = useState(0)
			const [total_counter, setTotalCounter] = useState(0)

			// 入力ボタンクリック時のイベントハンドラ
			// 関数コンポーネント内なので、const 関数名 = () => {} の形式でイベントハンドラを定義する
			const onClickCounter = ()=>{
				setCounter(counter+1)
			}

			// 副作用フックで実際の更新処理を定義。この副作用フックは、state 更新時に自動的に呼び出される
			// useEffect((event)=>{...}, [副作用フックが呼び出されるステート１, 副作用フックが呼び出されるステート２, ...]) の形式で定義することで、副作用フックが呼び出されるステートを限定出来る
			useEffect(() => {
				setTotalCounter(total_counter+1)
			}, [counter])

			// 関数コンポーネントでも（クラスコンポーネントのときと同じように）<コンポーネント名 args1="" args2="" ... /> の形式ででタグ属性を指定出来る
			// useState() メソッドで取得した第１戻り値（＝state の値）を、別の関数コンポーネントのタグ属性に指定にて渡す
			return (
				<div className="App">
					<header className="App-header">
						<h1>React Hook Sample App</h1>
						<Counter counter={total_counter} />
						<button onClick={onClickCounter} className="btn btn-primary">add counter</button>
					</header>
				</div>
			);
		}

		export default App;
		```

	- NG 例
		```js
		import React, { useState, useEffect } from 'react'
		import './App.css';

		// 関数コンポーネントにおいても、コンポーネントの呼び出し側で <コンポーネント名 args1="" args2="" ... /> で指定されたタグ属性の値は、props 引数で取得出来る
		function Counter(props) {
			return (
				<div>
					<p>total counter : {props.counter}</p>
				</div>
			)
		}

		function AppNG() {
			// ステートフックの宣言
			// 第１戻り値には、state の値が入る。
			// 第２戻り値には、state の値を変更する関数が入る。
			// 引数には、state の初期値を設定
			const [counter, setCounter] = useState(0)
			const [total_counter, setTotalCounter] = useState(0)

			// 入力ボタンクリック時のイベントハンドラ
			// 関数コンポーネント内なので、const 関数名 = () => {} の形式でイベントハンドラを定義する
			const onClickCounter = ()=>{
				setCounter(counter+1)
			}

			// 副作用フックで実際の更新処理を定義
			// この副作用フックは、state 更新時に自動的に呼び出される
			useEffect(() => {
				// NG 箇所 : ステート total_counter の値が更新されるので、再度同じ副作用フックが呼び出され、無限に値が加算され続ける
				setTotalCounter(total_counter+1)
			})

			// 関数コンポーネントでも（クラスコンポーネントのときと同じように）<コンポーネント名 args1="" args2="" ... /> の形式ででタグ属性を指定出来る
			// useState() メソッドで取得した第１戻り値（＝state の値）を、別の関数コンポーネントのタグ属性に指定にて渡す
			return (
				<div className="App">
					<header className="App-header">
						<h1>React Hook Sample App</h1>
						<Counter counter={total_counter} />
						<button onClick={onClickCounter} className="btn btn-primary">add counter</button>
					</header>
				</div>
			);
		}

		export default AppNG;
		```

  ポイントは、以下の通り

  - NG 例のコードでは、まずボタンクリック時のイベントハンドラ `onClickCounter()` 内にて、`setCounter()` で state `counter` の値を更新されることにより、副作用フック `useEffect(() => {...})` が呼び出される。次に、副作用フック内の処理にて、`setTotalCounter()` で state `total_counter` の値を更新しているが、この state の値が更新されると、再度同じ副作用フックが呼び出されるために、副作用フックが無限に呼び出され、`total_counter` が無限に増加している挙動になってしまっている。

	- 一方で、OK 例のコードでは、`useEffect((event)=>{...}, [副作用フックが呼び出されるステート１, 副作用フックが呼び出されるステート２, ...])` の形式で、副作用フックが呼び出されるステートを限定している。そのため、まずボタンクリック時のイベントハンドラ `onClickCounter()` 内にて、`setCounter()` で state `counter` の値を更新されることにより、副作用フック `useEffect(() => {...})` が呼び出される動作は同じであるが、次に副作用フック内の処理にて、`setTotalCounter()` で state `total_counter` の値を更新しても、副作用フックが呼び出される state を `counter` に限定しているために、この state `total_counter` の値が更新されても、再度同じ副作用フックが呼び出されことなく、ボタンクリック時に値が加算するだけの正常な挙動になる。

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
