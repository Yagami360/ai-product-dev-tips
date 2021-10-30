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
      $ npm install --save firebase
      ```

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

    - その他の部分は、Redux のストア・レデューサー・プロバイダーなどを使わないシンプルな構成になっている

1. `src/App.js` を修正する<br>
    ```js
    ```

    ポイントは、以下の通り

    - xxx

1. `src/FirebaseDatabase.js` を作成する<br>
    Firebase の Realtime Database からデータを取り出し、それらを表示する `FirebaseDatabase` コンポーネントを作成する

    ```js
    ```

    ポイントは、以下の通り

    - xxx

1. 【オプション】プロジェクトをビルドする<br>
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
