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
      // `SliverAppBar` を使用する場合は、`Scaffold` の `appBar` プロパティを使用せず、`body` プロパティに `CustomScrollView` オブジェクトを設定する
      body: CustomScrollView(
        // `CustomScrollView` オブジェクトの `slivers` プロパティ（リスト形式）の１つの要素として `SliverAppBar` のオブジェクトを設定
        slivers: [
          SliverAppBar(
            backgroundColor: Colors.blueAccent.withOpacity(0.3),
            floating: true,         // true の場合は、最上段までスクロールしなくても上スクロール時にヘッダーが表示されるようになる。
            pinned: true,           // true の場合は、ヘッダーを完全に隠すのではなくタイトルの１行文は常に表示する
            snap: false,            // `floating` が true の場合に有効で true の場合は、ヘッダーがスクロールにより部分的に表示されるのではなく、完全に表示する
            expandedHeight: 180,    // ヘッダーの完全表示時の高さ
            toolbarHeight: 60,
            // flexibleSpace : ヘッダーのコンテンツ
            // 通常 `FlexibleSpaceBar` オブジェクトを設定する。そして`FlexibleSpaceBar` オブジェクトの `title` プロパティにヘッダーのタイトルを設定し、`background` にヘッダーの背景画像を設定するといった具合で、ヘッダーのコンテンツを設定する形式になる。
            flexibleSpace: FlexibleSpaceBar(
              title: Text('Flutter Sample App'),
              background: Image.network('https://avatars.githubusercontent.com/u/25688193?v=4', fit: BoxFit.cover),
            )
          ),
          // ヘッダーに各種 Widget を追加したい場合は、`CustomScrollView` オブジェクトの `slivers` プロパティ（リスト形式）に `SliverList` オブジェクトを追加する。
          SliverList(
            // `SliverList` オブジェクトの `delegate` プロパティに追加した Widget を設定する。
            // この際に、ヘッダーにグリッドやリストの Widget を追加したい場合は、`SliverList` オブジェクトの `delegate` プロパティには、`SliverChildBuilderDelegate` オブジェクトを設定し、その引数に各種 Widget を追加していく形式になる。
            // それ以外の各種 Widget を追加したい場合は、`SliverList` オブジェクトの `delegate` プロパティには、`SliverChildListDelegate` オブジェクトを設定し、その引数に各種 Widget を追加していく形式になる。
            delegate: SliverChildListDelegate(
              // `SliverChildListDelegate` オブジェクトの引数に各種 Widget を追加していく
              <Widget>[
                Container(
                  child: Column(
                    children: [
                      Text("Text1", style: TextStyle(fontSize: 64)),
                      Text("Text2", style: TextStyle(fontSize: 64)),
                      Text("Text3", style: TextStyle(fontSize: 64)),
                      Text("Text4", style: TextStyle(fontSize: 64)),
                      Text("Text5", style: TextStyle(fontSize: 64)),
                      Text("Text6", style: TextStyle(fontSize: 64)),
                      Text("Text7", style: TextStyle(fontSize: 64)),
                      Text("Text8", style: TextStyle(fontSize: 64)),
                      Text("Text9", style: TextStyle(fontSize: 64)),
                      Text("Text10", style: TextStyle(fontSize: 64)),
                    ],
                  ),     
                )
              ]
            ),
          ),
        ],
      ),
    );
  }
}
