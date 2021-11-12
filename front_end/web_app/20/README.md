# 【React】Creat React App を用いて React アプリをデプロイする

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

	> JavaScript ではなく TypeScript での React アプリを作成する場合は、`--template typescript ` を追加すればよい
	> ```sh
	> # 強制 yes にする場合
	> $ npx -y create-react-app ${PROJECT_NAME} --template typescript 
	> ```	

	上記コマンドでプロジェクトを作成すると、以下のようなディレクトリ構造で各種ファイルが出力される。

	```sh
	+ ${PROJECT_NAME} + /public         			# HTML や CSS などの公開ファイル
	|                 +-- index.html    			# 表示される Web サイト。
	|                 + /src            			# React が作成した各種ソースファイル
	|                 +-- index.js    				# 起点となる JavaScript。index.html から呼び出される
	|                 +-- App.js    					# 画面表示を行うクラスのコンポーネント。index.js から呼び出される
	|                 + /node_modules         # npm のモジュール群  
	|                 + package.json          # npm でのパッケージ管理情報
	```
	
	> JavaScript ではなく TypeScript での React アプリを作成した場合は、`*.js` の部分が `*.tsx` に置き換わる

	- `index.html`<br>
		```html
		<!DOCTYPE html>
		<html lang="en">
			<head>
				<meta charset="utf-8" />
				<link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
				<meta name="viewport" content="width=device-width, initial-scale=1" />
				<meta name="theme-color" content="#000000" />
				<meta
					name="description"
					content="Web site created using create-react-app"
				/>
				<link rel="apple-touch-icon" href="%PUBLIC_URL%/logo192.png" />
				<link rel="manifest" href="%PUBLIC_URL%/manifest.json" />
				<title>React App</title>
			</head>
			<body>
				<noscript>You need to enable JavaScript to run this app.</noscript>
				<div id="root"></div>
			</body>
		</html>
		```

		ポイントは、以下の通り

		- `<div id="root"></div>` の部分に React を使ってタグを埋め込むようになっている

	- `index.js`
		```js
		import React from 'react';
		import ReactDOM from 'react-dom';
		import './index.css';
		import App from './App';													// App.js で定義したコンポーネントを import
		import reportWebVitals from './reportWebVitals';

		ReactDOM.render(
			<React.StrictMode>
				<App />
			</React.StrictMode>,
			document.getElementById('root')
		);

		reportWebVitals();
		```

		ポイントは、以下の通り

		- `ReactDOM.render(エレメント, DOM)` で、React-DOM ライブラリの `ReactDOM` オブジェクトを用いて、仮想DOMにレンダリングしている。

		- `<App />` で `App.js` で定義したコンポーネントを呼び出し、`ReactDOM.render(エレメント, DOM)` の第１引数に設定している

		- `document.getElementById('root')` で、DOM におけるタグ `<div id="root"></div>` のエレメントを取得し（※ このメソッドは、React のメソッドではなく JavaScript のメソッド）、`ReactDOM.render(エレメント, DOM)` の第２引数に設定している

	- `App.js`
		```js
		import logo from './logo.svg';
		import './App.css';

		function App() {
			return (
				<div className="App">
					<header className="App-header">
						<img src={logo} className="App-logo" alt="logo" />
						<p>
							Edit <code>src/App.js</code> and save to reload.
						</p>
						<a
							className="App-link"
							href="https://reactjs.org"
							target="_blank"
							rel="noopener noreferrer"
						>
							Learn React
						</a>
					</header>
				</div>
			);
		}

		export default App;
		```
		
		ポイントは、以下の通り

		- `function App(){...}` で関数コンポーネントを定義し、JSX 形式で return している。この return 分の内容に `index.html` の `<div id="root"></div>` 部分が置き換わる動作になる

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

<!--
1. デプロイしたアプリの Web サイトにアクセスする
	```sh
	$ open http://localhost:3000
	```
-->
