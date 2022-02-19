# 【Flutter】スクロール時に大きさが変わる独自のフッターを作成する

ここでは、[【Flutter】独自のフッターを作成する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/cross_platform_app/10) で作成した独自のフッターをベースに、`ScrollController`, `AnimatedContainer`, `Curves` を使用して、スクロール時に大きさが変わる独自のフッターを作成する。

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

1. `lib/CustomIconTextItem.dart` を作成する<br>
    フッターのテキスト付きアイコンを表示するためのクラスである `CustomIconTextItem` クラスを作成する

    ```dart
    ```

    ポイントは、以下の通り

    - `SizedBox(...)` でフッターの空白を確保

    - `Stack(...)` を使用して アイコン `Icon(...)` とテキスト `Text(...)` の Widget を重ねて、テキスト付きアイコンを表示できるようにしている。

    - アイコンとテキストの内容は、コンストラクタで指定できるようにしている

    - xxx

1. `lib/CustomBottomNavigationBar.dart` を作成する<br>
    フッターを表示するためのクラスである `CustomBottomNavigationBar` クラスを作成する

    ```dart
    ```

    ポイントは、以下の通り

    - `Container(...)` 内に、複数の `CustomIconTextItem` を `Padding(...)` と `Row(...)` の配置で配置する

    - xxx

1. `lib/main.dart` を修正する<br>
    ```dart
    ```

    ポイントは、以下の通り

    - `Stack()` を使用して、フッダー以外の body 部分（今回の例では `ListView`）とフッダー部分 `CustomBottomNavigationBar(...)` を重ねることで、フッダー以外の body 部分の上にフッダーが表示されるようにする

    - この際に、フッダー以外の body 部分は Stack の `Positioned(...)` を指定せず、フッダー部分の `CustomBottomNavigationBar(...)` に関してのみ Stack の `Positioned(...)` を指定して表示位置を固定することで、スクロール時にフッダー以外の body 部分はスクロールされるが、フッダー部分はスクロールされず固定位置で表示されたままの挙動になる。

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
