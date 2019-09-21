# 【Python】画像の背景部分をくり抜く。（グラフ カット）

## 機械学習の文脈での用途
- 例えば GAN による画像の生成タスクにおいて、対象物以外の背景部分をくり抜いておくと、生成画像の品質向上が見込めるケースが存在する。
- そのため、このような画像の背景抜き取りスクリプトを部品化しておくと便利である。

## 実現方法
画像の背景抜き取りは、以下のような手順で実現出来る。

- (A) 画像のセグメンテーション画像を使用して、グラフカットする方法。
    1. 画像のセグメンテーション画像を生成する。<br>
        画像のセグメンテーション画像を生成するには、例えば、Graphonomy 等のセグメンテーション画像生成モデルを利用すればよい。
    1. セグメンテーション画像をグレースケールに変換する。
    1. セグメンテーション画像のバイナリマスク画像を生成する。
    1. バイナリマスクの輪郭を抽出する。
    1. バイナリマスクの輪郭内部を塗りつぶす。
    1. グレースケールのバイナリマスクを RGB の３チャンネルに戻す。
    1. ブレンド式用に元画像とバイナリマスク画像を 0.0 ~ 1.0f のスケールに変換する。
    1. 元画像とバイナリマスク画像をブレンドする。
    1. 0 ~255 のスケールに戻す。

    `graph_cut_from_image_parse.py`
    ```python

    # 1. 画像のセグメンテーション画像を生成する。
    # 画像のセグメンテーション画像を生成するには、例えば、Graphonomy 等のセグメンテーション画像生成モデルを利用すればよい
    pass

    # 人物セグメンテーション画像をグレースケールに変換する。
    img_parse_gray = cv2.cvtColor(img_parse, cv2.COLOR_BGR2GRAY)

    # 人物セグメンテーション画像をバイナリ化する。
    _, img_parse_binary = cv2.threshold( img_parse_gray, args.binary_threshold, 255, cv2.THRESH_BINARY )

    # バイナリマスクの輪郭を抽出する。
    contours, hierarchy = cv2.findContours(img_parse_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # バイナリマスクの輪郭内部を 白 = (255, 255, 255) で塗りつぶす。
    binary_mask = np.zeros_like(img_parse_binary)
    cv2.drawContours(binary_mask, contours, -1, color=(255, 255, 255), thickness=-1)

    # グレースケールのバイナリマスクを RGB の３チャンネルに戻す
    img_parse = cv2.merge((img_parse_binary, img_parse_binary, img_parse_binary))

    # ブレンド式用に 0.0 ~ 1.0f のスケールに変換する。
    img_parse  = img_parse.astype('float32') / 255.0
    img_org = img_org.astype('float32') / 255.0

    # 元画像とバイナリマスク画像をブレンドする。
    back_ground_color = (1.0,1.0,1.0)
    masked = (img_parse * img_org) + ((1-img_parse) * back_ground_color )

    # 0 ~255 のスケールに戻す
    masked = (masked * 255).astype('uint8')
    cv2.imwrite( os.path.join(args.out_image_dir, image_name), masked)
    ```

- (B) セグメンテーション画像を使用せずに、元画像からグラフカットする方法。<br>
    元画像のバイナリマスク画像をうまく生成できればこの方法でもうまくいく。
    1. 元画像をグレースケールに変換する。
    1. グレースケールの元画像をバイナリ化する。
    1. 以下同様の手順。

    `graph_cut_from_image.py`

## 入出力データ

- 【入力データ】元画像：<br>
    ![messi](https://user-images.githubusercontent.com/25688193/65334339-270ec900-dbfd-11e9-90e3-e188f1baa8e8.png)

- 【入力データ】元画像のセグメンテーション画像：<br>
    ![messi](https://user-images.githubusercontent.com/25688193/65334343-29712300-dbfd-11e9-8599-dab0c5c305b5.png)

- 【中間データ】バイナリマスク画像：<br>
    ![binary_mask_messi](https://user-images.githubusercontent.com/25688193/65334349-2c6c1380-dbfd-11e9-8b83-05147ae1639e.png)

- 【出力データ】背景くり抜き画像（グラフカット画像）
    ![messi](https://user-images.githubusercontent.com/25688193/65334351-2c6c1380-dbfd-11e9-81ab-5b3e7e937f5b.png)
