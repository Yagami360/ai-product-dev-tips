import 'package:flutter/material.dart';
import 'package:provider/provider.dart';  // Provider を使用するためのパッケージを追加する
import 'package:flutter_app/Counter.dart';

// StatelessWidget として定義する
class WidgetA extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    int count = 0;
    try {
      // Provider.of<ChangeNotifier を継承した状態管理を行う変数のクラス> で、ChangeNotifier を継承した状態管理を行う変数のクラスで定義した状態を受け取る
      final Counter counter = Provider.of<Counter>(context);
      count = counter.count;
    }
    catch (e) {
      count = 0;
    }
    return Text("$count", style: TextStyle(fontSize: 100));
  }
}
