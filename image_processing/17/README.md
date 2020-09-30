# 【Python】画像の境界輪郭線を滑らかにしたマスク画像を生成する。

- 参考サイト
    - https://axa.biopapyrus.jp/ia/opencv/detect-contours.html
    - xxx

## 実現方法

### 1. マスク画像の輪郭境界線を外側で直線近似する。
- OpenCV の `cv2.findContours`, `cv2.approxPolyDP` を用いて境界を直線近似する

### 2. マスク画像の輪郭境界線を曲線近似する。

### 3. マスク画像の境界線の外側輪郭と内側輪郭の間で近似する。

## 入出力データ

- xxx