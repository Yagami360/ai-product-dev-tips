# 【Flutter】ListView の `ListView.builder(...)` を使用して可変リスト長のリストレイアウトを行う

ListView は直線的に配置されたスクロール可能なリストの Widget である。<br>
ListViewを構築するためには4つの方法があるが、ここでは２つ目の方法を記載する。

1. `ListView()` オブジェクトを `Scaffold` オブジェクトの `body` プロパティに設定する方法<br>
  最も単純な方法であるが、`ListView()` オブジェクト生成時に明示的にリストを受け取るため、表示するリストが予めわかっている必要がある。

1. `ListView.builder(...)` で生成したオブジェクトを `Scaffold` オブジェクトの `body` プロパティに設定する方法<br>
  表示するリストが予めわかっていないケースや、無限のリストを表示する場合などに利用する

1. `ListView.separated(...)` で生成したオブジェクトを `Scaffold` オブジェクトの `body` プロパティに設定する方法<br>
  表示する項目と項目の間に区切りをつけることが可能になる。ただしリストの件数が固定の場合にのみ利用できる作成方法。

1. `ListView.custom(...)` で生成したオブジェクトを `Scaffold` オブジェクトの `body` プロパティに設定する方法<br>
  「SliverChildDelegate」を追加してカスタマイズできる。

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

1. `lib/main.dart` を修正する<br>
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
      @override
      Widget build(BuildContext context) {
        return Scaffold(
          appBar: AppBar(
            title: Text(widget.title),
          ),
          // `ListView()` オブジェクトを `Scaffold` オブジェクトの `body` プロパティに設定。リストの内容が予めわかっている場合に使用する
          body: ListView.builder(
            // リスト数
            itemCount: 10,
            // itemBuilder プロパティで、リストの Widget を設定する
            itemBuilder: (BuildContext context, int index) {
              return Container(
                color: Colors.blue,
                margin: EdgeInsets.fromLTRB(10, 10, 10, 10),
                child: Center(
                  child: Text(
                    "List" + index.toString(),
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.white,
                    ),
                  ),
                ),
              );
            }
          )
        );
      }
    }
    ```

    <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/154783753-127f3f85-9fec-478d-ac60-cf19724a7c9b.png">


    ポイントは、以下の通り

    - `ListView.builder(...)` で生成したオブジェクトを `Scaffold` オブジェクトの `body` プロパティに設定するしている。リストの内容が予めわかっていない場合に使用できる。

    - `itemCount` プロパティで、リスト数を指定する。

    - `itemBuilder` プロパティで、グリッドの Widget を設定する。<br>
      ここでは例として、青色の Container に "ListX" のテキストを描く Widget を設定して return している。このとき無名関数 `(BuildContext context, int index) {...}` の `index` には、`itemCount` プロパティで指定したリスト数まで繰り返し index 値が入る

1. 作成したプロジェクトのアプリをエミュレータで実行する<br>
    - CLI コマンドを使用する場合<br>
      以下の CLI コマンドを実行することでアプリを実行できる。

      ```sh
      $ cd ${PROJECT_NAME}
      $ flutter run
      ```

    - VSCode を使用する場合<br>
      VSCode の「実行 > デバッグ > Dart & Flutter」ボタンをクリックすると Chrome 上でアプリが実行される。

## ■ 参考サイト

- https://flutter.ctrnost.com/basic/layout/listview/