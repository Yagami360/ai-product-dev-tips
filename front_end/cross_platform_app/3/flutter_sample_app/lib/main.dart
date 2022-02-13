import 'package:flutter/material.dart';
import 'package:flutter_sample_app/Page1.dart';

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
      body: Column(children: [
        Text("Hello Flutter Sample App"),
        TextButton(
          onPressed: () => {
            // push() メソッドでスタックに次のページオブジェクトを push することで、「進む」遷移を行う
            Navigator.of(context).push(
              // `push()` メソッドの引数として `MaterialPageRoute` オブジェクトを指定することで、MaterialDesign（Google のデザイン規格）に則ったアニメーションを行う
              // `MaterialPageRoute` の `builder` プロパティに、遷移先のページのオブジェクト（今回の例では `Page1`）を return することで、そのページへのページ遷移を実現できる。
              MaterialPageRoute(builder: (context){
                return Page1();
              })
            );            
          },
          child: Text("進む", style: TextStyle(fontSize: 20))
        )
      ])
    );
  }
}
