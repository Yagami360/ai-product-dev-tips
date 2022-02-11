# 【Flutter】`pubspec.yml` でパッケージ管理（ライブラリ管理）を行う

Flutter では、Flutter の CLI コマンドで外部パッケージ（＝ライブラリ）を行うのではなくて、`pubspec.yml` でライブラリの依存関係を編集した後に、`flutter pub get` の CLI コマンドを実行することで外部パッケージのインストールを行うことができる。ただし VSCode の場合は、`pubspec.yml` を編集すると、自動でパッケージの取得が行われるので、`flutter pub get` の CLI コマンドでのインストール作業は不要になる。

## 方法

1. `pubspec.yml` を編集する<br>
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
  ```

