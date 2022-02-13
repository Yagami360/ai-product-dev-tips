# 【Flutter】Navigator の `pop()`, `push()` メソッドを使用して画面のページ遷移を行う

Navigator は、Flutter でページ遷移を実装する際に使用する Widget であり、アプリ画面の「進む」「戻る」でのページ遷移を `pop()`, `push()` メソッドでのスタック操作的に実現する事ができる。

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

1. `lib/main.dart` を修正する
    ```dart
    import 'package:flutter/material.dart';
    import 'package:flutter_sample_app/Page1.dart';
    ...

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
          body: Column(children: [
            Text("Hello Flutter Sample App"),
            TextButton(
              onPressed: () => {
                // push() メソッドでスタックに次のページオブジェクトを push することで、「進む」遷移を行う
                Navigator.of(context).push(
                  // `push()` メソッドの引数として `MaterialPageRoute` オブジェクトを指定することで、MaterialDesign（Google のデザイン規格）に則ったアニメーションを行う
                  // `MaterialPageRoute` の `builder` プロパティに、遷移先のページのオブジェクト（今回の例では `Page1`）を return することで、そのページへのページ遷移を実現できる。
                  MaterialPageRoute(builder: (context){
                    return Page1();
                  })
                );
              },
              child: Text("進む", style: TextStyle(fontSize: 20))
            )
          ])
        );
      }
    }
    ```

    ポイントは、以下の通り

    - 今回の例では、`TextButton()` の `onPressed` プロパティにイベントハンドラ（無名関数） `() => {...}` を設定して、アプリ画面の「進む」遷移を行うようにしている。

    - アプリ画面の「進む」遷移は、`Navigator.of(context).push(...)` メソッドを使用して、スタックに次のページオブジェクトを push することで、「進む」遷移を行う。
    
    - この際の `push()` メソッドの引数として `MaterialPageRoute` オブジェクトを指定しているが、これは、遷移時に MaterialDesign（Google のデザイン規格）に則ったアニメーションを行うための指定している。`MaterialPageRoute` を`CupertinoPageRoute` と書き換えれば、iOS風のアニメーションで遷移する。

    - 更に、この `push()` メソッドの引数 `MaterialPageRoute` の `builder` プロパティに、遷移先のページのオブジェクト（今回の例では `Page1`）を return することで、そのページへのページ遷移を実現できる。


1. `lib/Page1.dart` を作成する
    ページ遷移先ページのクラス `lib/Page1.dart` のコードを作成する

    ```dart
    import 'package:flutter/material.dart';

    class Page1 extends StatelessWidget {
      @override
      Widget build(BuildContext context) {
        return Scaffold(
          appBar: AppBar(
            title: Text("Page1"),
          ),
          body: Column(children: [
            Text("Hello Flutter Sample App"),
            TextButton(
              onPressed: () => {
                // pop() メソッドを使用して、スタックから前のページオブジェクトを pop することで、「戻る」遷移を行う
                Navigator.of(context).pop();
              },
              child: Text("戻る", style: TextStyle(fontSize: 20))
            )
          ])
        );
      }
    }
    ```

    ポイントは、以下の通り

    - アプリ画面の「進む」遷移は、`Navigator.of(context).pop(...)` メソッドを使用して、スタックに前のページオブジェクトを pop することで、「戻る」遷移を行う


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

- https://zenn.dev/kazutxt/books/flutter_practice_introduction/viewer/beginner_page#navigator2.0
- https://qiita.com/heavenosk/items/9e43298955a371221393
