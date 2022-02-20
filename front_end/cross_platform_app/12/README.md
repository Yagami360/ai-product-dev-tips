# 【Flutter】ポートレートモード（縦向き）でのレスポンシブデザインを行う

Flutter は、クロスプラットホームアプリ開発に対応した UI フレームワークであり、多種多様な画面サイズを持つデバイス間で同じようなレイアウトで表示するレスポンシブデザインを比較的に容易に実現できる。<br>
ここでは、ポートレートモード（縦向き）のみに対応したレスポンシブデザインの実現方法を記載する。<br>

レスポンシブデバイスのポイントは、以下の通り。

- `Flexible`, `Spacer`, `ConstrainedBox` などを使用して、Widget の明示的なサイズ指定を避け柔軟に配置する。
- `MediaQuery` を使用して画面サイズを取得し、これをサイズを決定するための変数として利用する
- `ConstrainedBox` を使用して、横幅の最大値を柔軟に設定する。
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


1. `lib/main.dart` を修正する<br>
    ```dart
    ```

    ポイントは、以下の通り

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

- xxx