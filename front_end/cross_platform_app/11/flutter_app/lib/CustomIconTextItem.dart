import 'package:flutter/material.dart';

class CustomIconTextItem extends StatelessWidget {
  final double deviceWidth;
  final IconData icon;
  final String title;
  final bool isScrollingReverse;    // 下方向にスクロール中かどうか

  // コンストラクタ（required : 必須引数）
  const CustomIconTextItem({
    Key? key,
    required this.deviceWidth,
    required this.icon,
    required this.title,
    this.isScrollingReverse = false,
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
          // AnimatedOpacity() を使用して、アニメーション的に透明度を変化させることで、下方向スクロール時はアイコンのテキストを消去するようにする
          AnimatedOpacity(
            opacity: isScrollingReverse ? 0 : 1,  // 透明度。下方向スクロール中は1、そうでない場合は0
            duration: const Duration(milliseconds: 120),
            curve: Curves.easeInQuart,
            child: Align(
              alignment: Alignment.bottomCenter,
              child: Text(title, style: const TextStyle(fontSize: 16),),
            ),
          )
          // bottomCenter にアイコンを配置
          
        ],
      ),
    );
  }
}
