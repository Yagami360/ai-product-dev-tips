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
            controller: _scrollController,
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
