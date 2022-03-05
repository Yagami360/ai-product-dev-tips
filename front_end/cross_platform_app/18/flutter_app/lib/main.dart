import 'package:flutter/material.dart';
import 'dart:io';
import 'package:firebase_core/firebase_core.dart';      // For Firebase
import 'package:firebase_auth/firebase_auth.dart';      // For Firebase Auth
import 'package:google_sign_in/google_sign_in.dart';    // Google アカウントでのログイン機能パッケージ

// main 関数を非同期関数にする
Future<void> main() async {
  // Firebase.initializeApp() する前に必要な処理。この処理を行わないと Firebase.initializeApp() 時にエラーがでる
  WidgetsFlutterBinding.ensureInitialized();

  //-------------------------------
  // Firebase の初期化処理
  //-------------------------------
  // ios/andriod で起動する場合
  await Firebase.initializeApp();

  // Chrome で起動する場合
  /*
  await Firebase.initializeApp(
    options: FirebaseOptions(
      apiKey: "AIzaSyBe2uVN91FHE_d86h5zfdoHvvj2StIl3lo",
      authDomain: "flutter-app-20eec.firebaseapp.com",
      projectId: "flutter-app-20eec",
      storageBucket: "flutter-app-20eec.appspot.com",
      messagingSenderId: "712798902626",
      appId: "1:712798902626:web:920f725cbda10bedccf43b",
      measurementId: "G-1FELNJ9ZQ5",
    ),    
  );
  */

  /*
  print("Platform.isIOS : ${Platform.isIOS}");
  print("Platform.isAndroid : ${Platform.isAndroid}");

  // runApp(...) の前では Platform.isIOS の値は取れない？
  if(Platform.isIOS || Platform.isAndroid ) {
    await Firebase.initializeApp();
  }
  else {
    await Firebase.initializeApp(
      options: FirebaseOptions(
        apiKey: "AIzaSyBe2uVN91FHE_d86h5zfdoHvvj2StIl3lo",
        authDomain: "flutter-app-20eec.firebaseapp.com",
        projectId: "flutter-app-20eec",
        storageBucket: "flutter-app-20eec.appspot.com",
        messagingSenderId: "712798902626",
        appId: "1:712798902626:web:920f725cbda10bedccf43b",
        measurementId: "G-1FELNJ9ZQ5",
      ),    
    );
  }
  */
  
  //-------------------------------
  // アプリを起動
  //-------------------------------
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
  // Google アカウントを取得するために GoogleSignIn(...) オブジェクトを作成する
  static final _googleSignIn = GoogleSignIn(
    scopes: [
      'email',
      'https://www.googleapis.com/auth/contacts.readonly',
    ]
  );

  //
  final _firebaseAuth = FirebaseAuth.instance;

  //-------------------------------------------------------
  // Google アカウントでのログインボタンクリック時のコールバック関数。
  // 内部で非同期関数を呼び出す際に await するので非同期関数で定義する
  //-------------------------------------------------------
  //Future<void> _onPressedLoginWithGoogle() async {
  /*
  void _onPressedLoginWithGoogle() async {
    // GoogleSignIn(...).signIn() を使用して Google アカウントを取得する
    GoogleSignInAccount signinAccount = await _googleSignIn.signIn();
    if (signinAccount == null) return;
    
    // 取得した Google アカウントを元に GoogleSignInAuthentication, AuthCredential で Google 認証を行う
    GoogleSignInAuthentication googlAuth = await signinAccount.authentication;
    final AuthCredential credential = GoogleAuthProvider.credential(
      idToken: googlAuth.idToken,
      accessToken: googlAuth.accessToken,
    );

    // Google認情報を元に Firebase に認証情報を登録し、ログインユーザーを取得する
    User user = (await _firebaseAuth.signInWithCredential(credential)).user;

    //
    if (user != null) {
    }    
  }
  */

  //-------------------------------------------------------
  // ログアウトボタンクリック時のコールバック関数。
  //-------------------------------------------------------
  void _onPressedLogout() {
    _firebaseAuth.signOut();
    _googleSignIn.signOut();
  }

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
              'Hello Flutter App',
            ),
            TextButton(
              // ログインボタンクリック時のコールバック関数
              //onPressed: _onPressedLoginWithGoogle,
              onPressed: () async {
                // GoogleSignIn(...).signIn() を使用して Google アカウントを取得する
                GoogleSignInAccount signinAccount = await _googleSignIn.signIn();
                if (signinAccount == null) return;
                
                // 取得した Google アカウントを元に GoogleSignInAuthentication, AuthCredential で Google 認証を行う
                GoogleSignInAuthentication googlAuth = await signinAccount.authentication;
                final AuthCredential credential = GoogleAuthProvider.credential(
                  idToken: googlAuth.idToken,
                  accessToken: googlAuth.accessToken,
                );

                // Google認情報を元に Firebase に認証情報を登録し、ログインユーザーを取得する
                User user = (await _firebaseAuth.signInWithCredential(credential)).user;
              }
              child: Text("login with Google"),
            ),
            TextButton(
              // ログアウトボタンクリック時のコールバック関数
              onPressed: _onPressedLogout,
              child: Text("logout"),
            ),
          ],
        ),
      ),
    );
  }
}
