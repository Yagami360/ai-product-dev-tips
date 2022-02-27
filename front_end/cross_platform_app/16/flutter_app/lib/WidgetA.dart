import 'package:flutter/material.dart';
import 'package:provider/provider.dart';  // Provider を使用するためのパッケージを追加する

// StatelessWidget として定義する
class WidgetA extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    int count;
    try {
      // Provider.of<int> で祖先 Widget の状態を受け取る
      count = Provider.of<int>(context);
    }
    catch (e) {
      count = 0;
    }
    return Text("$count", style: TextStyle(fontSize: 100));
  }
}
