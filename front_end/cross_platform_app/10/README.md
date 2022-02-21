# 【Flutter】独自のフッターを作成する

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

      // コンストラクタ（required : 必須引数）
      const CustomIconTextItem({
        Key? key,
        required this.deviceWidth,
        required this.icon,
        required this.title,
      }) : super(key: key);
      
      @override
      Widget build(BuildContext context) {
        // SizedBox() でフッターの空白を確保
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
              // bottomCenter にアイコンを配置
              Align(
                alignment: Alignment.bottomCenter,
                child: Text(
                  title,
                  style: const TextStyle(fontSize: 16),
                ),
              ),
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

1. `lib/CustomBottomNavigationBar.dart` を作成する<br>
    フッターを表示するためのクラスである `CustomBottomNavigationBar` クラスを作成する

    ```dart
    import 'package:flutter/material.dart';
    import 'package:flutter_app/CustomIconTextItem.dart';

    class CustomBottomNavigationBar extends StatelessWidget {
      final double height;

      // コンストラクタ
      const CustomBottomNavigationBar({
        Key? key,
        this.height = 40,
      }) : super(key: key);

      @override
      Widget build(BuildContext context) {
        final width = MediaQuery.of(context).size.width;

        return Container(
          height: this.height,
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
                ),
                CustomIconTextItem(
                  deviceWidth: width,
                  icon: Icons.star,
                  title: 'Favorite',
                ),
                CustomIconTextItem(
                  deviceWidth: width,
                  icon: Icons.favorite,
                  title: 'Like',
                ),
                CustomIconTextItem(
                  deviceWidth: width,
                  icon: Icons.settings,
                  title: 'Menu',
                ),
              ],
            ),
          ),
        );
      }
    }
    ```

    ポイントは、以下の通り

    - `Container(...)` 内に、複数の `CustomIconTextItem` を `Padding(...)` と `Row(...)` の配置で配置する

1. `lib/main.dart` を修正する<br>
    ```dart
    import 'package:flutter/material.dart';
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
                        style: TextStyle(
                          fontSize: 16,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  );
                }
              ),
              // Stack の子要素は Positioned で Widget の配置位置を指定できる
              // Positioned(...) で CustomBottomNavigationBar() の位置指定することで、スクロールしてもフッダーが表示されたままにする
              Positioned(
                bottom: 0,
                child: CustomBottomNavigationBar(height: 50,),
              ),
            ],
          )
        );
      }
    }
    ```

    <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/154789150-00ff9a6b-7edf-45f6-8496-92a4028adb30.png">

    ポイントは、以下の通り

    - `Stack()` を使用して、フッダー以外の body 部分（今回の例では `ListView`）とフッダー部分 `CustomBottomNavigationBar(...)` を重ねることで、フッダー以外の body 部分の上にフッダーが表示されるようにする

    - この際に、フッダー以外の body 部分は Stack の `Positioned(...)` を指定せず、フッダー部分の `CustomBottomNavigationBar(...)` に関してのみ Stack の `Positioned(...)` を指定して表示位置を固定することで、スクロール時にフッダー以外の body 部分はスクロールされるが、フッダー部分はスクロールされず固定位置で表示されたままの挙動になる。

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
