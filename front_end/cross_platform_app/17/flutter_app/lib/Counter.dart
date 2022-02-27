import 'package:flutter/foundation.dart';

// ChangeNotifier を継承して、状態管理を行う変数のクラスを定義する
class Counter extends ChangeNotifier {
  int count = 0;

  void incrementCounter() {
    count++;
    // notifyListeners() で状態の値が変更したことを知らせる
    notifyListeners();
  }
}
