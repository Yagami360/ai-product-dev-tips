import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';      // For Firebase
import 'package:cloud_firestore/cloud_firestore.dart';  // For Firestore

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
  String _todoText = "";  // Add ボタンクリック時に入力フィールドの値を参照できるように、フィールド変数で定義

  //---------------------------------
  // Add ボタンクリック時のコールバック関数
  //---------------------------------
  void _onPressedAdd() {
    print("call onPressedAdd()");

    // Firestore のコレクションに自動ドキュメントIDでフィールドを追加する。コレクションがない場合はコレクションも作成する
    FirebaseFirestore.instance.collection(collectionName).add({
      'createdAt': Timestamp.fromDate(DateTime.now()),
      "text": _todoText,
    });
  }

  //---------------------------------
  // Delete ボタンクリック時のコールバック関数
  //---------------------------------
  void _onPressedDelete(String docId) {
    print("call onPressedDelete()");

    // 指定したドキュメントID のデータを削除する
    FirebaseFirestore.instance.collection(collectionName).doc(docId).delete();
  }

  //---------------------------------
  // Firestore 内のデータ一覧を表示する Widget を返す関数
  //---------------------------------
  Widget _buildTodoList(BuildContext context) {
    // StreamBuilder を使用して Firestore のコレクションに更新があった場合に、自動的に再描画する
    return StreamBuilder(
      // stream プロパティに入力データとしての Firestore のコレクションの snapshots を設定
      stream: FirebaseFirestore.instance.collection(collectionName).orderBy('createdAt', descending: true).snapshots(),
      // builder プロパティに stream プロパティで設定した入力データを元に出力されるデータが非同期的に入る。出力データは snapshot 引数に格納される
      builder: (BuildContext context, AsyncSnapshot<QuerySnapshot> snapshot) {
        // エラーの場合
        if (snapshot.hasError) {
          return Text('Error: ${snapshot.error}');
        }
        else if (!snapshot.hasData) {
          return Container();
        }
        else {
          // Flexible(ListView(...)) : Column の中で ListView を使う場合、そのまま使うと ListView の大きさが定まらず、エラーが発生する。Flexible を用いると、ListView が Overflow する限界まで広がり、エラーなしで表示できるようになる。
          return Flexible(
            child: ListView(
              // snapshot.data!.docs に各ドキュメントIDのドキュメントデータ全体が格納されているので、これを map(...) で　　Widget に変換したものを ListView の children プロパティに設定する
              // ※ ! は「non-nullableな型にキャスト」することを明示するための Dart 構文
              children: snapshot.data!.docs.map(
                (DocumentSnapshot document) {
                  //print("document: ${document}");
                  //print("document[text]: ${document["text"]}");
                  String createdAtString = document["createdAt"].toDate().toString().split(".")[0];
                  return Container(
                    color: Colors.lightBlue.shade50,
                    margin: EdgeInsets.fromLTRB(2, 2, 2, 2),
                    child: Row(
                      //mainAxisAlignment: MainAxisAlignment.center,  // 中央配置
                      children : [
                        Text(createdAtString, textAlign: TextAlign.center,),
                        Spacer(flex: 1,),         // `Spacer` を使用して、余白を確保する
                        Text(document["text"], textAlign: TextAlign.left ),
                        Spacer(flex: 1,),
                        // Database の削除
                        OutlinedButton(
                          onPressed: () { _onPressedDelete(document.id); },
                          child: Text('Delete'),
                        ),
                      ],
                    )
                  );
                },
              ).toList()
            )
          );
        }
      }
    );
  }

  //---------------------------------
  // build 関数
  //---------------------------------
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Container(
        margin: EdgeInsets.fromLTRB(10, 10, 10, 10),    // マージン（Container外側の余白）
        child : Column(
          children: <Widget>[
            //--------------------------
            // Database への追加 UI
            //--------------------------
            Text(
              'Firestore Database にデータ追加',
              style: TextStyle(
                fontSize: 16,
              ),
            ),
            SizedBox(height: 8,),              
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
                  onPressed: _onPressedAdd,
                  child: Text('Add'),
                ),
              ],
            ),
            SizedBox(height: 20,),
            //--------------------------
            // Database 内容表示 UI
            //--------------------------
            Text(
              'Firestore Database の内容表示',
              style: TextStyle(
                fontSize: 16,
              ),
            ),
            SizedBox(height: 8,),              
            _buildTodoList(context),
          ],
        ),
      ),
    );
  }
}
