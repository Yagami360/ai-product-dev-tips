# 【Flutter】Flutter アプリから Firebase Authentication でのユーザー認証を利用する

## ■ 方法

### I. Flutter の設定

1. Flutter プロジェクトを作成する。<br>
    - CLI コマンドを使用する場合<br>
      以下の CLI コマンドで Flutter プロジェクトを作成できる。
      ```sh
      # Flutter プロジェクトを作成する
      flutter create -t app --project-name ${PROJECT_NAME} ./${PROJECT_NAME}
      ```

    - VSCode を使用する場合<br>
      VSCode の「表示 > コマンドパレット > Flutter New Application Project」で Flutter プロジェクトを作成できる。


### II. Firebase の設定

1. Firebase プロジェクトの作成<br>
    1. [Firebase コンソール画面](https://console.firebase.google.com/?hl=ja&pli=1)にアクセス
    1. 「プロジェクトを作成」
    1. 「設定」ボタン→「全般」タブから、GCP リソースのリージョンを指定する<br>
        <img src="https://user-images.githubusercontent.com/25688193/107106996-d4759180-6871-11eb-909c-14915bde83c6.png" width="500"><br>    

1. ウェブアプリを Firebase に登録する<br>
    1. Firebase コンソールの「プロジェクトの概要」ページの中央にあるウェブアイコン `</>` をクリックし、設定ワークフローを起動する。<br>
        <img src="https://user-images.githubusercontent.com/25688193/107107327-bd37a380-6873-11eb-972d-4957992a748c.png" width="300"><br>

    1. 設定ワークフロー画面でアプリ名を入力後、「アプリを登録」ボタンをクリックする。
    
    1. 【旧 Firebase のバージョンを使用する場合のみ必要な処理】<br>
        `${FLUTTER_PROJECT_DIR}/web/index.html` を以下のような内容に書き変えて、Firebase の初期化コードを追加する。
        このとき、`firebaseConfig` の値は、以下の画面のコードの内容にする
        <img src="https://user-images.githubusercontent.com/25688193/138590270-3304ca03-787d-43d2-8c81-e6f65e754b6e.png" width="300"><br>

        ```html
        <!DOCTYPE html>
        <html>
        <head>
            <!--
                If you are serving your web app in a path other than the root, change the
                href value below to reflect the base path you are serving from.

                The path provided below has to start and end with a slash "/" in order for
                it to work correctly.

                For more details:
                * https://developer.mozilla.org/en-US/docs/Web/HTML/Element/base

                This is a placeholder for base href that will be replaced by the value of
                the `--base-href` argument provided to `flutter build`.
            -->
            <base href="$FLUTTER_BASE_HREF">

            <meta charset="UTF-8">
            <meta content="IE=Edge" http-equiv="X-UA-Compatible">
            <meta name="description" content="A new Flutter project.">

            <!-- iOS meta tags & icons -->
            <meta name="apple-mobile-web-app-capable" content="yes">
            <meta name="apple-mobile-web-app-status-bar-style" content="black">
            <meta name="apple-mobile-web-app-title" content="flutter_app">
            <link rel="apple-touch-icon" href="icons/Icon-192.png">

            <!-- Favicon -->
            <link rel="icon" type="image/png" href="favicon.png"/>

            <title>flutter_app</title>
            <link rel="manifest" href="manifest.json">
        </head>
        <body>
            <!-- The core Firebase JS SDK is always required and must be listed first -->
            <script src="https://www.gstatic.com/firebasejs/8.10.1/firebase-app.js"></script>
            <script src="https://www.gstatic.com/firebasejs/8.10.1/firebase-auth.js"></script>
            <script src="https://www.gstatic.com/firebasejs/8.10.1/firebase-firestore.js"></script>
            <script src="https://www.gstatic.com/firebasejs/8.10.1/firebase-analytics.js"></script>

            <script>
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
            </script>

            <!-- This script installs service_worker.js to provide PWA functionality to
                application. For more information, see:
                https://developers.google.com/web/fundamentals/primers/service-workers -->
            <script>
                var serviceWorkerVersion = null;
                var scriptLoaded = false;
                function loadMainDartJs() {
                if (scriptLoaded) {
                    return;
                }
                scriptLoaded = true;
                var scriptTag = document.createElement('script');
                scriptTag.src = 'main.dart.js';
                scriptTag.type = 'application/javascript';
                document.body.append(scriptTag);
                }

                if ('serviceWorker' in navigator) {
                // Service workers are supported. Use them.
                window.addEventListener('load', function () {
                    // Wait for registration to finish before dropping the <script> tag.
                    // Otherwise, the browser will load the script multiple times,
                    // potentially different versions.
                    var serviceWorkerUrl = 'flutter_service_worker.js?v=' + serviceWorkerVersion;
                    navigator.serviceWorker.register(serviceWorkerUrl)
                    .then((reg) => {
                        function waitForActivation(serviceWorker) {
                        serviceWorker.addEventListener('statechange', () => {
                            if (serviceWorker.state == 'activated') {
                            console.log('Installed new service worker.');
                            loadMainDartJs();
                            }
                        });
                        }
                        if (!reg.active && (reg.installing || reg.waiting)) {
                        // No active web worker and we have installed or are installing
                        // one for the first time. Simply wait for it to activate.
                        waitForActivation(reg.installing || reg.waiting);
                        } else if (!reg.active.scriptURL.endsWith(serviceWorkerVersion)) {
                        // When the app updates the serviceWorkerVersion changes, so we
                        // need to ask the service worker to update.
                        console.log('New service worker available.');
                        reg.update();
                        waitForActivation(reg.installing);
                        } else {
                        // Existing service worker is still good.
                        console.log('Loading app from service worker.');
                        loadMainDartJs();
                        }
                    });

                    // If service worker doesn't succeed in a reasonable amount of time,
                    // fallback to plaint <script> tag.
                    setTimeout(() => {
                    if (!scriptLoaded) {
                        console.warn(
                        'Failed to load app from service worker. Falling back to plain <script> tag.',
                        );
                        loadMainDartJs();
                    }
                    }, 4000);
                });
                } else {
                // Service workers not supported. Just drop the <script> tag.
                loadMainDartJs();
                }
            </script>

            <script src="main.dart.js" type="application/javascript"></script>
        </body>
        </html>
        ```

        > `service_worker.js` や `main.dart.js` の読み込みは、Firebase の初期化後に行う必要があることに注意

        > 本処理は、旧 Firebase のバージョンでのみ必要な処理になっていることに注意。新しい Firebase のバージョンでは、`index.html` はそのままで、`main.dart` で `Firebase.initializeApp(...)` で Firebase を初期化処理する際に、API キーなどの各種コンフィグ値を設定するだけでよくなっている。今回の Firebase バージョンでは、後者の方法を採用している
        > - 参照サイト
        >     - https://stackoverflow.com/questions/70232931/firebaseoptions-cannot-be-null-when-creating-the-default-app

1. iOS アプリを Firebase に登録する<br>
    1. Firebase コンソールの「プロジェクトの概要」ページの中央にある iOS アイコン `iOS+` をクリックし、「Apple アプリへの Firebase の追加」画面を起動する。<br>
    1. 「Apple アプリへの Firebase の追加」画面にて、「Apple バンドル ID」を入力し、「アプリを登録」ボタンをクリックする<br>

        > 「Apple バンドル ID」は、`${FLUTTER_PROJECT_DIR}/ios/Runner.xcodeproj/project.pbxproj` の `PRODUCT_BUNDLE_IDENTIFIER` の値から取得できる。<br>

        <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/155833852-b51ce5df-236c-4da7-986d-2685a19ed647.png">

    1. ダウンロードした設定ファイル `GoogleService-Info.plist` を Flutter アプリの `${FLUTTER_PROJECT_DIR}/ios/Runner` ディレクトリ以下に配置し、「次へ」ボタンをクリックする

        > VSCode を使って `GoogleService-Info.plist` で単純にコピーしても参照情報などのリンクがうまく作られないことがあるので、この配置処理は、VSCode ではなく XCode で行う必要があることに注意。作成した Flutter プロジェクトを XCode で開くには、以下のコマンドを実行すればよい。
        > ```sh
        > $ open ${FLUTTER_PROJECT_DIR}/ios/Runner.xcodeproj
        > ```

        > ダウンロードした設定ファイル `GoogleService-Info.plist` は、GitHub 上に公開しないようにすること

        <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/155834122-b85ce2d5-df1a-4c0f-b49d-44b7f140b039.png">

    1. `{FLUTTER_PROJECT_DIR}/ios/Runner/info.plist` に、以下のコードを追加する<br>
        ```
        <array>
            <dict>
                <key>CFBundleTypeRole</key>
                <string>Editor</string>
                <key>CFBundleURLSchemes</key>
                <array>
                    <string>{REVERSED_CLIENT_ID}</string>
                </array>
            </dict>
        </array>
        ```

        このとき `{REVERSED_CLIENT_ID}` には、`GoogleService-Info.plist` 内の `REVERSED_CLIENT_ID` の値を設定する

1. android アプリを Firebase に登録する<br>
    xxx

1. Flutter の firebase SDK をインストールする<br>
    `${FLUTTER_PROJECT_DIR}/pubspec.yaml` を以下のように修正し、Firebase SDK をインストールする

    ```yaml
    name: flutter_app
    description: A new Flutter project.
    publish_to: 'none' # Remove this line if you wish to publish to pub.dev
    version: 1.0.0+1

    environment:
        sdk: ">=2.16.0 <3.0.0"

    dependencies:
        flutter:
            sdk: flutter

        cupertino_icons: ^1.0.2
        firebase_core: ^1.3.0       # For Firebase
        firebase_auth: ^1.0.1       # For Firebase Auth
        google_sign_in: ^5.0.2      # Google アカウントでのログインを行う場合に必要
        ...
    ```

    > 上記のようにして、Firebase のパッケージをインストールした場合に、iOS 環境でのビルド時に `CocoaPods could not find compatible versions for pod Firebase/Core ...` といった内容のエラーが発生するケースがある。この場合は、`${FLUTTER_PROJECT_DIR}/ios/Podfile` にあるファイルに `platform :ios, '12.0'` の行を追加して、CocoaPods の iOS バージョンを 12.0 に指定すれば解決される。
    > - 参考サイト : https://zenn.dev/umi_mori/articles/328fb6f96dfc4e

    - `ios/Podfile`
        ```yaml
        # この行を追加
        platform :ios, '12.0'

        # CocoaPods analytics sends network stats synchronously affecting flutter build latency.
        ENV['COCOAPODS_DISABLE_STATS'] = 'true'

        project 'Runner', {
            'Debug' => :debug,
            'Profile' => :release,
            'Release' => :release,
        }
        ...
        ```

1. Firestore Auth の設定<br>
    1. [Authenticationコンソール画面](https://console.firebase.google.com/project/sample-app-73cab/authentication/providers?hl=ja) から各種ログイン方法を「有効」にする。<br>
        <img src="https://user-images.githubusercontent.com/25688193/107348240-1caee100-6b0a-11eb-9b61-8a7d3163422d.png" width="500"><br>

    1. メールアドレスでのログインを有効にする場合の設定<br>
        メールアドレスでのログインを有効化したあとで、「Authentication -> Users」画面で、「ユーザーを追加」ボタンをクリックし、ログイン可能なメールアドレスとそのパスワードを登録しておく。<br>
        <image src="https://user-images.githubusercontent.com/25688193/107481910-49beca80-6bc2-11eb-9b5b-aa2589c30bfb.png" width="500"><br>

    1. Google アカウントでのログインを有効にする場合の設定<br>
        「Authenctication > Sign-in method」から、「Google」を選択し、Google アカウントでのログインを有効化する

    1. GitHub を有効にする場合の設定<br>
        GitHub を有効にする場合は、GitHub のクライアントIDとクライアントシークレットが必要になる。<br>
        <image src="https://user-images.githubusercontent.com/25688193/107350003-3d783600-6b0c-11eb-8b29-f4fbfd400164.png" width="500"><br>

        クライアントIDとクライアントシークレットは、GitHub 上の「Settings -> Developer settings -> OAuth Apps」で、「Register a new OAuth application」作成後に取得できる。この際の Homepage URL には、今作成している firebase アプリの URL を指定し、Authorization callback URL には、上記画面で提示されているコールバック URL を貼り付ければよい。<br>
        <image src="https://user-images.githubusercontent.com/25688193/107350167-6e586b00-6b0c-11eb-8a41-a1f61e942b07.png" width="800"><br>


### III. Flutter アプリのコード実装＆アプリの起動

1. `lib/main.dart` を作成する<br>
    ```dart
    ```

    ポイントは、以下の通り

    - `import 'package:firebase_core/firebase_core.dart'` で Firebase をコアパッケージを import し、`import 'package:cloud_firestore/cloud_firestore.dart'` で Firestore のパッケージを import する

    - `main()` 関数内にて、`runApp()` でアプリを起動する前に、`Firebase.initializeApp()` を呼び出し、Firebase を初期化する。
        - このとき、`Firebase.initializeApp()` は非同期関数なので、`await Firebase.initializeApp();` の形式で呼び出し、処理が完了するまで await する。
        - `main()` 関数で await できるようにするために、`main()` 関数は、`Future<void> main() async {...}` の形式で定義して非同期関数にする。
        - 更に、`Firebase.initializeApp()` を呼び出す前に、`WidgetsFlutterBinding.ensureInitialized();` を呼び出すようにする。この処理を行わないと `Firebase.initializeApp()` 呼び出し時にエラーがでる。
        
            > `WidgetsFlutterBinding.ensureInitialized();` は、`runApp()` でアプリを起動する前に Flutter Engine の機能（iOS や android などのプラットフォームでレンダリングなどをする機能）を利用したい場合にコールする関数。今回のケースでは、`runApp()` でアプリを起動する前に `Firebase.initializeApp()` を呼び出しているが、`Firebase.initializeApp()` 内で Flutter Engine の機能を利用するので、呼び出す必要がある。

            > - 参照サイト
            >     - https://qiita.com/kurun_pan/items/04f34a47cc8cee0fe542

        - ios/android アプリで動作させる場合は、`Firebase.initializeApp()` の引数は設定しなくていいが、今回の Firebase バージョンで Chrome アプリで動作させる場合は、`Firebase.initializeApp()` の `options` プロパティに、 `FirebaseOptions(...)` で API キーなどの各種コンフィグ値を設定する必要がある。

            > - 参照サイト
            >     - https://stackoverflow.com/questions/70232931/firebaseoptions-cannot-be-null-when-creating-the-default-app

    - xxx

1. 作成したプロジェクトのアプリを Chrome ブラウザのエミュレータで実行する<br>
    - CLI コマンドを使用する場合<br>
      以下の CLI コマンドを実行することでアプリを実行できる。
      ```sh
      $ cd ${PROJECT_NAME}
      $ flutter run
      ```

    - VSCode を使用する場合<br>
      1. VSCode の右下にある device をクリックし、実行デバイスとして Chrome を選択する。
      1. VSCode の「実行 > デバッグ > Dart & Flutter」ボタンをクリックし、Chrome エミュレータ上でアプリを実行する

1. 作成したプロジェクトのアプリを iOS エミュレータで実行する<br>
    Xcode をインストールした上で、以下の操作を実行する。<br>

    - CLI コマンドを使用する場合<br>
      1. 以下の CLI コマンドを実行して、iOS のエミュレータを起動する
          ```sh
          $ open -a simulator
          ```
      1. 以下の CLI コマンドを実行して、iOS エミュレータ上でアプリを実行する
          ```sh
          $ cd ${PROJECT_NAME}
          $ flutter run
          ```

    - VSCode を使用する場合<br>
      1. 以下の CLI コマンドを実行して、iOS のエミュレータを起動する
          ```sh
          $ open -a simulator
          ```
      1. VSCode の右下にある device をクリックし、実行デバイスとして iOS を選択する。
      1. VSCode の「実行 > デバッグ > Dart & Flutter」ボタンをクリックし、iOS エミュレータ上でアプリを実行する

## ■ 参考サイト

- https://zenn.dev/kazutxt/books/flutter_practice_introduction/viewer/firebase_authentication
- https://qiita.com/smiler5617/items/f94fdc1afe088586715b