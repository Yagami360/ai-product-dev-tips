import 'package:flutter/material.dart';

class CustomIconTextItem extends StatelessWidget {
  final double deviceWidth;
  final IconData icon;
  final String title;

  // コンストラクタ（required : 必須引数）
  const CustomIconTextItem({
    Key? key,
    required this.deviceWidth,
    required this.icon,
    required this.title,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    // SizedBox() : 空白
    return SizedBox(
      width: 0.25 * (deviceWidth - 32),
      // Stack を使用して アイコンとテキストの Widget を重ねる
      child: Stack(
        children: [
          // topCenter にアイコンを配置
          Align(
            alignment: Alignment.topCenter,
            child: Icon(
              icon,
              color: const Color(0xFF442C2E),
              size: 24,
            ),
          ),
          // bottomCenter にアイコンを配置
          Align(
            alignment: Alignment.bottomCenter,
            child: Text(
              title,
              style: const TextStyle(fontSize: 16),
            ),
          ),
        ],
      ),
    );
  }
}
