## 【Python】セマンティックセグメンテーション画像の特定のラベル値の部分を抜き取る。

- セマンティックセグメンテーション画像から特定のラベル値の部分を crop するには、以下の方法が考えられるが、この方法では処理に時間がかかる。
    1. 画像の縦横の全ピクセルに対して for ループを回して各ピクセルのラベル値を取得する。
    2. ベースとなる画像に paste することで crop する。
    ```python
    image = cv2.imread( "1.png" )
    height, width = image.shape[0], image.shape[1]

    # crop 先の空の画像
    image_base_np = np.zeros((height, width, 3))
    for i in range(height) :
        for j in range(width):
            label = image[i][j]
            if( all(label == map_name_to_rgb["Background"]) ):
                pass
            elif( all(label == map_name_to_rgb["Face"]) ):
                image_base_np[i][j] = label
            else:
                pass

    cv2.imwrite("1_cropped.png", image_base_np)
    ```
    - もっと効率的な方法はないか？
        - OpenCV の機能にこのような機能はないか？
