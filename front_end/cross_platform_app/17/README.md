# 【Flutter】ChangeNotifierProvider を使用して値の状態管理を行う

「[【Flutter】Provider を使用して値の状態管理を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/cross_platform_app/16)」で記載したように、Provider を使用すれば、親 Widget (StatefulWidget) の `setState(...)` で管理した状態を、子 Widget から直接取得することができるが、更に `ChangeNotifierProvider` を使用すれば、`setState(...)` を使用しなくとも、祖先 Widget の状態変更を子 Widget に通知することができる。

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

1. `lib/Counter.dart` を作成する<br>
    状態管理を行う変数を定義した `lib/Counter.dart` のコードを作成する

    ```dart
    import 'package:flutter/foundation.dart';

    // ChangeNotifier を継承して、状態管理を行う変数のクラスを定義する
    class Counter extends ChangeNotifier {
      int count = 0;

      void incrementCounter() {
        count++;
        // notifyListeners() で状態の値が変更したことを知らせる
        notifyListeners();
      }
    }
    ```

    ポイントは、以下の通り

    -  `ChangeNotifier` を使用するために、`import 'package:flutter/foundation.dart';` でパッケージを import する

    - `ChangeNotifier` を継承して、を継承して、状態管理を行う変数 `count` のクラスを定義する

    - `notifyListeners()` で状態の値が変更したことを知らせる


1. `lib/main.dart` を作成する<br>
    祖先 Widget になる `lib/main.dart` のコードを作成する

    ```dart
    import 'package:flutter/material.dart';
    import 'package:provider/provider.dart';  // Provider を使用するためのパッケージを追加する
    import 'package:flutter_app/Counter.dart';
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
      // ChangeNotifier を継承した状態管理を行う変数のオブジェクトを作成する
      final Counter _counter = Counter();

      @override
      Widget build(BuildContext context) {
        return Scaffold(
          appBar: AppBar(
            title: Text(widget.title),
          ),
          // Scaffold の body プロパティに `ChangeNotifierProvider<ChangeNotifier を継承した状態管理を行う変数の型>.value(ChangeNotifier を継承した状態管理を行う変数 子Widgetの定義)` で値を渡すことで、子 Widget から ChangeNotifier を継承した状態管理を行う変数に直接アクセスできるようになる。
          body: ChangeNotifierProvider<Counter>.value(
            // 子 Widget に渡す状態
            value: _counter,
            // 子 Widget の定義
            child: Center(
              child: WidgetA(),
            ),
          ),
          floatingActionButton: FloatingActionButton(
            onPressed: () {
              _counter.incrementCounter();
            },
            tooltip: 'Increment',
            child: Icon(Icons.add),
          ),      
        );
      }
    }
    ```

    ポイントは、以下の通り

    - `import 'package:provider/provider.dart';` で、Provider を使用するためのパッケージを追加する

    - 祖先 Widget 側では、`build(...)` メソッド内にて、`Scaffold` の `body` プロパティに `ChangeNotifierProvider<状態の型>.value(状態, 子Widgetの定義)` で値を渡すことで、子 Widget から子 Widget から ChangeNotifier を継承した状態管理を行うクラス `Counter` の変数 `count` に直接アクセスできるようになる。


1. `lib/WidgetA.dart` を作成する<br>
    子 Widget になる `lib/WidgetA.dart` のコードを作成する

    ```dart
    import 'package:flutter/material.dart';
    import 'package:provider/provider.dart';  // Provider を使用するためのパッケージを追加する
    import 'package:flutter_app/Counter.dart';

    // StatelessWidget として定義する
    class WidgetA extends StatelessWidget {
      @override
      Widget build(BuildContext context) {
        int count = 0;
        try {
          // Provider.of<ChangeNotifier を継承した状態管理を行う変数のクラス> で、ChangeNotifier を継承した状態管理を行う変数のクラスで定義した状態を受け取る
          final Counter counter = Provider.of<Counter>(context);
          count = counter.count;
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

    - 子 Widget 側では、`build(...)` メソッド内にて、`Provider.of<ChangeNotifier を継承した状態管理を行う変数のクラス>` で、ChangeNotifier を継承した状態管理を行う変数のクラスで定義した状態を受け取る

    - 右下のフローティングボタンクリック時の動作は、以下のようになる
      1. `ChangeNotifier` を継承した状態管理を行うクラス `Counter` の `incrementCounter(...)` が呼び出される
      1. `incrementCounter(...)` 内にて、`notifyListeners()` が呼び出され、状態の値がインクリメントされたことが子 Widget 以下に通知される
      1. 子 Widget 内で `Provider.of<Counter>` で変更されたカウンター値のオブジェクト `counter` が取得され、`counter.count` で取得した画面上のカウンター値もインクリメントされる動作になる
 

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

- https://zenn.dev/kazutxt/books/flutter_practice_introduction/viewer/advanced_provider
- https://www.flutter-study.dev/create-app/provider
