import 'package:flutter/material.dart';
import 'package:provider/provider.dart';  // Provider を使用するためのパッケージを追加する
import 'package:flutter_app/Counter.dart';
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
  // ChangeNotifier を継承した状態管理を行う変数のオブジェクトを作成する
  final Counter _counter = Counter();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      // Scaffold の body プロパティに `ChangeNotifierProvider<ChangeNotifier を継承した状態管理を行う変数の型>.value(ChangeNotifier を継承した状態管理を行う変数 子Widgetの定義)` で値を渡すことで、子 Widget から ChangeNotifier を継承した状態管理を行う変数に直接アクセスできるようになる。
      body: ChangeNotifierProvider<Counter>.value(
        // 子 Widget に渡す状態
        value: _counter,
        // 子 Widget の定義
        child: Center(
          child: WidgetA(),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          _counter.incrementCounter();
        },
        tooltip: 'Increment',
        child: Icon(Icons.add),
      ),      
    );
  }
}
