# 【Flutter】ListView の `ListView(...)` を使用して固定リスト長のリストレイアウトを行う

ListView は直線的に配置されたスクロール可能なリストの Widget である。<br>
ListViewを構築するためには4つの方法があるが、ここでは１つ目の方法を記載する。

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
          body: ListView(
            // リストの各要素は、`ListView(...)` オブジェクトの `children` プロパティにリスト形式 `[...]` で割り当てる
            children: [
              Text("Text1"),
              Text("Text2"),
              Text("Text3"),
              // 画像を左寄せにするための Container
              Container(
                alignment: Alignment.centerLeft,
                child: Column(
                  children: [
                    Image.network('https://avatars.githubusercontent.com/u/25688193?v=4', width: 128, height: 128),
                    const SizedBox(height: 20.0),                                                                       // 空白
                    Image.network('https://avatars.githubusercontent.com/u/25688193?v=4', width: 128, height: 128),
                    const SizedBox(height: 20.0),                                                                       // 空白
                    Image.network('https://avatars.githubusercontent.com/u/25688193?v=4', width: 128, height: 128),
                  ],
                ),
              )
            ],
          )
        );
      }
    }
    ```

    ポイントは、以下の通り

    - `ListView()` オブジェクトを `Scaffold` オブジェクトの `body` プロパティに設定している。リストの内容が予めわかっている場合に使用できる。

    - リストの各要素は、`ListView(...)` オブジェクトの `children` プロパティにリスト形式 `[...]` で割り当てる

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

- https://flutter.ctrnost.com/basic/layout/listview/