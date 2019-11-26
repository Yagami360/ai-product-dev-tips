# 【Python】 人物画像の特定の対象物のみを膨張・収縮させる。

- 参考サイト
    - [【Python/OpenCV】膨張・収縮フィルタ処理（dilate, erode）](https://algorithm.joho.info/programming/python/opencv-dilate-erode-py/)

## 機械学習の文脈での用途

- オクリュージョンが生じているような画像においては、単純に resize で拡大縮小する方法では、うまく狙い通りの拡大縮小が行えないケースが存在する。
- このような画像に対しては、 OpenCV の `cv2.dilate()`, `cv2.erode()` を用いて、膨張収縮させるとうまくいくケースがある。

## 実現方法

- xxx

## 入出力データ

- 入力データ<br>
    ![1FI22O00N-L11@8](https://user-images.githubusercontent.com/25688193/69625547-29245680-108a-11ea-9fc0-89bc94eeca76.png)<br>
    ![1FI22O00N-L11@8](https://user-images.githubusercontent.com/25688193/69625607-46f1bb80-108a-11ea-823e-1a95916e0ab1.png)<br>

- 出力データ<br>
    - resize<br>

    - 膨張画像<br>
        ![1FI22O00N-L11@8_cloth_dilate](https://user-images.githubusercontent.com/25688193/69625696-802a2b80-108a-11ea-8ecb-df326f19bbc2.png)<br>
        ![1FI22O00N-L11@8](https://user-images.githubusercontent.com/25688193/69625656-62f55d00-108a-11ea-909c-f5b012080500.png)

    - 収縮画像<br>
