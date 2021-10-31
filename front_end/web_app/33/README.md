# 【React】React アプリで Firebase の Realtime Database を利用する

> Redux ではなく、Firebase の Realtime Database を利用する意義を追記

## ■ 方法

1. npm をインストール
    - MacOS の場合
        ```sh
        # Node.jsをインストール
        $ brew install node
        ```
    > npm : Node.js のパッケージを管理するコマンド

1. React のプロジェクトの作成<br>
	1. React のプロジェクトを作成する
		Node.js に組み込まれている `npx` コマンドを用いて、Create React App で React プロジェクトを作成する

		```sh
		$ npx create-react-app ${PROJECT_NAME}
		```
		```sh
		# 強制 yes にする場合
		$ npx -y create-react-app ${PROJECT_NAME}
		```
1. firebase API をインストールする<br>
		```sh
		$ cd ${PROJECT_NAME}
		$ npm install --save firebase@8.10.0
		```

	> バージョン指定なしの `npm install --save firebase` でインストールすると、現時点（21/10/31）では version 9.x の Firebase がインストールされるが、version8 -> version9 へ変更した場合は、firebase の import 方法が、`import firebase from 'firebase/app';` -> `import { initializeApp } from 'firebase/app';` に変更されたりしており、version8 の Firebase コードが動かなくなることに注意

