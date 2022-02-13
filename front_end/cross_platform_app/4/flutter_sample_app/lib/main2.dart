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
      body: Container(                                  // Container は HTML の <div> 相当
        width: 500,                                     // コンテナの横幅
        height: 300,                                    // コンテナの縦幅
        margin: EdgeInsets.fromLTRB(50, 50, 50, 50),    // マージン（Container外側の余白）
        padding: EdgeInsets.fromLTRB(100, 100, 100, 100),   // パディング（Container内側の余白）
        //color: Colors.blue,                           // コンテナの色
        decoration: BoxDecoration(                      // ボーダーのスタイル。color プロパティと decoration プロパティを同時に指定することはできない
          color: Colors.blue,
          borderRadius: BorderRadius.circular(5.0),
          border: Border.all(
            color: Colors.black,
            width: 3,
          ),
        ),
      )
    );
  }
}
