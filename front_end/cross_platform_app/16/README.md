# 【Flutter】Provider を使用して値の状態管理を行う

StatefulWidget を使用すれば、各 Widget の状態管理を行うことができるが、Widget の数が多くなってくると、各 Widget 内で個別の状態管理を行う方法では状態管理しきれなくなってくる問題がある。

Provider は、InheritedWidget のラッパーパッケージで、親 Widget から子 Widget に状態管理の対象となるデータを受け渡すことで、このような複雑な状態管理も簡単に行えるようにした機能である。

ここでは、Provider を使用して、親 Widget (StatefulWidget) の `setState(...)` で管理した状態を、子 Widget から直接取得する方法を記載する。

<img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/155875308-6685f80a-1a69-4c8d-86f8-5c1420a3db01.png">


> - InheritedWidget<br>
>   Widget ツリーにおいて、親の親（先祖） Widget の変数にアクセスしたい場合、上位の Widget から 子 Widget 順次パラメタ引数で渡していくのが一般的であるが、この方法だと Widget ツリーの階層が深くなっていくと、先祖 Widget の変数にアクセスする処理効率が悪くなる問題がある。InheritedWidget は、下位のツリーの Widget から O(1) で先祖 Widget の変数にアクセスできるようにした Widget である。<br>
>   <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/155874731-4df7281f-bf4f-4322-ac8c-5580438a6020.png">

## ■ 方法

1. Flutter プロジェクトを作成する。<br>
    - CLI コマンドを使用する場合<br>
      以下の CLI コマンドで Flutter プロジェクトを作成できる。
      ```sh
      # Flutter プロジェクトを作成する
      flutter create -t app --project-name ${PROJECT_NAME} ./${PROJECT_NAME}
      ```

    - VSCode を使用する場合<br>
      VSCode の「表示 > コマンドパレット > Flutter New Application Project」で Flutter プロジェクトを作成できる。


1. `pubspec.yaml` に Provider を使用するためのパッケージを追加する
    ```dart
    dependencies:
      provider: "^5.0.0"
      ...
    ```

1. `lib/main.dart` を作成する<br>
    祖先 Widget になる `lib/main.dart` のコードを作成する

    ```dart
    import 'package:flutter/material.dart';
    import 'package:provider/provider.dart';
    import 'package:flutter_app/WidgetA.dart';

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
      int _counter = 0;
      void _incrementCounter() {
        // `setState(...)` で祖先 Widget の状態 `_counter` の変更を行っている。
        setState(() {
          _counter++;
        });
        print("count:" + _counter.toString());
      }

      @override
      Widget build(BuildContext context) {
        return Scaffold(
          appBar: AppBar(
            title: Text(widget.title),
          ),
          // Scaffold の body プロパティに `Provider<状態１の型>.value(状態１, 子Widgetの定義)` で値を渡すことで、子 Widget から祖先 Widget の状態に直接アクセスできるようになる。
          body: Provider<int>.value(
            // 子 Widget に渡す状態
            value: _counter,
            // 子 Widget の定義
            child: Center(
              child: WidgetA(),
            ),
          ),
          floatingActionButton: FloatingActionButton(
            onPressed: _incrementCounter,
            tooltip: 'Increment',
            child: Icon(Icons.add),
          ),      
        );
      }
    }
    ```

    ポイントは、以下の通り

    - `import 'package:provider/provider.dart';` で、Provider を使用するためのパッケージを追加する

    - 祖先 Widget 側では、`build(...)` メソッド内にて、`Scaffold` の `body` プロパティに `Provider<状態１の型>.value(状態１, 子Widgetの定義)` で値を渡すことで、子 Widget から祖先 Widget の状態に直接アクセスできるようにする。

    - 祖先 Widget は、StatefulWidget で定義し、`setState(...)` で祖先 Widget の状態 `_counter` の変更を行っている。

      > `ChangeNotifierProvider` と `notifyListeners` を使用すれば、`setState(...)` を使用しなくとも、状態変更を子 Widget に通知することができる。

1. `lib/WidgetA.dart` を作成する<br>
    子 Widget になる `lib/WidgetA.dart` のコードを作成する

    ```dart
    import 'package:flutter/material.dart';
    import 'package:provider/provider.dart';

    // StatelessWidget として定義する
    class WidgetA extends StatelessWidget {
      @override
      Widget build(BuildContext context) {
        int count;
        try {
          // Provider.of<int> で祖先 Widget の状態を受け取る
          count = Provider.of<int>(context);
        }
        catch (e) {
          count = 0;
        }
        return Text("$count", style: TextStyle(fontSize: 100));
      }
    }
    ```

    - `import 'package:provider/provider.dart';` で、Provider を使用するためのパッケージを追加する

    - 状態を受け取る 子 Widget を `StatelessWidget` として定義する

    - 子 Widget 側では、`build(...)` メソッド内にて、`Provider.of<int>` で祖先 Widget の状態を受け取る

    - 右下のフローティングボタンクリック時に、祖先 Widget の `setState(...)` で定義したカウンター値のインクリメント処理が行われる。その後子 Widget 内で `Provider.of<int>` で変更されたカウンター値が取得され、画面上のカウンター値もインクリメントされる動作になる
 
    <img width="450" alt="image" src="https://user-images.githubusercontent.com/25688193/155875722-0d3d8333-9a3d-4222-98dc-44ad790fcdfb.png">


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

- https://zenn.dev/kazutxt/books/flutter_practice_introduction/viewer/advanced_inheritedwidget
- https://zenn.dev/kazutxt/books/flutter_practice_introduction/viewer/advanced_provider
- https://www.flutter-study.dev/create-app/provider
