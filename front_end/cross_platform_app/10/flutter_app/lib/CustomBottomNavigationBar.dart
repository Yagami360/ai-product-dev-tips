import 'package:flutter/material.dart';
import 'package:flutter_app/CustomIconTextItem.dart';

class CustomBottomNavigationBar extends StatelessWidget {
  final double height = 40;

  // コンストラクタ
  const CustomBottomNavigationBar({
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.of(context).size.width;

    return Container(
      height: this.height,
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
            ),
            CustomIconTextItem(
              deviceWidth: width,
              icon: Icons.star,
              title: 'Favorite',
            ),
            CustomIconTextItem(
              deviceWidth: width,
              icon: Icons.favorite,
              title: 'Like',
            ),
            CustomIconTextItem(
              deviceWidth: width,
              icon: Icons.settings,
              title: 'Menu',
            ),
          ],
        ),
      ),
    );
  }
}
