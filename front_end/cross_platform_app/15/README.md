# 【Flutter】Flutter アプリから Firestore Database を使用する。

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

    1. Web アプリ用の firebase SDK をインストールする<br>
        ```sh
        $ cd ${PROJECT_NAME}
        $ npm install --save firebase@8.10.0
        ```

          > バージョン指定なしの `npm install --save firebase` でインストールすると、現時点（21/10/31）では version 9.x の Firebase がインストールされるが、version8 -> version9 へ変更した場合は、firebase の import 方法が、`import firebase from 'firebase/app';` -> `import { initializeApp } from 'firebase/app';` に変更されたりしており、version8 の Firebase コードが動かなくなることに注意

    1. 設定ワークフロー画面でアプリ名を入力後、「アプリを登録」ボタンをクリックする。このとき、以下の画面のコードをコピーし、`${FLUTTER_PROJECT_DIR}/web/index.html` にコードを追加し、Firebase の初期化コードを追加する。

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

    1. iOS アプリ用の firebase SDK をインストールする<br>
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
            cloud_firestore: ^2.3.0     # For Firebase Firestore
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

1. Firestore Database を作成する。<br>
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
    1. 「+コレクションを開始」ボタンをクリックして、以下のような「コレクション -> ドキュメント -> フィールド」の階層構造をもつデータベースを作成する<br>
        <img src="https://user-images.githubusercontent.com/25688193/140602330-315bc90b-3c0d-4b02-b4b1-490158731309.png" width="400"><br>
        - コレクション : データベースの土台。コレクションの中にドキュメントとしてデータを追加していく。コレクションは複数個作成できる
        - ドキュメント : コレクションに保管されるデータの１セット。通常コレクションの中にフィールドとしてデータを追加していくが、コレクションの中のドキュメント内に別のコレクションを追加することも出来る
        - フィールド : key, value で保存される実際の値

<!--
1. Firebase プロジェクトの初期化<br>
    1. npm をインストール
        - MacOS の場合
            ```sh
            # Node.jsをインストール
            $ brew install node
            ```
        > npm : Node.js のパッケージを管理するコマンド

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

-->

### III. Flutter アプリのコード実装＆アプリの起動

1. `lib/main.dart` を作成する<br>
    ```dart
    ```

    ポイントは、以下の通り

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

- https://zenn.dev/kazutxt/books/flutter_practice_introduction/viewer/firebase_overview#ios%E3%81%AE%E8%A8%AD%E5%AE%9A
- https://github.com/nzigen/flutter_book_samples/tree/main/5_database/firebase_sample
- https://zenn.dev/captain_blue/articles/checking-bundle-id-in-flutter
