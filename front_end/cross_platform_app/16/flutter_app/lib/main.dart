import 'package:flutter/material.dart';
import 'package:provider/provider.dart';  // Provider を使用するためのパッケージを追加する
import 'package:flutter_app/WidgetA.dart';

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
  int _counter = 0;
  void _incrementCounter() {
    // `setState(...)` で、祖先 Widget の状態 `_counter` の変更を行っている。
    setState(() {
      _counter++;
    });
    print("count:" + _counter.toString());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      // Scaffold の body プロパティに `Provider<状態１の型>.value(状態１, 子Widgetの定義)` で値を渡すことで、子 Widget から祖先 Widget の状態に直接アクセスできるようになる。
      body: Provider<int>.value(
        // 子 Widget に渡す状態
        value: _counter,
        // 子 Widget の定義
        child: Center(
          child: WidgetA(),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: 'Increment',
        child: Icon(Icons.add),
      ),      
    );
  }
}
