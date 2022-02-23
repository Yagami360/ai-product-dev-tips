import 'package:flutter/material.dart';
import 'dart:ui';   // FontFeature.tabularFigures() を使用するために import

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

// Dart の構文では、`親クラス名 with クラス名` の構文で Mixin （親クラスに継承元クラスの機能を継承させる機能） を行える
// with SingleTickerProviderStateMixin とすることで、initState() に this にアクセスできるようになる。
// この this へのアクセスは、AnimationController(...) の初期化（＝オブジェクト作成）時に、`vsync` プロパティを this に設定する際に必要になる
class _MyHomePageState extends State<MyHomePage> with SingleTickerProviderStateMixin {
  // Dart の構文では、late 付きで変数宣言することで、変数の初期化処理を後で行える
  // AnimationController(...) の初期化（＝オブジェクト作成）時に、`vsync` プロパティを this に設定する必要があるが、クラスのメンバ宣言時には this は使えないので、初期化処理は this にアクセスできる initState() で初期化処理を行うようにする
  late AnimationController _animationController;

  final int _seconds = 15;  // アニメーション遷移時間
  double _value = 0;        // _animationController.value の値の Stateful 変数（指定した Duration の間に、 0.0 から 1.0 までの範囲の数で変化）

  // 各種変数型に対しての Tween。初期化処理は `initState()` 内で行う
  late Animation<int> _intAnimation;                      // int 値に対しての Tween
  late Animation<double> _doubleAnimation;                // double 値に対しての Tween
  late Animation<Color?> _colorAnimation;                 // color 値に対しての Tween

  @override
  void initState() {
    super.initState();

    //------------------------------------------------------------------------
    // AnimationController の処理化処理
    // AnimationController(...) の初期化（＝オブジェクト作成）時に、`vsync` プロパティを this に設定する必要があるが、with SingleTickerProviderStateMixin としたことで、initState() に内で this にアクセスできるようになっている
    //------------------------------------------------------------------------
    _animationController = AnimationController(
      vsync: this,                            // this を設定 
      duration: Duration(seconds: _seconds),  // アニメーションの遷移時間
    );

    //------------------------------------------------------------------------
    // AnimationController の値が変化するタイミングで呼び出されるコールバック関数（リスナー）を追加 
    //------------------------------------------------------------------------
    _animationController.addListener(() {
      // _animationController.value の値を Stateful 変数にする
      setState(() {
        // _animationController.value の値は、指定した Duration の間に、 0.0 から 1.0 までの範囲の数で変化する
        _value = _animationController.value;
      });
    });

    //------------------------------------------------------------------------
    // AnimationController の `drive(...)` メソッドに Tween オブジェクトを設定する
    // `_integer = IntTween(begin: 0, end: _seconds).animate(_animationController);` のように Tween オブジェクトの `animate(...)` メソッドに、AnimationController を設定する方法でもよい
    //------------------------------------------------------------------------
    _intAnimation = _animationController.drive(
      // IntTween で int 型のアニメーションを設定する
      // _animationController.value の値が 0.0 ~ 1.0 の遷移時に、0 ~ 15 の整数値で遷移するようにする
      IntTween(begin: 0, end: _seconds),
    );

    _doubleAnimation = _animationController
      // CurveTween() の curve プロパティでアニメーションの補間方法（線形補間など）を設定する。CurveTween() を先に設定する必要があることに注意
      .drive(
        CurveTween(
          curve: const Interval(0, 0.5),
        ),
      )
      // Tween() で double 型のアニメーションを設定する
      .drive(
        Tween(begin: 0, end: 10),
      );

    _colorAnimation = _animationController
      .drive(
        CurveTween(
          curve: const Interval(0.3,0.6,),
        ),
      )
      // ColorTween() で color 型のアニメーションを設定する
      .drive(
        ColorTween(
          begin: Colors.red,
          end: Colors.blue,
        ),
      );
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
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
            Text(
              "_animationController.value",
              style: const TextStyle(
                fontSize: 18,
              ),
            ),
            Text(
              _value.toStringAsFixed(2),
              style: const TextStyle(
                fontSize: 21,
                // iPhone では `_value` の数値によって、数値表示の横幅が違うので、そのまま _value の値をアニメーションさせると横ブレが発生する。
                // `FontFeature.tabularFigures()` で等幅フォントにすることで、iPhone 表示で `_value` の値が変化しても、表示が横ブレしなくなる
                fontFeatures: [
                  FontFeature.tabularFigures(),
                ],                
              ),
            ),
            const SizedBox(height: 12,),
            Text(
              "_intAnimation.value",
              style: const TextStyle(
                fontSize: 18,
              ),
            ),
            Text(
              _intAnimation.value.toString(),
              style: const TextStyle(
                fontSize: 21,
                fontFeatures: [
                  FontFeature.tabularFigures(),
                ],                
              ),
            ),
            const SizedBox(height: 12,),
            Text(
              "_doubleAnimation.value",
              style: const TextStyle(
                fontSize: 18,
              ),
            ),
            Text(
              _doubleAnimation.value.toStringAsFixed(2),
              style: const TextStyle(
                fontSize: 21,
                fontFeatures: [
                  FontFeature.tabularFigures(),
                ],                
              ),
            ),
            const SizedBox(height: 12,),
            Text(
              "_colorAnimation.value",
              style: const TextStyle(
                fontSize: 18,
              ),
            ),
            Text(
              _colorAnimation.value.toString(),
              style: const TextStyle(
                fontSize: 12,
                fontFeatures: [
                  FontFeature.tabularFigures(),
                ],                
              ),
            ),
            const SizedBox(height: 12,),
            CircularProgressIndicator(
              value: _animationController.value,    // CircularProgressIndicator の value プロパティに _animationController.value を設定することで、アニメーションさせる
              strokeWidth: _doubleAnimation.value,  // CircularProgressIndicator の strokeWidth プロパティに _doubleAnimation.value を設定することで、インジゲーターの幅を変化させる
              color: _colorAnimation.value,         // CircularProgressIndicator の color プロパティに _colorAnimation.value を設定することで、インジゲーターの色を変化させる
            ),
            const SizedBox(height: 12,),
            SizedBox(
              width: 130,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  primary: Colors.grey[300],
                  onPrimary: Colors.black,
                ),
                onPressed: _animationController.forward,  // _animationController.forward でアニメーションを再生。_animationController.value の値が 0.0 -> 1.0 に遷移時間かけて変化していく
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: const [
                    Icon(Icons.play_arrow),
                    Text(
                      '再生',
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12,),
            SizedBox(
              width: 130,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  primary: Colors.grey[300],
                  onPrimary: Colors.black,
                ),
                onPressed: _animationController.stop,   // _animationController.stop でアニメーションを停止
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Icon(Icons.pause),
                    const Text(
                      '停止',
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12,),
            SizedBox(
              width: 130,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  primary: Colors.grey[300],
                  onPrimary: Colors.black,
                ),
                onPressed: _animationController.reset,  // _animationController.stop でアニメーションをリセット（value 0.0 に戻る）
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: const [
                    Icon(Icons.stop),
                    Text(
                      'リセット',
                    ),
                  ],
                ),
              ),
            ),            
          ],
        ),
      ),
    );
  }
}
