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
          // `SliverAppBar` を使用する場合は、`Scaffold` の `appBar` プロパティを使用せず、`body` プロパティに `CustomScrollView` オブジェクトを設定する
          body: CustomScrollView(
            // `CustomScrollView` オブジェクトの `slivers` プロパティ（リスト形式）の１つの要素として `SliverAppBar` のオブジェクトを設定
            slivers: [
              SliverAppBar(
                backgroundColor: Colors.blueAccent.withOpacity(0.3),
                floating: true,         // true の場合は、最上段までスクロールしなくても上スクロール時にヘッダーが表示されるようになる。
                pinned: true,           // true の場合は、ヘッダーを完全に隠すのではなくタイトルの１行文は常に表示する
                snap: false,            // `floating` が true の場合に有効で true の場合は、ヘッダーがスクロールにより部分的に表示されるのではなく、完全に表示する
                expandedHeight: 180,    // ヘッダーの完全表示時の高さ
                toolbarHeight: 60,
                // flexibleSpace : ヘッダーのコンテンツ
                // 通常 `FlexibleSpaceBar` オブジェクトを設定する。そして`FlexibleSpaceBar` オブジェクトの `title` プロパティにヘッダーのタイトルを設定し、`background` にヘッダーの背景画像を設定するといった具合で、ヘッダーのコンテンツを設定する形式になる。
                flexibleSpace: FlexibleSpaceBar(
                  title: Text('Flutter Sample App'),
                  background: Image.network('https://avatars.githubusercontent.com/u/25688193?v=4', fit: BoxFit.cover),
                )
              ),
              // ヘッダーに各種 Widget を追加したい場合は、`CustomScrollView` オブジェクトの `slivers` プロパティ（リスト形式）に `SliverList` オブジェクトを追加する。
              SliverList(
                // `SliverList` オブジェクトの `delegate` プロパティに追加した Widget を設定する。
                // この際に、ヘッダーにグリッドやリストの Widget を追加したい場合は、`SliverList` オブジェクトの `delegate` プロパティには、`SliverChildBuilderDelegate` オブジェクトを設定し、その引数に各種 Widget を追加していく形式になる。
                // それ以外の各種 Widget を追加したい場合は、`SliverList` オブジェクトの `delegate` プロパティには、`SliverChildListDelegate` オブジェクトを設定し、その引数に各種 Widget を追加していく形式になる。
                delegate: SliverChildListDelegate(
                  // `SliverChildListDelegate` オブジェクトの引数に各種 Widget を追加していく
                  <Widget>[
                    Container(
                      child: Column(
                        children: [
                          Text("Text1", style: TextStyle(fontSize: 64)),
                          Text("Text2", style: TextStyle(fontSize: 64)),
                          Text("Text3", style: TextStyle(fontSize: 64)),
                          Text("Text4", style: TextStyle(fontSize: 64)),
                          Text("Text5", style: TextStyle(fontSize: 64)),
                          Text("Text6", style: TextStyle(fontSize: 64)),
                          Text("Text7", style: TextStyle(fontSize: 64)),
                          Text("Text8", style: TextStyle(fontSize: 64)),
                          Text("Text9", style: TextStyle(fontSize: 64)),
                          Text("Text10", style: TextStyle(fontSize: 64)),
                        ],
                      ),     
                    )
                  ]
                ),
              ),
            ],
          ),
        );
      }
    }
    ```

    <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/154053552-a31d66a1-3d9b-4d3c-9cf0-d4c52b5dd94b.png">

    ポイントは、以下の通り

    - `SliverAppBar` を使用する場合は、`Scaffold` の `appBar` プロパティを使用せず、`body` プロパティに `CustomScrollView` オブジェクトを設定し、`CustomScrollView` オブジェクトの `slivers` プロパティ（リスト形式）の１つの要素として `SliverAppBar` のオブジェクトを設定する形式になる。

    - ここで、`SliverAppBar` オブジェクトのプロパティは、以下のようになる。<br>
      - `floating` : true の場合は、最上段までスクロールしなくても上スクロール時にヘッダーが表示されるようになる。<br>
      - `pinned` : true の場合は、ヘッダーを完全に隠すのではなくタイトルの１行文は常に表示する<br>
      - `snap` : `floating` が true の場合に有効で true の場合は、ヘッダーがスクロールにより部分的に表示されるのではなく、完全に表示する<br>
      - `expandedHeight` : ヘッダーの完全表示時の高さ<br>
      - `toolbarHeight` : ヘッダーの部分表示時の高さ<br>
      - `flexibleSpace` : ヘッダーのコンテンツ。<br>
          通常 `FlexibleSpaceBar` オブジェクトを設定する。そして`FlexibleSpaceBar` オブジェクトの `title` プロパティにヘッダーのタイトルを設定し、`background` にヘッダーの背景画像を設定するといった具合で、ヘッダーのコンテンツを設定する形式になる。

    - body に各種 Widget を追加したい場合は、`CustomScrollView` オブジェクトの `slivers` プロパティ（リスト形式）に `SliverList` オブジェクトを追加し、`SliverList` オブジェクトの `delegate` プロパティに追加した Widget を設定する。<br>
      - この際に、ヘッダーにグリッドやリストの Widget を追加したい場合は、`SliverList` オブジェクトの `delegate` プロパティには、`SliverChildBuilderDelegate` オブジェクトを設定し、その引数に各種 Widget を追加していく形式になる。
      - それ以外の各種 Widget を追加したい場合は、`SliverList` オブジェクトの `delegate` プロパティには、`SliverChildListDelegate` オブジェクトを設定し、その引数に各種 Widget を追加していく形式になる。

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

- https://qiita.com/canisterism/items/6ec326e8593425630c1a
- https://dev.classmethod.jp/articles/flutter_widget_intro_sliver_app_bar/
