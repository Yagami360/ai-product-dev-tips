import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

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
        // This is the theme of your application.
        //
        // Try running your application with "flutter run". You'll see the
        // application has a blue toolbar. Then, without quitting the app, try
        // changing the primarySwatch below to Colors.green and then invoke
        // "hot reload" (press "r" in the console where you ran "flutter run",
        // or simply save your changes to "hot reload" in a Flutter IDE).
        // Notice that the counter didn't reset back to zero; the application
        // is not restarted.
        primarySwatch: Colors.blue,
      ),
      home: const MyHomePage(title: 'Flutter Demo Home Page'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({Key? key, required this.title}) : super(key: key);

  // This widget is the home page of your application. It is stateful, meaning
  // that it has a State object (defined below) that contains fields that affect
  // how it looks.

  // This class is the configuration for the state. It holds the values (in this
  // case the title) provided by the parent (in this case the App widget) and
  // used by the build method of the State. Fields in a Widget subclass are
  // always marked "final".

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  String url = "https://www.google.co.jp";

  // ボタンクリック時の非同期メソッド
  // `_メソッド名` で定義するとプライベートメソッド扱いになる
  // Dart 言語では、`関数名 asuync {...}` の形式で非同期メソッドを定義する
  void _onPressedButton() async{
    // url_launcher パッケージでは、URL を `launch()` メソッドに渡すことで、その URL に合ったアプリケーションが起動できる。
    // ただし、システムによっては、その URL を処理できるアプリケーションが存在しない可能性もある。 このため `canLaunch()` メソッドで処理可能かどうかチェックし、OK の場合のみ `launch()` メソッドを呼ぶようする
    // url_launcher の `launch()`, `canLaunch()` メソッドは非同期メソッドなので、`await` で非同期処理が完了するまで処理を待って次の処理を行うようにする
    if (await canLaunch(url)) {
      await launch(url);
    }
  }

  @override
  Widget build(BuildContext context) {
    // This method is rerun every time setState is called, for instance as done
    // by the _incrementCounter method above.
    //
    // The Flutter framework has been optimized to make rerunning build methods
    // fast, so that you can just rebuild anything that needs updating rather
    // than having to individually change instances of widgets.
    return Scaffold(
      appBar: AppBar(
        // Here we take the value from the MyHomePage object that was created by
        // the App.build method, and use it to set our appbar title.
        title: Text(widget.title),
      ),
      body: Column(children: [
        Text("Hello Flutter Sample App"),
        IconButton(
          icon: Icon(Icons.open_in_browser),
          onPressed: _onPressedButton,
        ),
      ]),
    );
  }
}
