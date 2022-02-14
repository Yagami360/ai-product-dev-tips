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
  // ScrollController のオブジェクトを作成
  // ※ final は、再代入不可の変数を表す Dart 言語の構文
  final ScrollController _scrollController = ScrollController();

  // このクラスのオブジェクトが Widget ツリーから完全に削除され、2度とビルドされなくなったら呼ばれるコールバック関数
  @override
  void dispose() {
    // ScrollController のオブジェクトを dispose
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: GridView.builder(
        // ScrollController のオブジェクトを設定
        controller: _scrollController,
        // グリッドの表示方法の指定。SliverGridDelegateWithFixedCrossAxisCount() を指定した場合は、列の数を基準として表示される
        gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 4,      // 列数
          crossAxisSpacing: 10,   // グリッド間の横スペース
          mainAxisSpacing: 10,    // グリッド間の縦スペース
        ),
        // グリッドの Widget を設定
        itemBuilder: (context, index) => Container(
          color: Colors.blue,
          margin: EdgeInsets.fromLTRB(10, 10, 10, 10),
          child: Center(
            child: Text(
              "Grid" + index.toString(),
              style: TextStyle(
                fontSize: 16,
                color: Colors.white,
              ),
            ),
          ),
        ),
        // グリッド数
        itemCount: 10,
      ),
      // floatingActionButton : 画面右下に表示されるボタン
      floatingActionButton: FloatingActionButton(
        heroTag: '上に戻る',
        onPressed: () {
          // `ScrollController` オブジェクトの `animateTo(...)` メソッドを使用して、指定したスクロール位置までジャンプする。
          _scrollController.animateTo(
            0,    // スクロール位置（ピクセル単位）
            duration: const Duration(milliseconds: 100),
            curve: Curves.easeInQuint,
          );
        },
        child: const Icon(
          Icons.arrow_upward,
          color: Colors.white,
        ),       
      )
    );
  }
}
