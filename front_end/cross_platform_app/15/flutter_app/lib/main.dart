import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';      // For Firebase
import 'package:cloud_firestore/cloud_firestore.dart';  // For Firestore

// main 関数を非同期関数にする
Future<void> main() async {
  //
  WidgetsFlutterBinding.ensureInitialized();

  // Firebase の初期化処理
  await Firebase.initializeApp();

  // アプリを起動
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
  final String collectionName = "sample_database";

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            const Text(
              'Flutter Firebase App',
            ),
            // Database の表示
            const Text(
              'Firestore Database',
            ),
            DataTable(
              columns: [
                DataColumn(label: Text("name")),
                DataColumn(label: Text("id")),
              ],
              rows: [
                DataRow(
                  cells: [
                    DataCell(Text('yagami')),
                    DataCell(Text('1')),
                  ]
                )
              ],
            )
            // Database への追加
            const Text(
              'Add',
            ),
            // Database の削除
            const Text(
              'Delete',
            ),
          ],
        ),
      ),
    );
  }
}
