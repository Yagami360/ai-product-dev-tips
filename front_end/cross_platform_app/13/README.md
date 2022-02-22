# 【Flutter】AnimationController を使用してアニメーションを行う

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
    ```dart
    import 'package:flutter/material.dart';
    ...
    class MyHomePage extends StatefulWidget {
      const MyHomePage({Key? key, required this.title}) : super(key: key);
      final String title;

      @override
      State<MyHomePage> createState() => _MyHomePageState();
    }

    // Dart の構文では、`親クラス名 with クラス名` の構文で Mixin （親クラスに継承元クラスの機能を継承させる機能） を行える
    // with SingleTickerProviderStateMixin とすることで、initState() に this にアクセスできるようになる。
    // この this へのアクセスは、AnimationController(...) の初期化（＝オブジェクト作成）時に、`vsync` プロパティを this に設定する際に必要になる
    class _MyHomePageState extends State<MyHomePage> with SingleTickerProviderStateMixin {
      // Dart の構文では、late 付きで変数宣言することで、変数の初期化処理を後で行える
      // AnimationController(...) の初期化（＝オブジェクト作成）時に、`vsync` プロパティを this に設定する必要があるが、クラスのメンバ宣言時には this は使えないので、初期化処理は this にアクセスできる initState() で初期化処理を行うようにする
      late AnimationController _animationController;

      int _seconds = 15;  // アニメーション遷移時間
      double _value = 0;  // _animationController.value の値の Stateful 変数（指定した Duration の間に、 0.0 から 1.0 までの範囲の数で変化）

      @override
      void initState() {
        super.initState();

        // AnimationController の処理化処理
        // AnimationController(...) の初期化（＝オブジェクト作成）時に、`vsync` プロパティを this に設定する必要があるが、with SingleTickerProviderStateMixin としたことで、initState() に内で this にアクセスできるようになっている
        _animationController = AnimationController(
          vsync: this,                            // this を設定 
          duration: Duration(seconds: _seconds),  // アニメーションの遷移時間
        );

        // AnimationController の値が変化するタイミングで呼び出されるコールバック関数（リスナー）を追加 
        _animationController.addListener(() {
          // _animationController.value の値を Stateful 変数にする
          setState(() {
            // _animationController.value の値は、指定した Duration の間に、 0.0 から 1.0 までの範囲の数で変化する
            _value = _animationController.value;
          });
        });
      }

      @override
      void dispose() {
        _animationController.dispose();
          super.dispose();
      }

      @override
      Widget build(BuildContext context) {
        return Scaffold(
          appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text(
              "_animationController.value : " + _value.toStringAsFixed(2),
              style: const TextStyle(
                fontSize: 21,
              ),
            ),
            const SizedBox(height: 12,),
            CircularProgressIndicator(
              value: _animationController.value,    // CircularProgressIndicator の value プロパティに、_animationController.value を設定することで、アニメーションさせる
              backgroundColor: Colors.grey[300],
            ),
            const SizedBox(height: 12,),
            SizedBox(
              width: 130,
              child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      primary: Colors.grey[300],
                      onPrimary: Colors.black,
                    ),
                    onPressed: _animationController.forward,  // _animationController.forward でアニメーションを再生。_animationController.value の値が 0.0 -> 1.0 に遷移時間かけて変化していく
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: const [
                        Icon(Icons.play_arrow),
                        Text(
                          '再生',
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 12,),
                SizedBox(
                  width: 130,
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      primary: Colors.grey[300],
                      onPrimary: Colors.black,
                    ),
                    onPressed: _animationController.stop,   // _animationController.stop でアニメーションを停止
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Icon(Icons.pause),
                        const Text(
                          '停止',
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 12,),
                SizedBox(
                  width: 130,
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      primary: Colors.grey[300],
                      onPrimary: Colors.black,
                    ),
                    onPressed: _animationController.reset,  // _animationController.stop でアニメーションをリセット（value 0.0 に戻る）
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: const [
                        Icon(Icons.stop),
                        Text(
                          'リセット',
                        ),
                      ],
                    ),
                  ),
                ),            
              ],
            ),
          ),
        );
      }
    }
    ```

    ポイントは、以下の通り

    - `class _MyHomePageState extends State<MyHomePage> with SingleTickerProviderStateMixin` の部分では、Dart 言語の `親クラス名 with クラス名` の構文で Mixin （親クラスに継承元クラスの機能を継承させる機能） を利用しているが、`with SingleTickerProviderStateMixin` とすることで、`initState()` に `this` にアクセスできるようになる。この `this` へのアクセスは、`AnimationController(...)` の初期化（＝オブジェクト作成）時に、`vsync` プロパティを `this` に設定する際に必要になる

    - `AnimationController(...)` の初期化（＝オブジェクト作成）時に、`vsync` プロパティを `this` に設定する際に必要になるが、`with SingleTickerProviderStateMixin` でクラス定義したことで、`initState()` に内で `this` にアクセスできるようになっているので、`AnimationController(...)` の初期化処理（＝オブジェクト作成）を、`initState()` に内にて行う

    - `_animationController.addListener(...)` で、`AnimationController` の値が変化するタイミングで呼び出されるコールバック関数（リスナー）を追加する。今回の例では、`_animationController.value` の値を Stateful 変数 `_value` に設定する。

    - `_animationController.value` の値は、指定した Duration の間に、 0.0 から 1.0 までの範囲の数で変化する

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

- https://nzigen.com/reference/flutter/2018-04-30-animation/