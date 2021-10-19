# 【React】Redux を使用して値の状態管理を行う

Reduxは、React などが扱う UI の state を管理をするためのフレームワークで、xxx

※ Redux は、React の一部ではなく独立したフレームワークであることに注意

Redux には、主に以下のような要素で構成される。

<img src="https://user-images.githubusercontent.com/25688193/137906159-c1039d1e-d622-4cd8-8545-693d7e36b275.png" width="500"><br>

- ストア<br>
	Redux が扱うすべてのデータは、ストアに保管される。このストアに保管される値は state と呼ばれる（React における state と同じもの）。<br>
	ストアに保管されている値である state は、読み取り専用で書き換え不可になっている。state の変更は、後述のレデューサーで行う。<br>
	ストアの作成は、以下のように Redux　モジュールの `変数 = createStore(レデューサー)` の形式で行う。
	```js
	import { createStore } from 'redux';
	let ストアの変数名 = createStore(レデューサーの関数名)
	```

- プロバイダー<br>
	ストアを他のコンポーネントに渡すための仕組み。<br>
	プロバイダーは、`ReactDOM.render(element,dom)` の第１引数などで、`<Provider store={ストアの変数名}>xxx</Provider>` タグとその store 属性で定義し、このタグ内の xxx の箇所で定義されているコンポーネントにストアの内容が渡される。例えば、``<Provider store={ストアの変数名}><App /></Provider>`` の場合は、コンポーネント `<App />` にストア `{ストアの変数名}` の内容が渡される。

- レデューサー<br>
	ストアに保管されている state を変更するための仕組み。レデューサーはストアの中に組み込まれている<br>
	レデューサーの作成は、以下の形式で行う
	```js
	// action : レデューサーを呼び出す際の情報をまとめたオブジェクト
	function レデューサーの関数名 (state=stateの初期値, action){
		// 処理を定義
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

1. Redux, React Redux, React DevTools をインストールする<br>
	```sh
	$ cd ${PROJECT_NAME}
	$ npm install --save redux
	$ npm install --save react-redux
	$ npm install --save-dev redux-devtools
	```

1. `src/index.js` を修正する
	```js
	```

1. `src/App.js` を修正する
	```js
	```

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
