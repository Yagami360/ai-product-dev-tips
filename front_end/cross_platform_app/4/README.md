# 【Flutter】Container を使用して HTML での div 要素のようにアプリ画面の領域を指定する

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
    - パターン１：`child` プロパティなし + `decoration` 指定なしの場合<br>
        ```dart
        import 'package:flutter/material.dart';
        ...

        class _MyHomePageState extends State<MyHomePage> {
          @override
          Widget build(BuildContext context) {
            return Scaffold(
              appBar: AppBar(
                title: Text(widget.title),
              ),
              body: Container(                                  // Container は HTML の <div> 相当
                width: 500,                                     // コンテナの横幅
                height: 300,                                    // コンテナの縦幅
                margin: EdgeInsets.fromLTRB(50, 50, 50, 50),    // マージン（Container外側の余白）
                padding: EdgeInsets.fromLTRB(100, 100, 100, 100),   // パディング（Container内側の余白）
                color: Colors.blue,                           // コンテナの色
              )
            );
          }
        }
        ```
        <img src="https://user-images.githubusercontent.com/25688193/153742839-40252025-6390-4820-9b53-fb60b6972ccc.png" width="800" />


    - パターン２：`child` プロパティなし + `decoration` 指定ありの場合<br>
        ```dart
        import 'package:flutter/material.dart';
        ...

        class _MyHomePageState extends State<MyHomePage> {
          @override
          Widget build(BuildContext context) {
            return Scaffold(
              appBar: AppBar(
                title: Text(widget.title),
              ),
              body: Container(                                  // Container は HTML の <div> 相当
                width: 500,                                     // コンテナの横幅
                height: 300,                                    // コンテナの縦幅
                margin: EdgeInsets.fromLTRB(50, 50, 50, 50),    // マージン（Container外側の余白）
                padding: EdgeInsets.fromLTRB(100, 100, 100, 100),   // パディング（Container内側の余白）
                //color: Colors.blue,                           // コンテナの色
                decoration: BoxDecoration(                      // ボーダーのスタイル。color プロパティと decoration プロパティを同時に指定することはできない
                  color: Colors.blue,
                  borderRadius: BorderRadius.circular(5.0),
                  border: Border.all(
                    color: Colors.black,
                    width: 3,
                  ),
                ),
              )
            );
          }
        }
        ```
        <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/153743378-5e56c468-fe6c-4c23-872c-6032e3b2b0e7.png">

    - パターン３：`child` プロパティあり + `width` 指定なし + `height` 指定なし + `alignment` 指定なし + `decoration` 指定なしの場合<br>
        ```dart
        class _MyHomePageState extends State<MyHomePage> {
          @override
          Widget build(BuildContext context) {
            return Scaffold(
              appBar: AppBar(
                title: Text(widget.title),
              ),
              body: Container(                                  // Container は HTML の <div> 相当
                //width: 500,                                     // コンテナの横幅
                //height: 300,                                    // コンテナの縦幅
                margin: EdgeInsets.fromLTRB(50, 50, 50, 50),    // マージン（Container外側の余白）
                //padding: EdgeInsets.fromLTRB(100, 100, 100, 100),   // パディング（Container内側の余白）
                color: Colors.blue,                           // コンテナの色
                child: Text('child Widget'),                    // Container の子 Widget（１つのみ指定可能）
                //alignment: Alignment.center,                    // child プロパティの位置
              )
            );
          }
        }
        ```
        <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/153743668-d8d323f0-c61e-4df3-8fe7-4366c4498156.png">


    ポイントは、以下の通り。

    - `Container` オブジェクトは、HTML での `<div>` タグのように画面領域指定する Widget であり、以下のプロパティを持つ
      - `width` : コンテナの横幅
      - `height` : コンテナの縦幅
      - `margin` : マージン（Container外側の余白）
      - `padding` : パディング（Container内側の余白）
      - `color` : コンテナの色
      - `decoration` : ボーダーのスタイル。color プロパティと decoration プロパティを同時に指定することはできない。
      - `child` : `Container` の子 Widget（１つのみ指定可能）
      - `alignment` : `child` プロパティの位置

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

- https://flutternyumon.com/how-to-use-container/
- https://qiita.com/alpex/items/4bc43fa873b3be8538d2