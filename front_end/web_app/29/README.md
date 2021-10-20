# 【React】Redux を使用して値の状態管理を行う

Reduxは、React などが扱う UI の state を管理をするためのフレームワークで、xxx

※ Redux は、React の一部ではなく独立したフレームワークであることに注意

Redux には、主に以下のような要素で構成される。

<img src="https://user-images.githubusercontent.com/25688193/138116456-1f71ea7d-1ec5-4eb2-bdbd-029328ff9220.png" width="500"><br>

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

	プロバイダーによって渡されるストアの state を各コンポーネントでアクセスできようにするためには、`コンポーネント名=connect(stateを設定する関数)(コンポーネント名)` を呼び出せばよい。こうすることで、各クラスコンポーネント内において `this.probs.state内の変数名` で state にアクセスできるようになる。

- レデューサー<br>
	ストアに保管されている state を変更するための仕組み。レデューサーはストアの中に組み込まれている<br>
	レデューサーは、以下の形式で定義する
	```js
	// action : レデューサーを呼び出す際の情報をまとめたオブジェクト
	function レデューサーの関数名 (state=stateの初期値, action){
		// state の更新処理を定義
	}
	```

	レデューサーの呼び出しは、`コンポーネント名=connect(stateを設定する関数)(コンポーネント名)` で state を接続したクラスコンポーネント内にて、`this.props.dispatch({action})` を呼び出すことで行うことができる。

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
	import React from 'react';
	import ReactDOM from 'react-dom';
	import { createStore, combineReducers } from 'redux';   // ストア機能を import
	import { Provider } from 'react-redux';                 // プロバイダー機能を import
	import './index.css';
	import AppComponent from './App';
	import reportWebVitals from './reportWebVitals';

	// ステートの初期値
	let state_value = {
		name: "Yagami",
		id:-1,
	}

	// function レデューサーの関数名 (state=stateの初期値, action){} の形式でレデューサーを定義
	function reducer(state = state_value, action) {
		// action : レデューサーを呼び出す際の情報をまとめたオブジェクト
		// action.type : action オブジェクトに必ず用意されているプロパティで、レデューサーを呼び出す際の呼び出しの種類を表している。これらの値は、App.js 内の `this.props.dispath({type:"xxx"})` で定義している
		switch (action.type) {
			case 'INCREMENT_ID': // 
				// state の新しい値を return する
				return {
						name:state.name,
						id:state.id + 1,
				};
			case 'DECREMENT_ID':
				return {
					name:state.name,
					id:state.id - 1,
				};
			default:
				return state;
		}
	}

	// `ストア変数名 = createStore(レデューサー関数名)` の形式でストアを作成
	let store = createStore(reducer);

	// 表示をレンダリング
	ReactDOM.render(
		// プロバイダーは、`<Provider store={ストアの変数名}>xxx</Provider>` タグとその store 属性で定義し、このタグ内の xxx の箇所で定義されているコンポーネントにストアの内容が渡される。
		// この例では、App.js で定義されている App コンポーネントにストアの内容が渡される
		<Provider store={store}>
			<AppComponent />
		</Provider>,
		document.getElementById('root')
	);
	```

	ポイントは、以下の通り

	- `function レデューサーの関数名 (state=stateの初期値, action){...}` の形式でレデューサーを定義している。
		ここで、`action` 引数には、レデューサーを呼び出す際の情報をまとめたオブジェクトが設定される。この内、`action.type` は `action` オブジェクトに必ず用意されているプロパティで、レデューサーを呼び出す際の呼び出しの種類を表している。
		そして、レデューサーは、後述の `App.js` 内で定義した（ストアの state を接続した）クラスコンポーネント内にて、`this.props.dispatch({action})` を呼び出したときに呼び出される

	- `let ストア変数名 = createStore(レデューサー関数名)` の形式でストアを作成する

	- プロバイダーは、`<Provider store={ストアの変数名}>xxx</Provider>` タグとその store 属性で定義し、このタグ内の xxx の箇所で定義されているコンポーネントにストアの内容が渡される。この例では、`App.js` で定義されている `AppComponent` コンポーネントにストアの内容が渡される。但し、ストアの state をコンポーネントで利用可能にするためには、`connect(stateを設定する関数)(コンポーネント)` でストアの state を接続する処理も必要なことに注意。この処理は、後述の `App.js` で行っている

1. `src/App.js` を修正する
	```js
	import React, { Component } from 'react';
	import { connect } from 'react-redux';
	import './App.css';

	// コンポーネントで使用する state を返すメソッド
	function mappingState(state) {
		return state;
	}

	// App コンポーネント
	class AppComponent extends Component {
		constructor(props){
			super(props);
		}

		render() {
			// <StateComponent /> に部分を <StateComponent id="-1" /> のように属性を指定した呼び出し方をしなくとも、StateComponent コンポーネントで this.props.id でアクセスできる
			return (
				<div>
					<p>Hello React Component!</p>
					<StateComponent />
					<ButtonComponent />
				</div>
			);
		}
	}

	// connect(stateを設定する関数)(コンポーネント) : コンポーネントにストアを接続する
	// let warpWithConnect = connect()  // warpWithConnect は関数オブジェクト
	// AppComponent = warpWithConnect(warpWithConnect)
	AppComponent = connect()(AppComponent);

	// ID 表示のコンポーネント
	class StateComponent extends Component {
		render(){
			// このクラスコンポーネントでは、<StateComponent name="Yagami" id="1" /> のように属性を指定して呼び出さられなくても、this.props に index.js のレデューサーで定義した state が設定されている
			return (
				<p>
					name={this.props.name}, id={this.props.id}
				</p>
			);
		}
	}

	// StateComponent コンポーネントにストアを接続する
	// 第１引数に state の内容をそのまま返す mappingState() メソッドを設定することで、StateComponent コンポーネント内の this.props に index.js 内のレデューサーで定義した state が設定される
	StateComponent = connect(mappingState)(StateComponent);

	// ボタンのコンポーネント
	class ButtonComponent extends Component {
		constructor(props){
			super(props);
			// this.メソッド名 = this.メソッド名.bind(this); の形式でイベントをバインド（割り当て）する
			this.doAction = this.doAction.bind(this);
		}

		// ボタンクリックでディスパッチ（レデューサーの呼び出し値を操作するためのもの）を実行
		doAction(e){
			if (e.shiftKey){
				// this.props.dispatch({action}) でレデューサーを呼び出す。このときレデューサーメソッドの action 引数にここで設定した値が設定される
				// type は必ず設定する必要がある
				this.props.dispatch({ type:'DECREMENT_ID' });
			} else {
				this.props.dispatch({ type:'INCREMENT_ID' });
			}
		}

		render(){
			// <button> タグの onClick 属性に、このクラスコンポーネントで定義したイベント処理のメソッドを設定し、onClick 属性に紐付ける
			return (
				<button onClick={this.doAction}>
					click
				</button>
			);
		}
	}
	// ストアのコネクト
	ButtonComponent = connect()(ButtonComponent);

	// AppComponent を外部ファイルから利用できるようにする
	export default AppComponent;

	```

	ポイントは、以下の通り

	- `connect(stateを設定する関数)(コンポーネント)` で、各クラスコンポーネントに対して、ストアの state を接続している。
		特に `StateComponent` コンポーネントに対しては、第１引数に state の内容をそのまま返す `mappingState()` メソッドを設定することで、StateComponent コンポーネント内の `this.props.state内の変数名` で `index.js` 内のレデューサー `reducer` で定義した state にアクセス出来るようにしている。このとき、`StateComponent` コンポーネントを呼び出す際に、`<StateComponent name="Yagami" id="1" />` のように属性を指定して呼び出さられなくても、`<StateComponent />` で呼び出しただけで `this.props.name`, `this.props.id` でアクセスできるようになっている点に注目

	- `ButtonComponent` コンポーネントも `connect(stateを設定する関数)(コンポーネント)` で、各クラスコンポーネントに対して、ストアの state を接続している。このコンポーネント内では、`this.props.dispatch({action})` を呼び出し、`index.js` 内で定義したレデューサー `reducer` を呼び出している。
		このときレデューサーメソッドの action 引数にここで設定した値が設定される。特に、`type` は必ず設定する必要がある

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
