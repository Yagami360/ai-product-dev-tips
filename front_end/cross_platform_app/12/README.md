# 【Flutter】ポートレートモード（縦向き）でのレスポンシブデザインを行う

Flutter は、クロスプラットホームアプリ開発に対応した UI フレームワークであり、多種多様な画面サイズを持つデバイス間で同じようなレイアウトで表示するレスポンシブデザインを比較的に容易に実現できる。<br>
ここでは、ポートレートモード（縦向き）のみに対応したレスポンシブデザインの実現方法を記載する。<br>

レスポンシブデバイスのポイントは、以下の通り。

- `Flexible`, `Spacer`, `ConstrainedBox` などを使用して、Widget の明示的なサイズ指定を避け柔軟に配置する。
- `MediaQuery` を使用して画面サイズを取得し、これをサイズを決定するための変数として利用する
- 画面サイズの｛縦幅 + 横幅｝の値に応じて、文字サイズを決定する。

> 異なるデバイス間で表示がうまくいかなくなる原因は、Widget の width や height を、50, 60 といった具体的な数値で決めることが原因になっているので、これらの値を柔軟に指定できるようにする点がポイント

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


1. `lib/main.dart` を作成する<br>

    1. レスポンシブデザインを考慮していないコード<br>
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
              body: Center(
                      child: Column(
                        children: <Widget>[
                          const SizedBox(
                            height: 80,
                          ),
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 50),
                            child: Text(
                              "Flutter is Google's UI toolkit for building beautiful, natively compiled",
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                color: Colors.black,
                                fontSize: 16,
                                height: 1.85,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          const SizedBox(
                            height: 60,
                          ),
                          FlutterLogo(
                            size: 240,
                          ),
                          const SizedBox(
                            height: 60,
                          ),
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 50),
                            child: Text(
                              'Fast Development Paint your app to life in milliseconds with Stateful Hot Reload. Use a rich set of ',
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                color: Colors.black,
                                fontSize: 15,
                                height: 1.85,
                              ),
                            ),
                          ),
                          const SizedBox(
                            height: 60,
                          ),
                          SizedBox(
                            height: 42,
                            width: 300,
                            child: ElevatedButton(
                              style: ElevatedButton.styleFrom(
                                textStyle: const TextStyle(
                                  color: Colors.white,
                                ),
                                primary: Theme.of(context).accentColor,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(4),
                                ),
                              ),
                              onPressed: () {},
                              child: Padding(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 15,
                                ),
                                child: Text(
                                  'get started',
                                  textAlign: TextAlign.center,
                                  style: TextStyle(
                                    fontSize: 15,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(height: 60,),
                        ],
                      ),
                    ),
            );
          }
        }
        ```

        - Chrome で表示した場合<br>
          <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/154937959-a390fd79-5cab-4edd-a263-49b6f1e79fb5.png">

          > ボタンが横に広がりすぎている

        - iPhone 8 Plus で表示した場合<br>
          <img width="200" alt="image" src="https://user-images.githubusercontent.com/25688193/154939299-76823b7a-f57d-442a-a513-35b4025593d4.png">

          > 余白のはみ出しエラーが発生している

        - iPad で表示した場合<br>
          <img width="300" alt="image" src="https://user-images.githubusercontent.com/25688193/154945763-70ef9a5d-a140-4d53-ad39-33b7c9b0c0e8.png">

          > ボタンが横に広がりすぎている

    1. `Spacer` を使用して空白部分のレスポンシブデザインを考慮したコード<br>
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
              body: Center(
                      child: Column(
                        children: <Widget>[
                          // `SizedBox` ではなく `Spacer` を使用して、余白を確保する。`Spacer` では `flex` プロパティを指定することで相対的な余白の大きさを設定できる。
                          //const SizedBox(height: 80,),
                          Spacer(flex: 1,),
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 50),
                            child: Text(
                              "Flutter is Google's UI toolkit for building beautiful, natively compiled",
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                color: Colors.black,
                                fontSize: 16,
                                height: 1.85,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          //const SizedBox(height: 60,),
                          Spacer(flex: 1,),
                          FlutterLogo(
                            size: 240,
                          ),
                          //const SizedBox(height: 60,),
                          Spacer(flex: 1,),
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 50),
                            child: Text(
                              'Fast Development Paint your app to life in milliseconds with Stateful Hot Reload. Use a rich set of ',
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                color: Colors.black,
                                fontSize: 15,
                                height: 1.85,
                              ),
                            ),
                          ),
                          //const SizedBox(height: 60,),
                          Spacer(flex: 1,),                  
                          SizedBox(
                            height: 42,
                            width: 300,
                            child: ElevatedButton(
                              style: ElevatedButton.styleFrom(
                                textStyle: const TextStyle(
                                  color: Colors.white,
                                ),
                                primary: Theme.of(context).accentColor,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(4),
                                ),
                              ),
                              onPressed: () {},
                              child: Padding(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 15,
                                ),
                                child: Text(
                                  'get started',
                                  textAlign: TextAlign.center,
                                  style: TextStyle(
                                    fontSize: 15,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(height: 60,),
                        ],
                      ),
                    ),
            );
          }
        }
        ```

        - Chrome で表示した場合<br>

        - iPhone 8 Plus で表示した場合<br>
            <img width="200" alt="image" src="https://user-images.githubusercontent.com/25688193/154941486-83c53160-2a47-42c0-bff9-e0836845a478.png">

            > 余白のはみ出しエラーが発生しなくなっている

        - iPad で表示した場合<br>

        ポイントは、以下の通り

        - `SizedBox` ではなく `Spacer` を使用して、余白を確保する。`Spacer` では `flex` プロパティを指定することで相対的な余白の大きさを設定できる。


    1. `MediaQuery` を使用して取得した画面サイズからレスポンシブデザインを考慮したコード<br>
        ```dart
        import 'package:flutter/material.dart';
        ...
        class _MyHomePageState extends State<MyHomePage> {
          @override
          Widget build(BuildContext context) {
            // `MediaQuery` を使用してデバイス毎の画面サイズを取得し、これをサイズを決定するための変数として利用する。
            final width = MediaQuery.of(context).size.width;
            final height = MediaQuery.of(context).size.height;

            return Scaffold(
              appBar: AppBar(
                title: Text(widget.title),
              ),
              body: Center(
                      child: Column(
                        children: <Widget>[
                          // `SizedBox` ではなく `Spacer` を使用して、余白を確保する。`Spacer` では `flex` プロパティを指定することで相対的な余白の大きさを設定できる。
                          //const SizedBox(height: 80,),
                          Spacer(flex: 1,),
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 50),
                            child: Text(
                              "Flutter is Google's UI toolkit for building beautiful, natively compiled",
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                color: Colors.black,
                                fontSize: 16,
                                height: 1.85,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          //const SizedBox(height: 60,),
                          Spacer(flex: 1,),
                          FlutterLogo(
                            //size: 240,
                            size: height * 0.3,   // Flutter ロゴのサイズを画面の高さの 0.3 倍にすることで、デバイスの画面サイズに応じて適切な大きさで表示するようにしている。
                          ),
                          //const SizedBox(height: 60,),
                          Spacer(flex: 1,),
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 50),
                            child: Text(
                              'Fast Development Paint your app to life in milliseconds with Stateful Hot Reload. Use a rich set of ',
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                color: Colors.black,
                                fontSize: 15,
                                height: 1.85,
                              ),
                            ),
                          ),
                          //const SizedBox(height: 60,),
                          Spacer(flex: 1,),                  
                          SizedBox(
                            height: 42,
                            width: 300,
                            child: ElevatedButton(
                              style: ElevatedButton.styleFrom(
                                textStyle: const TextStyle(
                                  color: Colors.white,
                                ),
                                primary: Theme.of(context).accentColor,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(4),
                                ),
                              ),
                              onPressed: () {},
                              child: Padding(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 15,
                                ),
                                child: Text(
                                  'get started',
                                  textAlign: TextAlign.center,
                                  style: TextStyle(
                                    fontSize: 15,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(height: 60,),
                        ],
                      ),
                    ),
            );
          }
        }
        ```

        - Chrome で表示した場合<br>

        - iPhone 8 Plus で表示した場合<br>
          <img width="200" alt="image" src="https://user-images.githubusercontent.com/25688193/154946369-b6e88372-1d18-4716-a013-5b8fbe8fba70.png">

        - iPad で表示した場合<br>

          > デバイスの画面サイズに応じて、ロゴの大きさが適切に変化している

        ポイントは、以下の通り

        - `MediaQuery` を使用してデバイス毎の画面サイズを取得し、これをサイズを決定するための変数として利用する。<br>
            この例では、Flutter ロゴのサイズを画面の高さの 0.3 倍にすることで、デバイスの画面サイズに応じて適切な大きさで表示するようにしている。

    1. `ConstrainedBox` を使用してボタンの横幅のレスポンシブデザインを考慮したコード<br>
        ```dart
        import 'package:flutter/material.dart';
        ...
        class _MyHomePageState extends State<MyHomePage> {
          @override
          Widget build(BuildContext context) {
            // `MediaQuery` を使用してデバイス毎の画面サイズを取得し、これをサイズを決定するための変数として利用する。
            final width = MediaQuery.of(context).size.width;
            final height = MediaQuery.of(context).size.height;

            return Scaffold(
              appBar: AppBar(
                title: Text(widget.title),
              ),
              body: Center(
                      child: Column(
                        children: <Widget>[
                          // `SizedBox` ではなく `Spacer` を使用して、余白を確保する。`Spacer` では `flex` プロパティを指定することで相対的な余白の大きさを設定できる。
                          //const SizedBox(height: 80,),
                          Spacer(flex: 1,),
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 50),
                            child: Text(
                              "Flutter is Google's UI toolkit for building beautiful, natively compiled",
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                color: Colors.black,
                                fontSize: 16,
                                height: 1.85,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          //const SizedBox(height: 60,),
                          Spacer(flex: 1,),
                          FlutterLogo(
                            //size: 240,
                            size: height * 0.3,   // Flutter ロゴのサイズを画面の高さの 0.3 倍にすることで、デバイスの画面サイズに応じて適切な大きさで表示するようにしている。
                          ),
                          //const SizedBox(height: 60,),
                          Spacer(flex: 1,),
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 50),
                            child: Text(
                              'Fast Development Paint your app to life in milliseconds with Stateful Hot Reload. Use a rich set of ',
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                color: Colors.black,
                                fontSize: 15,
                                height: 1.85,
                              ),
                            ),
                          ),
                          //const SizedBox(height: 60,),
                          Spacer(flex: 1,),      
                          //SizedBox(
                          //  height: 42,
                          ///  width: 300,
                          // `ConstrainedBox` を使用して、縦横の最大最小値を設定する。
                          ConstrainedBox(
                            constraints: BoxConstraints(maxWidth: 650),   // ここでは、横幅の最大値 `maxWidth` を柔軟に表示できる値（一般的に 650 程度の値）を設定している。
                            child: ElevatedButton(
                              style: ElevatedButton.styleFrom(
                                textStyle: const TextStyle(
                                  color: Colors.white,
                                ),
                                primary: Theme.of(context).accentColor,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(4),
                                ),
                              ),
                              onPressed: () {},
                              child: Padding(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 15,
                                ),
                                child: Text(
                                  'get started',
                                  textAlign: TextAlign.center,
                                  style: TextStyle(
                                    fontSize: 15,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(height: 60,),
                        ],
                      ),
                    ),
            );
          }
        }
        ```

        - Chrome で表示した場合<br>

        - iPhone 8 Plus で表示した場合<br>

        - iPad で表示した場合<br>
          <img width="300" alt="image" src="https://user-images.githubusercontent.com/25688193/154945345-7d6f2618-ec63-4f0e-930d-63163c915e68.png">

          > ボタンの横幅が伸びすぎる問題が解決できている

        ポイントは、以下の通り

        - `ConstrainedBox` を使用して、縦横の最大最小値を設定する。ここでは、横幅の最大値 `maxWidth` を柔軟に表示できる値（一般的に 650 程度の値）を設定している。

    1. `MediaQuery` を使用して取得した画面サイズから文字サイズのレスポンシブデザインを考慮したコード<br>
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
          @override
          Widget build(BuildContext context) {
            // `MediaQuery` を使用してデバイス毎の画面サイズを取得し、これをサイズを決定するための変数として利用する。
            final width = MediaQuery.of(context).size.width;
            final height = MediaQuery.of(context).size.height;

            return Scaffold(
              appBar: AppBar(
                title: Text(widget.title),
              ),
              body: Center(
                      child: Column(
                        children: <Widget>[
                          // `SizedBox` ではなく `Spacer` を使用して、余白を確保する。`Spacer` では `flex` プロパティを指定することで相対的な余白の大きさを設定できる。
                          //const SizedBox(height: 80,),
                          Spacer(flex: 1,),
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 50),
                            child: Text(
                              "Flutter is Google's UI toolkit for building beautiful, natively compiled",
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                color: Colors.black,
                                //fontSize: 16,
                                fontSize: 15 * (height + width) / (926 + 438),    // 文字サイズを｛縦幅＋横幅｝の画面サイズに応じて適切に変化させる
                                height: 1.85,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          //const SizedBox(height: 60,),
                          Spacer(flex: 1,),
                          FlutterLogo(
                            //size: 240,
                            size: height * 0.3,   // Flutter ロゴのサイズを画面の高さの 0.3 倍にすることで、デバイスの画面サイズに応じて適切な大きさで表示するようにしている。
                          ),
                          //const SizedBox(height: 60,),
                          Spacer(flex: 1,),
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 50),
                            child: Text(
                              'Fast Development Paint your app to life in milliseconds with Stateful Hot Reload. Use a rich set of ',
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                color: Colors.black,
                                //fontSize: 15,
                                fontSize: 15 * (height + width) / (926 + 438),    // 文字サイズを｛縦幅＋横幅｝の画面サイズに応じて適切に変化させる
                                height: 1.85,
                              ),
                            ),
                          ),
                          //const SizedBox(height: 60,),
                          Spacer(flex: 1,),      
                          //SizedBox(
                          //  height: 42,
                          ///  width: 300,
                          // `ConstrainedBox` を使用して、縦横の最大最小値を設定する。
                          ConstrainedBox(
                            constraints: BoxConstraints(maxWidth: 650),   // ここでは、横幅の最大値 `maxWidth` を柔軟に表示できる値（一般的に 650 程度の値）を設定している。
                            child: ElevatedButton(
                              style: ElevatedButton.styleFrom(
                                textStyle: const TextStyle(
                                  color: Colors.white,
                                ),
                                primary: Theme.of(context).accentColor,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(4),
                                ),
                              ),
                              onPressed: () {},
                              child: Padding(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 15,
                                ),
                                child: Text(
                                  'get started',
                                  textAlign: TextAlign.center,
                                  style: TextStyle(
                                    //fontSize: 15,
                                    fontSize: 15 * (height + width) / (926 + 438),    // 文字サイズを｛縦幅＋横幅｝の画面サイズに応じて適切に変化させる
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(height: 60,),
                        ],
                      ),
                    ),
            );
          }
        }

        ```

        - Chrome で表示した場合<br>

        - iPhone 8 Plus で表示した場合<br>
            <img width="200" alt="image" src="https://user-images.githubusercontent.com/25688193/154947236-976e2ca6-9e46-41e4-b98a-a53a4f7114b0.png">

        - iPad で表示した場合<br>

        ポイントは、以下の通り

        - `Text` の `style` プロパティに設定した `TextStyle` オブジェクトの `fontSize` の値を、｛縦幅＋横幅｝の画面サイズに応じた値に設定している。<br>
            ここでは、`fontSize: 15 * (height + width) / (926 + 438)` のように、iPhone 12Pro Max の画面サイズ {926, 438} とデバイスの｛縦幅＋横幅｝の画面サイズの比率で変化するように設定している。

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