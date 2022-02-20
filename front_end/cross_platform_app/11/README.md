# 【Flutter】スクロール時に大きさが変わる独自のフッターを作成する

ここでは、[【Flutter】独自のフッターを作成する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/cross_platform_app/10) で作成した独自のフッターをベースに、`ScrollController`, `AnimatedContainer`, `AnimatedOpacity` を使用して、スクロール時に大きさが変わる独自のフッターを作成する。

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
    import 'package:flutter/material.dart';

    class CustomIconTextItem extends StatelessWidget {
      final double deviceWidth;
      final IconData icon;
      final String title;
      final bool isScrollingReverse;    // 下方向にスクロール中かどうか

      // コンストラクタ（required : 必須引数）
      const CustomIconTextItem({
        Key? key,
        required this.deviceWidth,
        required this.icon,
        required this.title,
        this.isScrollingReverse = false,
      }) : super(key: key);
      
      @override
      Widget build(BuildContext context) {
        // SizedBox() : 空白
        return SizedBox(
          width: 0.25 * (deviceWidth - 32),
          // Stack を使用して アイコンとテキストの Widget を重ねる
          child: Stack(
            children: [
              // topCenter にアイコンを配置
              Align(
                alignment: Alignment.topCenter,
                child: Icon(
                  icon,
                  color: const Color(0xFF442C2E),
                  size: 24,
                ),
              ),
              // AnimatedOpacity() を使用して、アニメーション的に Widget の透明度を変化させることで、下方向スクロール時はアイコンのテキストを消去するようにする
              AnimatedOpacity(
                opacity: isScrollingReverse ? 0 : 1,  // 透明度。下方向スクロール中は1、そうでない場合は0
                duration: const Duration(milliseconds: 120),
                curve: Curves.easeInQuart,
                child: Align(
                  alignment: Alignment.bottomCenter,
                  child: Text(title, style: const TextStyle(fontSize: 16),),
                ),
              )
              // bottomCenter にアイコンを配置
              
            ],
          ),
        );
      }
    }
    ```

    ポイントは、以下の通り

    - `SizedBox(...)` でフッターの空白を確保

    - `Stack(...)` を使用して アイコン `Icon(...)` とテキスト `Text(...)` の Widget を重ねて、テキスト付きアイコンを表示できるようにしている。

    - アイコンとテキストの内容は、コンストラクタで指定できるようにしている

    - `AnimatedOpacity()` を使用して、アニメーション的に Widget の透明度を変化させる。具体的には、下方向スクロール時 `isScrollingReverse=true` は、`opacity=1` にして透明にすることで、アイコンのテキストを消去するようにする

1. `lib/CustomBottomNavigationBar.dart` を作成する<br>
    フッターを表示するためのクラスである `CustomBottomNavigationBar` クラスを作成する

    ```dart
    import 'package:flutter/material.dart';
    import 'package:flutter_app/CustomIconTextItem.dart';

    class CustomBottomNavigationBar extends StatelessWidget {
      final double height;
      final bool isScrollingReverse;    // 下方向にスクロール中かどうか

      // コンストラクタ
      const CustomBottomNavigationBar({
        Key? key,
        this.height = 40,
        this.isScrollingReverse = false,
      }) : super(key: key);

      @override
      Widget build(BuildContext context) {
        final width = MediaQuery.of(context).size.width;

        // `Container(...)` の代わりに、`AnimatedContainer()` を使用して Conatiner の各種プロパティの内容を段階的（アニメーション的に）に切り替える。
        return AnimatedContainer(
          // duration : アニメーション時間
          duration: const Duration(milliseconds: 200),
          // `height` プロパティの値を、下方向にスクロール中 `isScrollingReverse=true` に半分程度にする。そうすることで、`height` プロパティの値が下方向スクロール時にアニメーション的に変化する
          height: isScrollingReverse ? height/2 + 5 : height,
          color: const Color(0xFFFEEAE6),
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                CustomIconTextItem(
                  deviceWidth: width,
                  icon: Icons.home,
                  title: 'Home',
                  isScrollingReverse: isScrollingReverse,
                ),
                CustomIconTextItem(
                  deviceWidth: width,
                  icon: Icons.star,
                  title: 'Favorite',
                  isScrollingReverse: isScrollingReverse,
                ),
                CustomIconTextItem(
                  deviceWidth: width,
                  icon: Icons.favorite,
                  title: 'Like',
                  isScrollingReverse: isScrollingReverse,
                ),
                CustomIconTextItem(
                  deviceWidth: width,
                  icon: Icons.settings,
                  title: 'Menu',
                  isScrollingReverse: isScrollingReverse,
                ),
              ],
            ),
          ),
        );
      }
    }
    ```

    ポイントは、以下の通り

    - `Container(...)` の代わりに、`AnimatedContainer()` を使用して Conatiner の各種プロパティの内容を段階的（アニメーション的に）に切り替える。具体的には、`height` プロパティの値を、下方向にスクロール中 `isScrollingReverse=true` に半分程度にする。そうすることで、`height` プロパティの値が下方向スクロール時にアニメーション的に変化する

    - `AnimatedContainer(...)` 内に、複数の `CustomIconTextItem` を `Padding(...)` と `Row(...)` の配置で配置する

1. `lib/main.dart` を修正する<br>
    ```dart
    import 'package:flutter/material.dart';
    import 'package:flutter/rendering.dart';    // ScrollDirection を使用するために import
    import 'package:flutter_app/CustomBottomNavigationBar.dart';

    void main() {
      runApp(const MyApp());
    }

    class MyApp extends StatelessWidget {
      const MyApp({Key? key}) : super(key: key);

      // This widget is the root of your application.
      @override
      Widget build(BuildContext context) {
        return MaterialApp(
          title: 'Flutter Demo',
          theme: ThemeData(
            primarySwatch: Colors.blue,
          ),
          home: const MyHomePage(title: 'Flutter Demo Home Page'),
        );
      }
    }

    class MyHomePage extends StatefulWidget {
      const MyHomePage({Key? key, required this.title}) : super(key: key);
      final String title;

      @override
      State<MyHomePage> createState() => _MyHomePageState();
    }

    class _MyHomePageState extends State<MyHomePage> {
      final ScrollController _scrollController = ScrollController();  //  
      bool isScrollingReverse = false;                                // 下方向にスクロール中かどうか

      // スクロールを検知したときに呼ばれるリスナー（コールバック関数）
      void _scrollListener() {
          // 下方向にスクロール中の場合
          if (_scrollController.position.userScrollDirection == ScrollDirection.reverse) {
            isScrollingReverse = true;
          }
          // 上方向にスクロール中の場合
          else {
            isScrollingReverse = false;
          }
          //print('isScrollingReverse : ${isScrollingReverse}');

          // isScrollingReverse は Stateful にしない
          setState(() {});
      }

      // Widget ツリーの初期化を行うタイミングで呼び出されるコールバック関数
      @override
      void initState() {
        super.initState();
        // スクロールを検知したときに処理をしたいリスナー（コールバック関数）を設定
        _scrollController.addListener(_scrollListener);
      }

      @override
      void dispose() {
        _scrollController.dispose();   // ScrollController オブジェクトを dispose() 
        super.dispose();
      }

      @override
      Widget build(BuildContext context) {
        return Scaffold(
          appBar: AppBar(
            title: Text(widget.title),
          ),
          // `Stack()` を使用して、フッダー以外の body 部分（今回の例では `ListView`）とフッダー部分 `CustomBottomNavigationBar(...)` を重ねることで、フッダー以外の body 部分の上にフッダーが表示されるようにする
          body: Stack(
            // Stack の子の要素としては positioned、non-positioned な Widget を設定できる
            children: [
              // Stack の non-positioned な Widget 
              // フッダー以外の body 部分は Stack の `Positioned(...)` を指定せず、スクロール時にフッダー以外の body 部分はスクロールされるようにする
              ListView.builder(
                // リスト数
                itemCount: 50,
                // itemBuilder プロパティで、リストの Widget を設定する
                itemBuilder: (BuildContext context, int index) {
                  return Container(
                    color: Colors.blue,
                    margin: EdgeInsets.fromLTRB(10, 10, 10, 10),
                    child: Center(
                      child: Text(
                        "List" + index.toString(),
                        style: TextStyle(fontSize: 16, color: Colors.white,),
                      ),
                    ),
                  );
                },
                // controller プロパティに作成した `ScrollController` オブジェクトを割り当てる。
                // こうすることで、`ListView` の表示領域でスクロールしたときに、スクロールを検知できるようにする
                controller: _scrollController,   // 
              ),
              // Stack の子要素は Positioned で Widget の配置位置を指定できる
              // Positioned(...) で CustomBottomNavigationBar() の位置指定することで、スクロールしてもフッダーが表示されたままにする
              Positioned(
                bottom: 0,
                child: CustomBottomNavigationBar(height: 50, isScrollingReverse: isScrollingReverse,),
              ),
            ],
          )
        );
      }
    }
    ```

    ポイントは、以下の通り

    - `Stack()` を使用して、フッダー以外の body 部分（今回の例では `ListView`）とフッダー部分 `CustomBottomNavigationBar(...)` を重ねることで、フッダー以外の body 部分の上にフッダーが表示されるようにする

    - この際に、フッダー以外の body 部分は Stack の `Positioned(...)` を指定せず、フッダー部分の `CustomBottomNavigationBar(...)` に関してのみ Stack の `Positioned(...)` を指定して表示位置を固定することで、スクロール時にフッダー以外の body 部分はスクロールされるが、フッダー部分はスクロールされず固定位置で表示されたままの挙動になる。

    - 下方向スクロールを検知するために、`ScrollController` を使用した以下の処理を行う
      1. `ScrollController` のオブジェクトを作成する。<br>
          この例では、クラスのメンバにて `_scrollController` という変数名で作成している。
      1. `body` プロパティに設定している `ListView` オブジェクトの `controller` に、作成した`ScrollController` のオブジェクトを設定する。<br>
          こうすることで、`ListView` の表示領域でスクロールしたときに、スクロールを検知できるようにする。<br>
      1. `initState()` 内にて、`ScrollController` のオブジェクト の `addListener(コールバック関数名)` メソッドを呼び出し、スクロール検出時のコールバック関数（リスナー）を設定する<br>
          - このメソッド `addListener(...)` の引数には、スクロール検出時のコールバック関数（リスナー）を設定する。今回の場合では、`_scrollListener()` がこれに該当する
      1. スクロール検出時のコールバック関数（リスナー）の中身を実装する。<br>
          今回のケースでは、下方向スクロールのみ検知したいので、`_scrollController.position.userScrollDirection == ScrollDirection.reverse` の条件でこれを検知する。
      1. `dispose()` メソッド呼び出し、`ScrollController` のオブジェクトを破棄する。<br>
          この例では、`_MyHomePageState` クラスの `dispose()` メソッド（＝オブジェクトが Widget ツリーから完全に削除され、2度とビルドされなくなったら呼ばれるコールバック関数）内でこの処理を行っている


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

- https://kwmt27.net/2018/09/03/flutter-scroll/
- https://zenn.dev/kazutxt/books/flutter_practice_introduction/viewer/beginner_animation#animated%E7%B3%BBwidget
