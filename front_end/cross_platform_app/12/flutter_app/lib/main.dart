import 'package:flutter/material.dart';

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
