# 【Flutter】ScrollController を使用してスクロール位置を指定した位置に動かす

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
    ...

    class MyHomePage extends StatefulWidget {
      const MyHomePage({Key? key, required this.title}) : super(key: key);
      final String title;

      @override
      State<MyHomePage> createState() => _MyHomePageState();
    }

    class _MyHomePageState extends State<MyHomePage> {
      // ScrollController のオブジェクトを作成
      // ※ final は、再代入不可の変数を表す Dart 言語の構文
      final ScrollController _scrollController = ScrollController();

      // このクラスのオブジェクトが Widget ツリーから完全に削除され、2度とビルドされなくなったら呼ばれるコールバック関数
      @override
      void dispose() {
        // ScrollController のオブジェクトを dispose
        _scrollController.dispose();
        super.dispose();
      }

      @override
      Widget build(BuildContext context) {
        return Scaffold(
          appBar: AppBar(
            title: Text(widget.title),
          ),
          body: GridView.builder(
            // ScrollController のオブジェクトを設定。こうすることで、`GridView` の表示領域に `animateTo(...)` でジャンプできるようになる。
            controller: _scrollController,
            // グリッドの表示方法の指定。SliverGridDelegateWithFixedCrossAxisCount() を指定した場合は、列の数を基準として表示される
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 4,      // 列数
              crossAxisSpacing: 10,   // グリッド間の横スペース
              mainAxisSpacing: 10,    // グリッド間の縦スペース
            ),
            // グリッドの Widget を設定
            itemBuilder: (context, index) => Container(
              color: Colors.blue,
              margin: EdgeInsets.fromLTRB(10, 10, 10, 10),
              child: Center(
                child: Text(
                  "Grid" + index.toString(),
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
            // グリッド数
            itemCount: 10,
          ),
          // floatingActionButton : 画面右下に表示されるボタン
          floatingActionButton: FloatingActionButton(
            heroTag: '上に戻る',
            onPressed: () {
              // `ScrollController` オブジェクトの `animateTo(...)` メソッドを使用して、指定したスクロール位置までジャンプする。
              _scrollController.animateTo(
                0,    // スクロール位置（ピクセル単位）
                duration: const Duration(milliseconds: 100),
                curve: Curves.easeInQuint,
              );
            },
            child: const Icon(
              Icons.arrow_upward,
              color: Colors.white,
            ),       
          )
        );
      }
    }
    ```

    ポイントは、以下の通り

    - ScrollController を使用してスクロール位置を指定した位置に動かすためには、以下の手順で行えば良い<br>
      1. `ScrollController` オブジェクトを作成する。<br>
          この例では、`_MyHomePageState` クラスのフィールド内で `final ScrollController _scrollController = ScrollController();` として作成している。（`final` は、再代入不可の変数を表す Dart 言語の構文）
      1. 作成した `ScrollController` オブジェクトを、`build(...)` メソッドで return する `Scaffold` オブジェクトの `body` プロパティに設定する。<br>
          この例では、グリッド表示を行う `GridView` の `GridView.builder(...)` メソッドの `controller` プロパティに、`ScrollController` オブジェクトを設定している。こうすることで、`GridView` の表示領域に `animateTo(...)` でジャンプできるようになる。

      1. `ScrollController` オブジェクトの `animateTo(...)` メソッドを使用して、指定したスクロール位置までジャンプする。<br>
          この例では、`floatingActionButton` プロパティの `onPressed` イベントハンドラ内にて、`animateTo(...)` を実行することで、画面右下のボタンクリック時に画面最上部までスクロールするようにしている。
      
          > ここで、`animateTo(...)` では移行していることがわかるようなスクロール移動になる。即座にスクロール移動したい場合は `jumpTo(...)` を使用すればよい。

      1. `dispose()` メソッド呼び出し、`ScrollController` のオブジェクトを破棄する。<br>
          この例では、`_MyHomePageState` クラスの `dispose()` メソッド（＝オブジェクトが Widget ツリーから完全に削除され、2度とビルドされなくなったら呼ばれるコールバック関数）内でこの処理を行っている

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

- xxx