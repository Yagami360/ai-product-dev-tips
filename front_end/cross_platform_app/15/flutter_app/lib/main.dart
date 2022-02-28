import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';      // For Firebase
import 'package:cloud_firestore/cloud_firestore.dart';  // For Firestore

//import "package:intl/intl.dart";
//import 'package:intl/date_symbol_data_local.dart';

// main 関数を非同期関数にする
Future<void> main() async {
  // Firebase.initializeApp() する前に必要な処理。この処理を行わないと Firebase.initializeApp() 時にエラーがでる
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
  final String collectionName = "todo_database";
  String _todoText = "";

  void onPressedAdd() {
    print("call onPressedAdd()");

    // Firestore のコレクションに自動ドキュメントIDでフィールドを追加する。コレクションがない場合はコレクションも作成する
    FirebaseFirestore.instance.collection(collectionName).add({
      'createdAt': Timestamp.fromDate(DateTime.now()),
      "text": _todoText,
    });
  }

  Widget _buildTodoList(BuildContext context) {
    // StreamBuilder を使用して Firestore のコレクションに更新があった場合に、自動的に再描画する
    return StreamBuilder(
      // Stream に Firestore のコレクションの snapshots を設定
      stream: FirebaseFirestore.instance.collection(collectionName).snapshots(),
      //
      builder: (BuildContext context, AsyncSnapshot<QuerySnapshot> snapshot) {
        // エラーの場合
        if (snapshot.hasError) {
          return Text('Error: ${snapshot.error}');
        }
        else if (!snapshot.hasData) {
          return Container();
        }
        else {
          return ListView(
            children: snapshot.data!.docs.map(
              (DocumentSnapshot todoFields) {
                //String createdAtString = todoFields["createdAt"].toString();
                //var formatter = new DateFormat('yyyy/MM/dd(E) HH:mm', "ja_JP");
                //var createdAtString = formatter.format(todoFields["createdAt"]);
                //print(createdAtString);

                return Container(
                    //color: Colors.blue,
                    margin: EdgeInsets.fromLTRB(4, 4, 4, 4),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,  // 中央配置
                      children : [
                        DataTable(
                          columns: [
                            DataColumn(label: Text("text")),
                            DataColumn(label: Text("createdAt")),
                          ],
                          rows: [
                            DataRow(
                              cells: [
                                DataCell(Text(todoFields["text"])),
                                //DataCell(Text(createdAtString)),
                                DataCell(Text("aaa")),
                                
                              ]
                            )
                          ],
                        ),
                        // Database の削除
                        OutlinedButton(
                          onPressed: () { /* ボタンがタップされた時の処理 */ },
                          child: Text('Delete'),
                        ),
                      ],
                    )                    
                  );
              },
            ).toList(),
          );
        }
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Container(
        margin: EdgeInsets.fromLTRB(10, 10, 10, 10),    // マージン（Container外側の余白）
        child : Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              Text(
                'Flutter Firebase App',
              ),
              // Database への追加
              Row(
                mainAxisAlignment: MainAxisAlignment.center,  // 中央配置
                children : [
                  Flexible(
                    child: TextField(
                      enabled: true,
                      onChanged: (value) {
                        _todoText = value;
                      },
                    ),
                  ),
                  OutlinedButton(
                    onPressed: onPressedAdd,
                    child: Text('Add'),
                  ),
                ],
              ),
              // Database の表示
              Text(
                'Firestore Database',
              ),
              _buildTodoList(context),
              /*
              ListView.builder(
                //physics: NeverScrollableScrollPhysics(),
                shrinkWrap: true,
                // リスト数
                itemCount: 10,                
                // itemBuilder プロパティで、リストの Widget を設定する
                itemBuilder: (BuildContext context, int index) {
                  return Container(
                    //color: Colors.blue,
                    margin: EdgeInsets.fromLTRB(10, 10, 10, 10),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,  // 中央配置
                      children : [
                        DataTable(
                          columns: [
                            DataColumn(label: Text("index")),
                            DataColumn(label: Text("text")),
                            DataColumn(label: Text("createdAt")),
                          ],
                          rows: [
                            DataRow(
                              cells: [
                                DataCell(Text('1')),
                                DataCell(Text('aaa')),
                                DataCell(Text('03/01')),
                              ]
                            )
                          ],
                        ),
                        // Database の削除
                        OutlinedButton(
                          onPressed: () { /* ボタンがタップされた時の処理 */ },
                          child: Text('Delete'),
                        ),
                      ],
                    )                    
                  );
                }
              ),
              */
            ],
          ),
        ),
      ),
    );
  }
}
