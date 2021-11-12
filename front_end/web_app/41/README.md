# 【React】Next.js と React Hooks と Firebase を使用して簡単なウェブアプリを作成する

ここでは、Next.js と React Hooks と Firebase を使用して簡単なウェブアプリの例として、送信機能付きアドレス帳アプリを作成する


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
    $ npm install react-bootstrap bootstrap
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

1. Firestore Database を有効化する。<br>
    1. [Firebase コンソール画面](https://console.firebase.google.com/?hl=ja&pli=1) の左側画面の「Firestore Database」→「データベースの作成」ボタンをクリックする<br>
        <img src="https://user-images.githubusercontent.com/25688193/140601915-46e91203-5664-4d14-9751-8c815dcf66da.png" width="500"><br>
    1. セキュリティモードの選択画面で、「テストモードで開始」を選択し、「次へ」をクリックする<br>
        <img src="https://user-images.githubusercontent.com/25688193/140601923-c575d907-a8db-4aab-8f99-66f0da393901.png" width="400"><br>
        - 「ロックモードで開始」：特定のアプリケーションでのみ利用可能<br>
        - 「テストモードで開始」：公開モードでどこからでも自由にアクセスできる<br>
    1. セキュリティモードの選択画面で、「テストモードで開始」を選択し、「次へ」をクリックする<br>
        <img src="https://user-images.githubusercontent.com/25688193/140601923-c575d907-a8db-4aab-8f99-66f0da393901.png" width="400"><br>
    1. 「有効」をクリックする<br>
        <img src="https://user-images.githubusercontent.com/25688193/140601942-874ab099-78ef-450e-b390-9da1763b9e55.png" width="400"><br>

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

1. `firebase/initFirebase.js` を作成する
    FireBase の初期化処理を行う `initFirebase.js` を作成する

    ```js
    import firebase from "firebase";

    // Firebaseの初期化
    const firebaseConfig = {
      apiKey: "AIzaSyBSKhjSkI0pERNnYhcrl3Uldl47ZyGvNqE",
      authDomain: "react-firebase-app-2cc53.firebaseapp.com",
      databaseURL: "https://react-firebase-app-2cc53-default-rtdb.firebaseio.com",
      projectId: "react-firebase-app-2cc53",
      storageBucket: "react-firebase-app-2cc53.appspot.com",
      messagingSenderId: "686383733508",
      appId: "1:686383733508:web:a1d5c2ec271201d87b4e51",
      measurementId: "G-MCWN891SRK"   
    };

    if (firebase.apps.length == 0) {
      firebase.initializeApp(firebaseConfig);
    }
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
    
	  - `pages/index.js` 内で Firebase の初期化処理を行うと、他のページのコンポーネント（今回の場合は `pages/show.js` など）で Firebase が使えなくなるので、別の独立したファイルで初期化を行い、Firebase を使用する各ページのコンポーネントで、このファイルを import するようにする。

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
