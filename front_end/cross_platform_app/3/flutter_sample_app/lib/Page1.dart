import 'package:flutter/material.dart';

class Page1 extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Page1"),
      ),
      body: Column(children: [
        Text("Hello Flutter Sample App"),
        TextButton(
          onPressed: () => {
            // pop() メソッドを使用して、スタックから前のページオブジェクトを pop することで、「戻る」遷移を行う
            Navigator.of(context).pop();
          },
          child: Text("戻る", style: TextStyle(fontSize: 20))
        )
      ])
    );
  }
}
