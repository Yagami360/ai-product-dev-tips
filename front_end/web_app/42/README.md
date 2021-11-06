# 【React】Node.js + React Hooks アプリで Firebase の Realtime Database を利用する

## ■ 方法

1. npm をインストール
    - MacOS の場合
        ```sh
        # Node.jsをインストール
        $ brew install node
        ```
    > npm : Node.js のパッケージを管理するコマンド

1. Next.js プロジェクトのディレクトリを作成する<br>
    ```sh
    $ mkdir -p ${PROJECT_NAME}
    ```

1. `package.json` を作成する<br>
  Next.js プロジェクトのディレクトリ以下に、以下のような `package.json` を作成する

    ```json
    {
      "scripts": {
        "dev": "next",
        "build": "next build",
        "start": "next start",
        "export": "next export"
      }
    }
    ```

1. next.js, react, react-dom をインストールする
    ```sh
    $ cd ${PROJECT_NAME}
    $ npm install --save next
    $ npm install --save react
    $ npm install --save react-dom
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


1. `pages/index.js` を作成する
    ```js
    ```

1. 【オプション】プロジェクトをビルドする<br>
	1. Next.js の設定ファイル `next.config.js` を作成する<br>
			アプリの公開時に、外部公開される静的な HTML ファイルを生成するために、 Next.js の設定ファイル `next.config.js` を作成する
			```js
			module.exports = {
				exportPathMap: function () {
					return {
						'/': { page: '/' }
					}
				}
			}
			```

	1. プロジェクトをビルドする
		```sh
		$ npm run build
		```

	1. プロジェクトをエクスポートする
			```sh
			$ npm run export
			```

			> ビルドしてエクスポートされたプロジェクトは `${PROJECT_NAME}/out` ディレクトリに作成される。この out ディレクトリのファイルを全部アップロードすることで、アプリケーションを公開できる。

	1. 【オプション】出力された静的な Web ファイル　`out/index.html` を確認する

		> 出力された静的な Web ファイル　`index.html` では、`index.js` の JSX の内容で書き換わっていることに注目。
		
		> サーバーから送られる静的な Web ファイル　`index.html` に表示内容が生成されてウェブブラウザに送られた後に、ウェブブラウザで表示内容をレンダリングする形式になっているので、サーバーサイドレンダリングできるようになっている

1. 作成した React のプロジェクトのサーバーを起動する
    ```sh
    $ cd ${PROJECT_NAME}
    $ npm run dev
    ```

    コマンド実行後、作成した React アプリの Web サイト（デフォルトでは http://localhost:3000）が自動的に開く
