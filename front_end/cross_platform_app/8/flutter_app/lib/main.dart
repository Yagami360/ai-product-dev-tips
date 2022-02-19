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
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      // `ListView()` オブジェクトを `Scaffold` オブジェクトの `body` プロパティに設定。リストの内容が予めわかっている場合に使用する
      body: ListView(
        // リストの各要素は、`ListView(...)` オブジェクトの `children` プロパティにリスト形式 `[...]` で割り当てる
        children: [
          Text("Text1"),
          Text("Text2"),
          Text("Text3"),
          // 画像を左寄せにするための Container
          Container(
            alignment: Alignment.centerLeft,
            child: Column(
              children: [
                Image.network('https://avatars.githubusercontent.com/u/25688193?v=4', width: 128, height: 128),
                const SizedBox(height: 20.0),                                                                       // 空白
                Image.network('https://avatars.githubusercontent.com/u/25688193?v=4', width: 128, height: 128),
                const SizedBox(height: 20.0),                                                                       // 空白
                Image.network('https://avatars.githubusercontent.com/u/25688193?v=4', width: 128, height: 128),
              ],
            ),
          )
        ],
      )
    );
  }
}
