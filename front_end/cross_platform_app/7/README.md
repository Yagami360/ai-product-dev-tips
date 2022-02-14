# 【Flutter】SliverAppBar を使用してスクロール時に大きさが変わるヘッダーを作成する

Sliver 系 Widget を使用すれば、スクロール時に挙動を変化させる Widget を簡単に作成することができる。<br>
AppBar に対しての Sliver 系 Widget である SliverAppBar を使用すれば、スクロール時に消えるヘッダーや大きさが変わるヘッダーというように、スクロール時に挙動が変化するヘッダーを簡単に作成することができる。

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
    ```

    ポイントは、以下の通り

    - `SliverAppBar` を使用する場合は、`Scaffold` の `appBar` プロパティを使用せず、`body` プロパティに `CustomScrollView` オブジェクトを設定し、`CustomScrollView` オブジェクトの構成要素として `SliverAppBar` のオブジェクトを設定する形式になる。

    - xxx

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

- https://dev.classmethod.jp/articles/flutter_widget_intro_sliver_app_bar/