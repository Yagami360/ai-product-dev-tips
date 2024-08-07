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
      body: ListView.builder(
        // リスト数
        itemCount: 10,
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
      )
    );
  }
}
