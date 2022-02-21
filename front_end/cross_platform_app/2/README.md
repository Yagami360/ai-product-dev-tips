# 【Flutter】`pubspec.yml` でパッケージ管理（ライブラリ管理）を行う

Flutter では、Flutter の CLI コマンドで外部パッケージ（＝ライブラリ）を行うのではなくて、`pubspec.yml` でライブラリの依存関係を編集した後に、`flutter pub get` の CLI コマンドを実行することで外部パッケージのインストールを行うことができる。ただし VSCode の場合は、`pubspec.yml` を編集すると、自動でパッケージの取得が行われるので、`flutter pub get` の CLI コマンドでのインストール作業は不要になる。

## 方法

1. Flutter プロジェクトを作成する。<br>
    - CLI コマンドを使用する場合<br>
      以下の CLI コマンドで Flutter プロジェクトを作成できる。
      ```sh
      # Flutter プロジェクトを作成する
      flutter create -t app --project-name ${PROJECT_NAME} ./${PROJECT_NAME}
      ```

    - VSCode を使用する場合<br>
      VSCode の「表示 > コマンドパレット > Flutter New Application Project」で Flutter プロジェクトを作成できる。

2. `pubspec.yml` を編集する<br>
    `pubspec.yml` の `dependencies` タグに `パッケージ: バージョン` の形式でインストールするパッケージを追加して保存する

    ```yml
    name: flutter_sample_app
    description: A new Flutter project.
    version: 1.0.0+1

    environment:
      sdk: ">=2.16.0 <3.0.0"
    dependencies:
      flutter:
        sdk: flutter
      url_launcher: ^6.0.3  # パッケージ: バージョン の形式でインストールするパッケージを追加（* url_launcher 指定したURLをブラウザを起動するライブラリ）
    ...
    ```

1. ソースコード `*.dart` に import を追加する
    ```dart
    import 'package:url_launcher/url_launcher.dart';
    ...

    class _MyHomePageState extends State<MyHomePage> {
      String url = "https://www.google.co.jp";

      // ボタンクリック時の非同期メソッド
      // Dart 言語では、`_メソッド名` で定義するとプライベートメソッド扱いになる
      // Dart 言語では、`関数名 asuync {...}` の形式で非同期メソッドを定義する
      void _onPressedButton() async{
        // url_launcher パッケージでは、URL を `launch()` メソッドに渡すことで、その URL に合ったアプリケーションが起動できる。
        // ただし、システムによっては、その URL を処理できるアプリケーションが存在しない可能性もある。 このため `canLaunch()` メソッドで処理可能かどうかチェックし、OK の場合のみ `launch()` メソッドを呼ぶようする
        // url_launcher の `launch()`, `canLaunch()` メソッドは非同期メソッドなので、`await` で非同期処理が完了するまで処理を待って次の処理を行うようにする
        if (await canLaunch(url)) {
          await launch(url);
        }
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
            Text("Hello Flutter Sample App"),
            IconButton(
              icon: Icon(Icons.open_in_browser),
              onPressed: _onPressedButton,
            ),
          ]),
        );
      }
    }
    ```

    ポイントは、以下の通り。

    - `import '追加したパッケージのパッケージ';` の形式で追加したパッケージを import して利用可能にする

    - アイコンクリック時のコールバック関数 `_onPressedButton()` を定義し、この内で url_launcher パッケージを使用している。
    
    - Dart 言語では、`_メソッド名` で定義するとプライベートメソッド扱いになる。
    
    - またDart 言語では、`関数名 asuync {...}` の形式で定義すると非同期メソッドを定義する

    - url_launcher パッケージでは、URL を `launch()` メソッドに渡すことで、その URL に合ったアプリケーションが起動できる。

    - ただし、システムによっては、その URL を処理できるアプリケーションが存在しない可能性もある。 このため `canLaunch()` メソッドで処理可能かどうかチェックし、OK の場合のみ `launch()` メソッドを呼ぶようする

    - url_launcher の `launch()`, `canLaunch()` メソッドは非同期メソッドなので、`await` で非同期処理が完了するまで処理を待って次の処理を行うようにする

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

- https://zenn.dev/kazutxt/books/flutter_practice_introduction/viewer/beginner_package