1. Firebase プロジェクトの作成<br>
  1. [Firebase コンソール画面](https://console.firebase.google.com/?hl=ja&pli=1)にアクセス
  1. 「プロジェクトを作成」
  1. 「設定」ボタン→「全般」タブから、GCP リソースのリージョンを指定する<br>
      <img src="https://user-images.githubusercontent.com/25688193/107106996-d4759180-6871-11eb-909c-14915bde83c6.png" width="500"><br>

1. <a id="ウェブアプリをFirebaseに登録する"></a>ウェブアプリを Firebase に登録する<br>
  1. Firebase コンソールの「プロジェクトの概要」ページの中央にあるウェブアイコン `</>` をクリックし、設定ワークフローを起動する。<br>
      <img src="https://user-images.githubusercontent.com/25688193/107107327-bd37a380-6873-11eb-972d-4957992a748c.png" width="300"><br>
  1. 設定ワークフロー画面でアプリ名を入力後、「アプリを登録」ボタンをクリックする。このとき、以下の画面のコードをコピーしておく。<br>
      <img src="https://user-images.githubusercontent.com/25688193/138590270-3304ca03-787d-43d2-8c81-e6f65e754b6e.png" width="300"><br>

      ```js
      // Import the functions you need from the SDKs you need
      import { initializeApp } from "firebase/app";
      import { getAnalytics } from "firebase/analytics";
      // TODO: Add SDKs for Firebase products that you want to use
      // https://firebase.google.com/docs/web/setup#available-libraries

      // Your web app's Firebase configuration
      // For Firebase JS SDK v7.20.0 and later, measurementId is optional
      const firebaseConfig = {
        apiKey: " APIキー ",
        authDomain: "プロジェクト.firebaseapp.com",
        databaseURL: "https://プロジェクト.firebaseio.com",
        projectId: "プロジェクト",
        storageBucket: "プロジェクト.appspot.com",
        messagingSenderId: " ID番号 "
        appId: "appid",
        measurementId: "measurementId"
      };

      // Initialize Firebase
      const app = initializeApp(firebaseConfig);
      const analytics = getAnalytics(app);
      ```

1. Realtime Database を作成する。<br>
    1. [Firebase コンソール画面](https://console.firebase.google.com/?hl=ja&pli=1) の左側画面の「Realtime Database」→「データベースを作成」ボタンをクリックする<br>
        <img src="https://user-images.githubusercontent.com/25688193/138589481-c58b7c02-6d98-4f23-a5e6-8e6686835022.png" width="500"><br>
    1. セキュリティモードの選択画面で、「テストモードで開始」を選択する。<br>
        <img src="https://user-images.githubusercontent.com/25688193/138589630-24c5d0cf-af64-451c-aa0a-87f27ccd5c0f.png" width="400"><br>
        - 「ロックモードで開始」：特定のアプリケーションでのみ利用可能<br>
        - 「テストモードで開始」：公開モードでどこからでも自由にアクセスできる<br>
    1. 「+」ボタンをクリックして、以下のようなデータベースを作成する<br>
        <img src="https://user-images.githubusercontent.com/25688193/138589827-d01ecdd2-bdec-46b9-b14a-15ccf68b5a2a.png" width="400"><br>

<!--
1. Authentication を作成する。<br>
    作成した Realtime Database に対して、React アプリからアクセスできるようにするための Authentication
 を作成する<br>
    1. [Firebase コンソール画面](https://console.firebase.google.com/?hl=ja&pli=1) の左側画面の「Authentication」→「始める」ボタンをクリックする<br>
        <img src="https://user-images.githubusercontent.com/25688193/138589902-c3213972-abd6-45fa-86cd-3e217a7eefdb.png" width="500"><br>
    1. xxx
-->

1. Firebase プロジェクトの初期化<br>
  1. Firebase CLI をインストールする<br>
      ```sh
      $ cd ${PROJECT_NAME}
      $ sudo npm install -g firebase-tools
      ```
  1. Firebase プロジェクトにログインする<br>
      ```sh
      $ firebase login --project ${PROJECT_ID}
      ```
      - `${PROJECT_ID}` : Firebase プロジェクトのプロジェクトID。作成した Firebase プロジェクトのコンソール画面の「プロジェクトの設定」から確認可能

  1. Firebase プロジェクトを初期化する<br>
      ```sh
      $ firebase init --project ${PROJECT_ID}
      ```
      <img src="https://user-images.githubusercontent.com/25688193/138589325-28e234a6-2c99-4bff-8bc4-34ec47ec5545.png" width="500"><br>

      > "Realtime Database: Configure a security rules file for Realtime Database and (optionally) provision default instance" を選択しスペースキーを押して、Realtime Database の機能を有効化する。


1. `src/index.js` を修正する<br>
	```js
	import React from 'react';
	import ReactDOM from 'react-dom';
	import firebase from "firebase";
	import './index.css';
	import App from './App';

	// Firebaseの初期化
	var firebaseConfig = {
		apiKey: "AIzaSyBSKhjSkI0pERNnYhcrl3Uldl47ZyGvNqE",
		authDomain: "react-firebase-app-2cc53.firebaseapp.com",
		databaseURL: "https://react-firebase-app-2cc53-default-rtdb.firebaseio.com",
		projectId: "react-firebase-app-2cc53",
		storageBucket: "react-firebase-app-2cc53.appspot.com",
		messagingSenderId: "686383733508",
		appId: "1:686383733508:web:a1d5c2ec271201d87b4e51",
		measurementId: "G-MCWN891SRK"   
	};
	firebase.initializeApp(firebaseConfig);

	// 表示をレンダリング
	ReactDOM.render(
		<App />,
		document.getElementById('root')
	);
	```

	ポイントは、以下の通り

	- `firebase.initializeApp()` で firebase の初期化を行っている。このときの config 引数には、先の「[ウェブアプリをFirebaseに登録する](#ウェブアプリをFirebaseに登録する)」の処理時にコピーしていた値を設定すればよい。そして 一旦 firebase の初期化処理を行えば、どのコンポーネントからも firebase を利用することが出来るようになる。

			> このコンフィ値には、API キーの情報が含まれており、GitHub に公開することでセキュリティ上のリスクがあるように思えるが、公開前提の値であり隠すようなものではないらしい。<br>
			> 詳細は、https://qiita.com/hoshymo/items/e9c14ed157200b36eaa5 などを参照のこと


	- Firebase API を version8 -> version9 に変更した場合は、Firebase の処理化部分のコードは以下のようなコードになることに注意<br>
		```js
		import { initializeApp } from 'firebase/app';     // for version 9.x

		// Firebaseの初期化
		var firebaseConfig = {
				apiKey: "AIzaSyBSKhjSkI0pERNnYhcrl3Uldl47ZyGvNqE",
				authDomain: "react-firebase-app-2cc53.firebaseapp.com",
				databaseURL: "https://react-firebase-app-2cc53-default-rtdb.firebaseio.com",
				projectId: "react-firebase-app-2cc53",
				storageBucket: "react-firebase-app-2cc53.appspot.com",
				messagingSenderId: "686383733508",
				appId: "1:686383733508:web:a1d5c2ec271201d87b4e51",
				measurementId: "G-MCWN891SRK"   
		};
		initializeApp(firebaseConfig);                    // for version 9.x
		```

	- その他の部分は、Redux のストア・レデューサー・プロバイダーなどを使わないシンプルな構成になっている

1. `src/App.js` を修正する<br>
	`App.js` の `App` コンポーネントは、アプリ全部画面のコンポーネントであり、アプリ全部表示を行う。

	```js
	import React, { Component } from 'react';
	import './App.css';
	import FirebaseDatabase from './FirebaseDatabase';

	// App コンポーネント
	class App extends Component {
		constructor(props){
			super(props);
		}

		render() {
			return (
				<div>
					<p>Hello React Firebase App!</p>
					<FirebaseDatabase db_name="sample-database" />
				</div>
			);
		}
	}

	export default App;
	```

	ポイントは、以下の通り

	- `render()` 内で、後述で作成する `FirebaseDatabase` コンポーネント（Firebase の Realtime Database からデータを取り出しそれらを画面表示するコンポーネント）を呼び出すことで、アプリ全部画面の表示を行っている

	- `export default` で App コンポーネントを外部公開している


1. `src/FirebaseDatabase.js` を作成する<br>
	Firebase の Realtime Database からデータを取り出し、それらを画面表示する `FirebaseDatabase` コンポーネントを作成する

	```js
	import React, { Component } from 'react';
	import firebase from "firebase";
	import "firebase/storage";


	// Firebase の Realtime Database からデータを取り出し、それらを表示するコンポーネント
	class FirebaseDatabase extends Component {
		style = {
			fontSize:"12pt",
			padding:"5px 10px"
		}

		constructor(props) {
			super(props);

			// `state` の値の初期化は、コンストラクタで `this.state = {変数名1:値1, 変数名2:値2, ...};` の形式で行う
			this.state = {
				data_list:[]   // Firebase の Realtime Database からデータベースをリストで設定
			}

			this.getDatabaseFromFirebase();
		}

		// Firebase の Realtime Database からデータベースを取得する関数
		getDatabaseFromFirebase(){
			// database にアクセスするためのオブジェクト作成
			let db = firebase.database();

			// ref() メソッドで、取り出すデータの reference オブジェクト作成。
			// 引数には Firebase Realtime Database 上のデータベースのパスを指定（プロジェクト直下の場合は、`${データベース名}/` になる）
			let ref = db.ref(this.props.db_name + "/");

			// ?
			let self = this;

			// orderByKey() : キーをデータを並び替え
			// limitToFirst() : 引数で指定した数だけデータを取り出す
			// on(イベント名, (snapshot)=>{終了後の処理} ) : 
			//   limitToFirst() でアクセスした結果の処理イベントのイベントハンドラで、アクセス後の処理を定義する。ここでは、イベント名に "value"（データベースにアクセスし値を受け取るイベント）を設定している。
			//   snapshot には、イベント時発生時に受け取ったデータが {"id":1, name:"Yagami"} のような形式で入る
			//   limitToFirst().on(){} とすることで、limitToFirst() の引数で指定した数だけ繰り返し処理が行われるので、data_list に [{"id":1, name:"Yagami"}, {"id":2, name: "Yagoo"}, ...] のようなリストデータが入る
			ref.orderByKey().limitToFirst(10).on('value', (snapshot)=>{
				// state の更新は、setState() で行う
				self.setState({
					data_list:snapshot.val()
				});
			});
		}

		// データベースの各項目を表形式でレンダリングする関数
		renderTableColums(){
			console.log("this.state.data_list :", this.state.data_list)
			if (this.state.data_list == null || this.state.data_list.length == 0){
				return [<tr key="0"><th>NO DATA.</th></tr>];
			}

			let result = [];
			for(let i in this.state.data_list){
				// <tr> タグ（テーブルの行）・<th> タグ（テーブルの見出し）・<td> タグ（テーブルのセル）
				// タグ内の key属性 : React が画面表示を更新する際に更新対象を識別するための一意の値（※ この key 属性は、HTML　でもともと定義されているタグ属性ではなく、React の仮想DOM の機能であることに注意）
				result.push(
					<tr key={i}>
						<th>{this.state.data_list[i].id}</th>
						<td>{this.state.data_list[i].name}</td>
					</tr>
				);
			}
			return result;
		}

		render(){
			if (this.state.data_list.length == 0){
				this.getDatabaseFromFirebase();
			}
			return (
				<div>
					<p>Realtime Database name: {this.props.db_name}</p>
					<table><tbody>
						<tr>
							<th>id</th>
							<th>name</th>
						</tr>
						{this.renderTableColums()}
					</tbody></table>
				</div>
			)
		}
	}

	// 外部公開する
	export default FirebaseDatabase;
	```

	ポイントは、以下の通り

	- 今回の例では、`getDatabaseFromFirebase()` メソッド内で Firebase の Realtime Database からデータベースを取得する処理を行っているが、その大まかな流れは、以下のようになる
		1. `let db = firebase.database();` で Firebase の Realtime Database にアクセスするためのオブジェクト作成する。
		1. `let ref = db.ref(this.db_name + "/");` でデータベースから取り出すデータの reference オブジェクト作成する。この時、引数には Firebase Realtime Database 上のデータベースのパスを指定する（プロジェクト直下の場合は、`${データベース名}/` になる）
		1. reference オブジェクトを用いて、`ref.orderByKey().limitToFirst(10).on('value', (snapshot)=>{...}` の部分でデータベースからデータを取り出している。

			- `orderByKey()`<br>
				キーをデータを並び替え
			- `limitToFirst()`<br>
				引数で指定した数だけデータを取り出す
			- `on(イベント名, (snapshot)=>{終了後の処理} )`<br>
				`limitToFirst()` でアクセスした結果の処理イベントのイベントハンドラで、アクセス後の処理を定義する。ここでは、イベント名に `"value"`（データベースにアクセスし値を受け取るイベント）を設定している。<br>
				アロー関数の引数 `snapshot.val()` には、イベント時発生時に受け取ったデータが `[{"id":1, name:"Yagami"}, {"id":2, name: "Yagoo"}, ...]` のような形式で入る。そのため、この値を state の `this.state.data_list` に `setState()` で代入し、後の `render()` メソッド内でこのに基づきレンダリングすることで、データベースの内容を画面表示することが出来る<br>

	- `render()` 内で、`getDatabaseFromFirebase()` メソッド内で取得し、`this.state.data_list` に設定したデータベースの内容を表形式でレンダリングしている。

		> - HTML タグ内の key 属性について<br>
		> `render()` 内の `<tr key={i}>` の部分指定している key 属性は、HTMLでもともと定義されているタグ属性ではなく、React の機能であり、React が仮想DOM を更新する際に更新対象を識別するための一意の値になっている。<br>
		> key を設定しない場合は、データベースの内容が変わらなくても表示させる順が変化するするだけで、仮想DOMを再構成する必要がありパフォーマンスが低下する。一方、key を設定しない場合は、データベースの順番が変化しても、中身の値が変わらなければ、仮想DOMを再構成する必要がないのでパフォーマンスが向上するメリットがある。<br>
		> 詳細は、以下のサイトを参考のこと
		>    - https://watablogtravel.com/react-key-props/


1. 【オプション】プロジェクトをビルドする<br>
	React を用いたアプリケーションを公開したい場合は、以下のコマンドでプロジェクトをビルドして公開する
	```sh
	$ npm run build
	```

	> ビルドしたプロジェクトは `${PROJECT_NAME}/build` ディレクトリに作成される。この build ディレクトリのファイルを全部アップロードすることで、アプリケーションを公開できる。

1. 作成した React のプロジェクトのサーバーを起動する<br>
	```sh
	$ cd ${PROJECT_NAME}
	$ npm start
	```

	コマンド実行後、作成した React アプリの Web サイト（デフォルトでは http://localhost:3000）が自動的に開く

	<img src="https://user-images.githubusercontent.com/25688193/139570333-9704f263-213e-49a3-9400-1d333c534946.png" width="500"><br>

	