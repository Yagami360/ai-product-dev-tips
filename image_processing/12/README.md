# 【Python】元画像とセグメンテーション画像をアルファブレンディングで重ねて表示する。

## 機械学習の文脈での用途

- 機械学習のタスクにおいては、元画像のセグメンテーション画像を利用することが多いが、元画像に対してセグメンテーション画像がうまく生成出来ているかを、双方の画像を重ねたもの＋元画像＋セグメンテーション画像を並べて表示させることで確認したいことがよくある。
- そのため、このような処理スクリプトを部品化しておくと便利である。

## 実現方法

- OpenCV の `cv2.addWeighted()` メソッドを用いて、元画像とセグメンテーション画像をアルファブレンディングで重ねて表示する。

    `alpha_blend_image_and_parse.py`<br>
    ```python
    img = cv2.imread( os.path.join(args.in_image_dir, image_name) )
    img_parse = cv2.imread( os.path.join(args.in_image_parse_dir, image_name) )

    # OpenCV の `cv2.addWeighted()` メソッドを用いて、元画像とセグメンテーション画像をアルファブレンディング
    blended_img = cv2.addWeighted( img, args.alpha, img_parse, 1.0 - args.alpha, 0)

    # １枚目：アルファブレンディング画像、２枚目：元画像、３枚目：セグメンテーション画像を並べて表示
    base_img = Image.new( "RGB", (3*img.shape[1], img.shape[0]), (0, 0, 0) ) 
    base_img.paste( Image.fromarray(cv2.cvtColor(blended_img, cv2.COLOR_BGR2RGB)), (0, 0) )
    base_img.paste( Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)), (1*img.shape[1], 0) )
    base_img.paste( Image.fromarray(cv2.cvtColor(img_parse, cv2.COLOR_BGR2RGB)), (2*img.shape[1], 0) )
    base_img.save( os.path.join(args.out_image_dir, image_name) )
    ```

## 入出力データ

- 入力データ
    - 元画像<br>
        ![messi](https://user-images.githubusercontent.com/25688193/65367724-dc2e9900-dc70-11e9-857e-6684ce06925c.png)
    - セグメンテーション画像<br>
        ![messi](https://user-images.githubusercontent.com/25688193/65367725-ddf85c80-dc70-11e9-98aa-5b426ca25d54.png)

- 出力データ（１枚目：アルファブレンディング画像、２枚目：元画像、３枚目：セグメンテーション画像を並べて表示）
    - `--alpha 0.25`<br>
        ![messi](https://user-images.githubusercontent.com/25688193/65367726-e0f34d00-dc70-11e9-967e-2accd43fdfd0.png)

    - `--alpha 0.50`<br>
        ![messi](https://user-images.githubusercontent.com/25688193/65367727-e2bd1080-dc70-11e9-903e-8f0fc14344b7.png)

    - `--alpha 0.75`<br>
        ![messi](https://user-images.githubusercontent.com/25688193/65367728-e51f6a80-dc70-11e9-9584-1f898b3512f1.png)
