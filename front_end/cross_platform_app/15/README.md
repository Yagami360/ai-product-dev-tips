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
    import 'package:flutter/material.dart';
    import 'dart:io';
    import 'package:firebase_core/firebase_core.dart';      // For Firebase
    import 'package:cloud_firestore/cloud_firestore.dart';  // For Firestore

    // main 関数を非同期関数にする
    Future<void> main() async {
    // Firebase.initializeApp() する前に必要な処理。この処理を行わないと Firebase.initializeApp() 時にエラーがでる
    WidgetsFlutterBinding.ensureInitialized();

    //-------------------------------
    // Firebase の初期化処理
    //-------------------------------
    // ios/andriod で起動する場合
    await Firebase.initializeApp();

    // Chrome で起動する場合
    /*
    await Firebase.initializeApp(
        options: FirebaseOptions(
            apiKey: " APIキー ",
            authDomain: "プロジェクト.firebaseapp.com",
            databaseURL: "https://プロジェクト.firebaseio.com",
            projectId: "プロジェクト",
            storageBucket: "プロジェクト.appspot.com",
            messagingSenderId: " ID番号 "
            appId: "appid",
            measurementId: "measurementId"
        ),    
    );
    */

    /*
    print("Platform.isIOS : ${Platform.isIOS}");
    print("Platform.isAndroid : ${Platform.isAndroid}");

    // runApp(...) の前では Platform.isIOS の値は取れない？
    if(Platform.isIOS || Platform.isAndroid ) {
        await Firebase.initializeApp();
    }
    else {
        await Firebase.initializeApp(
        options: FirebaseOptions(
            apiKey: "AIzaSyBe2uVN91FHE_d86h5zfdoHvvj2StIl3lo",
            authDomain: "flutter-app-20eec.firebaseapp.com",
            projectId: "flutter-app-20eec",
            storageBucket: "flutter-app-20eec.appspot.com",
            messagingSenderId: "712798902626",
            appId: "1:712798902626:web:920f725cbda10bedccf43b",
            measurementId: "G-1FELNJ9ZQ5",
        ),    
        );
    }
    */
    
    //-------------------------------
    // アプリを起動
    //-------------------------------
    runApp(const MyApp());
    }

    class MyApp extends StatelessWidget {
    const MyApp({Key? key}) : super(key: key);

    // This widget is the root of your application.
    @override
    Widget build(BuildContext context) {
    return MaterialApp(
        title: 'Flutter Demo',
        theme: ThemeData(
        primarySwatch: Colors.blue,
        ),
        home: const MyHomePage(title: 'Flutter Demo Home Page'),
    );
    }
    }

    class MyHomePage extends StatefulWidget {
    const MyHomePage({Key? key, required this.title}) : super(key: key);
    final String title;

    @override
    State<MyHomePage> createState() => _MyHomePageState();
    }

    class _MyHomePageState extends State<MyHomePage> {
    final String collectionName = "todo_database";
    String _todoText = "";  // Add ボタンクリック時に入力フィールドの値を参照できるように、フィールド変数で定義

    //---------------------------------
    // Add ボタンクリック時のコールバック関数
    //---------------------------------
    void _onPressedAdd() {
    print("call onPressedAdd()");

    // Firestore のコレクションに自動ドキュメントIDでフィールドを追加する。コレクションがない場合はコレクションも作成する
    FirebaseFirestore.instance.collection(collectionName).add({
        'createdAt': Timestamp.fromDate(DateTime.now()),
        "text": _todoText,
    });
    }

    //---------------------------------
    // Delete ボタンクリック時のコールバック関数
    //---------------------------------
    void _onPressedDelete(String docId) {
    print("call onPressedDelete()");

    // 指定したドキュメントID のデータを削除する
    FirebaseFirestore.instance.collection(collectionName).doc(docId).delete();
    }

    //---------------------------------
    // Firestore 内のデータ一覧を表示する Widget を返す関数
    //---------------------------------
    Widget _buildTodoList(BuildContext context) {
    // StreamBuilder を使用して Firestore のコレクションに更新があった場合に、自動的に再描画する
    return StreamBuilder(
        // stream プロパティに入力データとしての Firestore のコレクションの snapshots を設定
        stream: FirebaseFirestore.instance.collection(collectionName).orderBy('createdAt', descending: true).snapshots(),
        // builder プロパティに stream プロパティで設定した入力データを元に出力されるデータが非同期的に入ってくる度に呼び出されるコールバック関数を設定する。出力データは、コールバック関数の snapshot 引数に格納される
        builder: (BuildContext context, AsyncSnapshot<QuerySnapshot> snapshot) {
        // エラーの場合
        if (snapshot.hasError) {
            return Text('Error: ${snapshot.error}');
        }
        else if (!snapshot.hasData) {
            return Container();
        }
        else {
            // Flexible(ListView(...)) : Column の中で ListView を使う場合、そのまま使うと ListView の大きさが定まらず、エラーが発生する。Flexible を用いると、ListView が Overflow する限界まで広がり、エラーなしで表示できるようになる。
            return Flexible(
            child: ListView(
                // snapshot.data!.docs に各ドキュメントIDのドキュメントデータ全体が格納されているので、これを map(...) で　　Widget に変換したものを ListView の children プロパティに設定する
                // ※ ! は「non-nullableな型にキャスト」することを明示するための Dart 構文
                children: snapshot.data!.docs.map(
                (DocumentSnapshot document) {
                    //print("document: ${document}");
                    //print("document[text]: ${document["text"]}");
                    String createdAtString = document["createdAt"].toDate().toString().split(".")[0];
                    return Container(
                    color: Colors.lightBlue.shade50,
                    margin: EdgeInsets.fromLTRB(2, 2, 2, 2),
                    child: Row(
                        //mainAxisAlignment: MainAxisAlignment.center,  // 中央配置
                        children : [
                        Text(createdAtString, textAlign: TextAlign.center,),
                        Spacer(flex: 1,),         // `Spacer` を使用して、余白を確保する
                        Text(document["text"], textAlign: TextAlign.left ),
                        Spacer(flex: 1,),
                        // Database の削除
                        OutlinedButton(
                            onPressed: () { _onPressedDelete(document.id); },
                            child: Text('Delete'),
                        ),
                        ],
                    )
                    );
                },
                ).toList()
            )
            );
        }
        }
    );
    }

    //---------------------------------
    // build 関数
    //---------------------------------
    @override
    Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(
        title: Text(widget.title),
        ),
        body: Container(
        margin: EdgeInsets.fromLTRB(10, 10, 10, 10),    // マージン（Container外側の余白）
        child : Column(
            children: <Widget>[
            //--------------------------
            // Database への追加 UI
            //--------------------------
            Text(
                'Firestore Database にデータ追加',
                style: TextStyle(
                fontSize: 16,
                ),
            ),
            SizedBox(height: 8,),              
            Row(
                mainAxisAlignment: MainAxisAlignment.center,  // 中央配置
                children : [
                Flexible(
                    child: TextField(
                    enabled: true,
                    onChanged: (value) {
                        _todoText = value;
                    },
                    ),
                ),
                OutlinedButton(
                    onPressed: _onPressedAdd,
                    child: Text('Add'),
                ),
                ],
            ),
            SizedBox(height: 20,),
            //--------------------------
            // Database 内容表示 UI
            //--------------------------
            Text(
                'Firestore Database の内容表示',
                style: TextStyle(
                fontSize: 16,
                ),
            ),
            SizedBox(height: 8,),              
            _buildTodoList(context),
            ],
        ),
        ),
    );
    }
    }
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

    - Firestore の CRUD 処理は、以下のメソッドで行う。
        - `FirebaseFirestore.instance.collection(collectionName).add(...)` を使用して、Firestore のコレクションにデータを追加することができる。この関数でデータを追加する場合は、ドキュメントID は自動的に割り振られた ID になる。指定したコレクション名のコレクションがない場合はコレクションも作成する

        - `FirebaseFirestore.instance.collection(collectionName).doc(docId).delete();` を使用して、指定したドキュメントID のデータを削除する

        - `FirebaseFirestore.instance.collection(collectionName).snapshots()` を使用して、指定したコレクション名のデータ（`snapshots`）を取得することができる。更に、`FirebaseFirestore.instance.collection(collectionName).orderBy('createdAt', descending: true).snapshots()` のようにすることで、フィールドの値に応じてデータをソートすることもできる

    - 今回の例では、Firestore のコレクション `todo_database` のデータを動的に表示させるために、StreamBuilder を使用して Firestore のコレクションに更新があった場合に、自動的に再描画するようにしている。
        - より詳細には、`StreamBuilder` の `stream` プロパティ（入力側）に、`FirebaseFirestore.instance.collection(collectionName).orderBy('createdAt', descending: true).snapshots()` を設定し、Firestore のコレクションの `snapshots` を設定する。
        - そして、`StreamBuilder` の `builder` プロパティ（出力側）には、`stream` プロパティで設定した入力データを元に出力されるデータが非同期的に入ってくる度に呼び出されるコールバック関数 `(BuildContext context, AsyncSnapshot<QuerySnapshot> snapshot) { ... }` を設定する。このとき出力データ（Firestore のコレクションデータ）は、コールバック関数の `snapshot` 引数に格納される

        - Firestore のコレクションデータは、`snapshot` に格納されているが、ドキュメントデータは、`snapshot.data!.docs` でアクセスすることができる。
            今回の例では、`snapshot.data!.docs` を `map(...)` で、コレクション内のフィールド値を表示する Widget に変換し、それを `ListView` の `children` プロパティに設定することで、コレクション内のフィールド値を可変長のリスト表示するようにしている。
            
        > Stream（小川）とは、データを作った側（小川の上流）は、自分がデータを作ったらStream（小川）に set して、データを使う側（小川の下流）は、Stream を監視しておき、データが流れてきたら get するというように、小川の上流で物（データ）を流す人（オブジェクト）と小川の下流で物（データ）を受け取る人（オブジェクト）がいるというイメージの機能。<br>
        > Stream を使用することで、非同期な連続したデータの受け渡しに対応できるメリットがある。<br>
        > そして StreamBuilder は、ある Stream を監視して、イベント（データ）が通知される度に Widget を更新（再描画）する機能
        > - 参照サイト
        >     - https://zenn.dev/kazutxt/books/flutter_practice_introduction/viewer/intermediate_bloc


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

