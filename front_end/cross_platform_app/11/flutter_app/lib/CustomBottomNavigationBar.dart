import 'package:flutter/material.dart';
import 'package:flutter_app/CustomIconTextItem.dart';

class CustomBottomNavigationBar extends StatelessWidget {
  final double height;
  final bool isScrollingReverse;    // 下方向にスクロール中かどうか

  // コンストラクタ
  const CustomBottomNavigationBar({
    Key? key,
    this.height = 40,
    this.isScrollingReverse = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.of(context).size.width;

    // `Container(...)` の代わりに、`AnimatedContainer()` を使用して Conatiner の各種プロパティの内容を段階的（アニメーション的に）に切り替える。
    return AnimatedContainer(
      // duration : アニメーション時間
      duration: const Duration(milliseconds: 200),
      // `height` プロパティの値を、下方向にスクロール中 `isScrollingReverse=true` に半分程度にする。そうすることで、`height` プロパティの値が下方向スクロール時にアニメーション的に変化する
      height: isScrollingReverse ? height/2 + 5 : height,
      color: const Color(0xFFFEEAE6),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            CustomIconTextItem(
              deviceWidth: width,
              icon: Icons.home,
              title: 'Home',
              isScrollingReverse: isScrollingReverse,
            ),
            CustomIconTextItem(
              deviceWidth: width,
              icon: Icons.star,
              title: 'Favorite',
              isScrollingReverse: isScrollingReverse,
            ),
            CustomIconTextItem(
              deviceWidth: width,
              icon: Icons.favorite,
              title: 'Like',
              isScrollingReverse: isScrollingReverse,
            ),
            CustomIconTextItem(
              deviceWidth: width,
              icon: Icons.settings,
              title: 'Menu',
              isScrollingReverse: isScrollingReverse,
            ),
          ],
        ),
      ),
    );
  }
}
