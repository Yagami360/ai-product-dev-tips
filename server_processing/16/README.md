# 【Firebase】Firebase Authentication を使用してウェブアプリに Authentication 機能を導入する

<a id="【事前準備】ログイン方法の設定"></a>

## 1. 【事前準備】ログイン方法の設定

1. [Authenticationコンソール画面](https://console.firebase.google.com/project/sample-app-73cab/authentication/providers?hl=ja) から各種ログイン方法を「有効」にする。<br>
    <img src="https://user-images.githubusercontent.com/25688193/107348240-1caee100-6b0a-11eb-9b61-8a7d3163422d.png" width="500"><br>

1. メールアドレスでのログインを有効にする場合の設定<br>
    メールアドレスでのログインを有効化したあとで、「Authentication -> Users」画面で、「ユーザーを追加」ボタンをクリックし、ログイン可能なメールアドレスとそのパスワードを登録しておく。<br>
    <image src="https://user-images.githubusercontent.com/25688193/107481910-49beca80-6bc2-11eb-9b5b-aa2589c30bfb.png" width="500"><br>

1. GitHub を有効にする場合の設定<br>
    GitHub を有効にする場合は、GitHub のクライアントIDとクライアントシークレットが必要になる。<br>
    <image src="https://user-images.githubusercontent.com/25688193/107350003-3d783600-6b0c-11eb-8b29-f4fbfd400164.png" width="500"><br>

    クライアントIDとクライアントシークレットは、GitHub 上の「Settings -> Developer settings -> OAuth Apps」で、「Register a new OAuth application」作成後に取得できる。この際の Homepage URL には、今作成している firebase アプリの URL を指定し、Authorization callback URL には、上記画面で提示されているコールバック URL を貼り付ければよい。<br>
    <image src="https://user-images.githubusercontent.com/25688193/107350167-6e586b00-6b0c-11eb-8a41-a1f61e942b07.png" width="800"><br>

<!--
1. Twitter を有効にする場合の設定<br>
    1. [Twitter ディベロッパーサイト](https://developer.twitter.com/en/apps) へアクセス
    1. 「Create an app」ボタンをクリック
    1. xxx
-->

## 2. Web アプリでの Authentication の利用（クライアント側から Authentication を利用する場合）
Firebase での Authentication は、以下の２つのパターンで利用できる。<br>

1. クライアント側から Authentication を利用<br>
    ウェブページの HTML `<script>` タグを設置することで、クライアント側から Authentication を利用する方法

1. サーバー側から Authentication を利用<br>
    Node.js で Firebase API を読み込み、サーバー側から Authentication を利用する方法

この内、「クライアント側から Authentication を利用する方法」では、ログインのための GUI などが Firebase によって予め提供されるので、こちらの方法のほうが便利で簡単である。<br>
そのため、以下ではこの方法での手順を記載する。

### 2-1. メールアドレスでのログイン

1. [【事前準備】ログイン方法の設定](#【事前準備】ログイン方法の設定) でメールアドレスでのログインを有効化する。<br>
1. Firebase プロジェクトのディレクトリに移動する。<br>
    Firebase プロジェクト（`public/` ディレクトリなど）が存在しない場合は、以下のコマンドでログインして初期化する。
    1. Firebase へのログイン
        ```sh
        $ firebase login
        ```
    1. Firebase プロジェクトの初期化
        ```sh
        $ firebase init
        ```
1. `index.html` ファイルの作成<br>
    `public/` ディレクトリ以下の `index.html` ファイルを以下のようなファイルに書き換える。<br>
    この内 `config` の値は、「プロジェクトの設定 -> 全般 -> ページ下部にあるマイアプリ ->
 Firebase SDK snippet」の画面からコピーしたものを貼り付ければよい。<br>
    ```html
    <!DOCTYPE html>
    <html lang="ja">
    <head>
    <meta charset="utf-8">
    <title>Sample Page</title>
    <script src="https://www.gstatic.com/firebasejs/5.8.4/firebase-app.js"></script>
    <script src="https://www.gstatic.com/firebasejs/5.8.4/firebase-auth.js"></script>
    <script>
    let config = {
        apiKey: "……APIキー……",
        authDomain: "……AUTHドメイン……",
        databaseURL: "……データベース……",
        projectId: "……プロジェクトID……",
        storageBucket: "……ストレージ……",
        messagingSenderId: "……メッセージID……"
    };
    try {
        firebase.initializeApp(config);     // Firebase の初期化
    } catch(e) {
        console.log(e);
    }

    firebase.auth().onAuthStateChanged((user) => {
        if (user) {
            console.log('auth user', user);
            document.querySelector('#msg').textContent = '"' + user.email + '"" logined!';
        }
    });

    // login
    function login(){
        let email = document.querySelector('#email').value;
        let password = document.querySelector('#password').value;
        firebase.auth().signInWithEmailAndPassword(email, password)
            .then((result) => {
                console.log('sign in successfully.');
            }).catch((error) => {
                console.log(error.message);
                document.querySelector('#msg').textContent = 'fail to login...';
            });
    }

    // logout
    function logout(){
        firebase.auth().signOut();
        document.getElementById('msg').textContent = 'no login...';
    }
    </script>
    </head>
    <body>
    <h1>メールアドレスでのログイン</h1>
    <p id="msg">no login...</p>
    <div id="firebaseui-auth-container"></div>
    <table>
        <tr><th>Email</th>
        <td><input type="email" id="email"></td></tr>
        <tr><th>Password</th>
        <td><input type="password" id="password"></td></tr>
        <tr><th></th><td>
            <button onclick="login();">Login</button>
            <button onclick="logout();">Logout</button>
        </th></tr>
    </table>
    </body>
    </html>
    ```
1. 作成した `index.html` をデプロイする。<br>
    以下のコマンドで作成した `index.html` を Hosting にデプロイして、公開するする。
    ```sh
    $ firebase deploy
    ```
1. Hosting URL にアクセスする<br>
    以下のコマンドなどで、提示された Hosting URL にアクセスし、動作確認する。
    ```sh
    $ open https://${PROJECT_ID}.web.app
    ```

### 2-2. 電話番号でのログイン
xxx

### 2-3. Google アカウントでのログイン

1. [【事前準備】ログイン方法の設定](#【事前準備】ログイン方法の設定) で Google アカウントでのログインを有効化する。<br>
1. Firebase プロジェクトのディレクトリに移動する。<br>
    Firebase プロジェクト（`public/` ディレクトリなど）が存在しない場合は、以下のコマンドでログインして初期化する。
    1. Firebase へのログイン
        ```sh
        $ firebase login
        ```
    1. Firebase プロジェクトの初期化
        ```sh
        $ firebase init
        ```
1. `index.html` ファイルの作成<br>
    `public/` ディレクトリ以下の `index.html` ファイルを以下のようなファイルに書き換える。<br>
    この内 `config` の値は、「プロジェクトの設定 -> 全般 -> ページ下部にあるマイアプリ ->
 Firebase SDK snippet」の画面からコピーしたものを貼り付ければよい。<br>
    ```html
    <!DOCTYPE html>
    <html lang="ja">
    <head>
    <meta charset="utf-8">
    <title>Sample Page</title>
    <script src="https://www.gstatic.com/firebasejs/5.8.4/firebase-app.js"></script>
    <script src="https://www.gstatic.com/firebasejs/5.8.4/firebase-auth.js"></script>
    <script>
    // Initialize Firebase
    let config = {
    apiKey: "AIzaSyBqwt9MVj6JWtDydOa7jflFxy_t8mE0LUg",
    authDomain: "sample-app-73cab.firebaseapp.com",
    databaseURL: "https://sample-app-73cab-default-rtdb.firebaseio.com",
    projectId: "sample-app-73cab",
    storageBucket: "sample-app-73cab.appspot.com",
    messagingSenderId: "101517631439",
    appId: "1:101517631439:web:a68b69649521dbef2ebcba",
    measurementId: "G-MSZ0YNEVK3"
    };
    try {
        firebase.initializeApp(config);
    } catch(e) {
        console.log(e);
    }

    firebase.auth().onAuthStateChanged(function(user) {
        if (user) {
            console.log('auth user', user);
            document.querySelector('#msg').textContent = '"' + user.email + '" logined!';
        }
    });

    // login
    function login(){
        let provider = new firebase.auth.GoogleAuthProvider();
        firebase.auth().signInWithRedirect(provider).then((result) => {
            console.log('sign in successfully.');
        }).catch((error) => {
            console.log('fail to sign in.');
            document.querySelector('#msg').textContent = 'fail to login...';
        });
    }

    // logout
    function logout(){
        firebase.auth().signOut().then((res)=>{
            document.getElementById('msg').textContent = 'no login...';
        });
    }
    </script>
    </head>
    <body>
        <h1>Google アカウントでのログイン</h1>
        <p id="msg">no login...</p>
        <button onclick="login();">Login</button>
        <button onclick="logout();">Logout</button>
    </body>
    </html>
    ```
1. 作成した `index.html` をデプロイする。<br>
    以下のコマンドで作成した `index.html` を Hosting にデプロイして、公開するする。
    ```sh
    $ firebase deploy
    ```
1. Hosting URL にアクセスする<br>
    以下のコマンドなどで、提示された Hosting URL にアクセスし、動作確認する。
    ```sh
    $ open https://${PROJECT_ID}.web.app
    ```

### 2-4. GitHub アカウントでのログイン
xxx

### 2-5. Twitter アカウントでのログイン
xxx

## ■ 参考サイト
- https://www.topgate.co.jp/firebase05-firebase-authentication
