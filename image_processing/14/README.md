# 【Python】 画像の対象物を膨張・収縮させる。

- 参考サイト
    - [【Python/OpenCV】膨張・収縮フィルタ処理（dilate, erode）](https://algorithm.joho.info/programming/python/opencv-dilate-erode-py/)

## 機械学習の文脈での用途

- オクリュージョンが生じているような画像においては、単純に resize で拡大縮小する方法では、うまく狙い通りの拡大縮小が行えないケースが存在する。
- このような画像に対しては、 OpenCV の `cv2.dilate()`, `cv2.erode()` を用いて、膨張収縮させるとうまくいくケースがある。

## 実現方法

- OpenCV の `cv2.dilate()`, `cv2.erode()` では、マスク画像に対して、畳み込みを行うことで膨張収縮を実現している。
- 膨張収縮率は、畳み込み時の畳み込みカーネルで指定できる。
    ```python
    img = cv2.imread("1.png")

    # 画像をグレースケールに変換
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # 畳み込み用カーネルを設定
    kernel_size = 8
    kernel = np.ones(kernel_size, kernel_size), np.uint8)

    # cv2.dilate() でマスク画像を膨張
    img = cv2.dilate(img, kernel)

    cv2.imwrite(os.path.join("1.png", img)
    ```

    ```python
    img = cv2.imread("1.png")

    # 画像をグレースケールに変換
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # 畳み込み用カーネルを設定
    kernel_size = 8
    kernel = np.ones(kernel_size, kernel_size), np.uint8)

    # cv2.erode() でマスク画像を収縮
    img = cv2.erode(img, kernel)
    
    cv2.imwrite(os.path.join("1.png", img)
    ```

## 入出力データ

- 入力データ<br>
    ![mask](https://user-images.githubusercontent.com/25688193/69625975-0a728f80-108b-11ea-980f-46184f5103ae.jpg)<br>

- 出力データ<br>
    - resize<br>

    - 膨張画像<br>
        ![mask](https://user-images.githubusercontent.com/25688193/69625984-0cd4e980-108b-11ea-8c16-ea28baea83ae.png)

    - 収縮画像<br>
        ![mask](https://user-images.githubusercontent.com/25688193/69625990-0fcfda00-108b-11ea-848c-e9629d096ee2.png)
