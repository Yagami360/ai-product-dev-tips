# 【Flutter】Flutter を使用して Web アプリの Hello World を行う

## ■ 方法

1. flutter SDK をダウンロードする<br>
    [Flutter 公式サイト](https://docs.flutter.dev/get-started/install) から flutter SDK の zip ファイルをダウンロードする
    ```sh
    $ wget https://storage.googleapis.com/flutter_infra_release/releases/stable/macos/${SDK_FILE_NAME}.zip
    ```

1. flutter コマンドへのパスを設定する<br>
    `~/.bash_profile` に `export PATH="$PATH:`${flutter SDKのディレクトリパス}`/flutter/bin"` を追加して、flutter コマンドへのパスを設定する

    ```sh
    $ echo "" >> ~/.bash_profile
    $ echo "# flutter sdk のパス設定" >> ~/.bash_profile
    $ echo "export PATH=""$""PATH":${INSTALL_PATH}/flutter/bin"" >> ~/.bash_profile
    $ cat ~/.bash_profile
    $ source ~/.bashrc
    ```

    ```sh
    # バージョン確認（要ターミナル再起動）
    $ which flutter
    $ flutter doctor  
    ```

1. VSCode で [Flutter の拡張機能](https://marketplace.visualstudio.com/items?itemName=Dart-Code.flutter) を追加する<br>

1. VSCode を再起動する<br>

1. Flutter プロジェクトを作成する。<br>
    - CLI コマンドを使用する場合<br>
      以下の CLI コマンドで Flutter プロジェクトを作成できる。
      ```sh
      # Flutter プロジェクトを作成する
      flutter create -t app --project-name ${PROJECT_NAME} ./${PROJECT_NAME}
      ```

    - VSCode を使用する場合<br>
      VSCode の「表示 > コマンドパレット > Flutter New Application Project」で Flutter プロジェクトを作成できる。

    プロジェクト（＝アプリ）のフォルダ構成は、以下のようになる

    - lib : 共通コード
    - web : Web アプリ固有のコード
    - ios : iOS 個別のコード
    - andriod : アンドロイドアプリ固有のコード
    - test : テストコード

1. `lib/main.dart` のコードを修正する<br>

    ```dart
    import 'package:flutter/material.dart';

    void main() {
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
            // This is the theme of your application.
            //
            // Try running your application with "flutter run". You'll see the
            // application has a blue toolbar. Then, without quitting the app, try
            // changing the primarySwatch below to Colors.green and then invoke
            // "hot reload" (press "r" in the console where you ran "flutter run",
            // or simply save your changes to "hot reload" in a Flutter IDE).
            // Notice that the counter didn't reset back to zero; the application
            // is not restarted.
            primarySwatch: Colors.blue,
          ),
          home: const MyHomePage(title: 'Flutter Demo Home Page'),
        );
      }
    }

    class MyHomePage extends StatefulWidget {
      const MyHomePage({Key? key, required this.title}) : super(key: key);

      // This widget is the home page of your application. It is stateful, meaning
      // that it has a State object (defined below) that contains fields that affect
      // how it looks.

      // This class is the configuration for the state. It holds the values (in this
      // case the title) provided by the parent (in this case the App widget) and
      // used by the build method of the State. Fields in a Widget subclass are
      // always marked "final".

      final String title;

      @override
      State<MyHomePage> createState() => _MyHomePageState();
    }

    class _MyHomePageState extends State<MyHomePage> {
      int _counter = 0;

      void _incrementCounter() {
        setState(() {
          // This call to setState tells the Flutter framework that something has
          // changed in this State, which causes it to rerun the build method below
          // so that the display can reflect the updated values. If we changed
          // _counter without calling setState(), then the build method would not be
          // called again, and so nothing would appear to happen.
          _counter++;
        });
      }

      @override
      Widget build(BuildContext context) {
        // This method is rerun every time setState is called, for instance as done
        // by the _incrementCounter method above.
        //
        // The Flutter framework has been optimized to make rerunning build methods
        // fast, so that you can just rebuild anything that needs updating rather
        // than having to individually change instances of widgets.
        return Scaffold(
          appBar: AppBar(
            // Here we take the value from the MyHomePage object that was created by
            // the App.build method, and use it to set our appbar title.
            title: Text(widget.title),
          ),
          body: Column(children: [
            Text("Hello Flutter App"),
            Text("counter : $_counter"),
          ]),
          floatingActionButton: FloatingActionButton(
            onPressed: _incrementCounter,
            tooltip: 'Increment',
            child: const Icon(Icons.add),
          ), // This trailing comma makes auto-formatting nicer for build methods.
        );
      }
    }
    ```

    ポイントは、以下の通り

    - プログラムが開始されると一番最初に呼び出されるのは、`lib/main.dart` の `main` 関数になる
    - `main` 関数の中の `runApp(const MyApp());` で `MyApp` クラスのオブジェクトを呼び出している
    - `MyApp` クラスの `build` メソッド内の `home: const MyHomePage(title: 'Flutter Demo Home Page'),` で `MyHomePage` クラスのオブジェクトを呼び出している。
    - `MyHomePage` クラスを継承した `_MyHomePageState` クラスの `build` メソッド内の `return Scaffold(...)` 内で定義している内容（＝Widget）が、画面表示の実体になっている。

    - Flutter は Widget というコンポーネント（アイコン、ボタン、画像やこれらの配置（行配置・列配置・中央揃え）など）の組み合わせで画面を構成している。<br>

      <img src="https://user-images.githubusercontent.com/25688193/153112644-261aee3b-71e2-4ebc-b0eb-b1b2f72750da.png" width="500"><br>

    - `_MyHomePageState` クラスで定義している `_counter` は値が変わると即座に画面表示の変わる Stateful な変数（React でいう useState()）である必要がある。<br>
      Stateful な変数であるようにするために `setState()` で値の更新処理を定義し、`MyHomePage` を `StatefulWidget` を継承したクラスで定義し Stateful なページであることを明示している。（`StatefulWidget` を継承したクラスでのみ `setState()` が使える）

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

<!--
1. 作成したプロジェクトのアプリを android エミュレータで実行する<br>
    Android Studio をインストールした上で、以下の操作を実行する。<br>

    - CLI コマンドを使用する場合<br>
      1. 以下の CLI コマンドを実行して、android のエミュレータを起動する
          ```sh
          ```
      1. 以下の CLI コマンドを実行して、android エミュレータ上でアプリを実行する
          ```sh
          $ cd ${PROJECT_NAME}
          $ flutter run
          ```

    - VSCode を使用する場合<br>
      1. 以下の CLI コマンドを実行して、android のエミュレータを起動する
          ```sh
          ```
      1. VSCode の右下にある device をクリックし、実行デバイスとして android を選択する。
      1. VSCode の「実行 > デバッグ > Dart & Flutter」ボタンをクリックし、android エミュレータ上でアプリを実行する
-->

1. アプリをデプロイする<br>
    アプリを公開する場合は、xxx でアプリをデプロイする。

## ■ 参考サイト
- https://zenn.dev/kazutxt/books/flutter_practice_introduction/viewer/tutorial_environment
- https://zenn.dev/kazutxt/books/flutter_practice_introduction/viewer/tutorial_helloworld
