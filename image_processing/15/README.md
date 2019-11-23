# 【Python】 dlib で顔の landmark 検出を検出し、画像上に表示する。

## 機械学習の文脈での用途

- 顔が正面を向いているか横を向いているかの判定や２つの顔の向きが一致しているかなどの判定のために、顔の輪郭線の landmark を検出したケースがある。
- このような場合には、dlib で顔の landmark 検出を検出する方法がある。

## 実現方法

- dlib の `dlib.get_frontal_face_detector()` と `dlib.shape_predictor()` を用いて、顔の検出器を生成し、その検出器から顔のランドマークに関する情報を取得していく流れとなる。但し、事前学習済みのモデルが必要となる。
    ```python
    # 検出器と識別器のオブジェクト作成
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat" )

    # 顔検出を行う画像を読み込む
    img = cv2.imread( os.path.join("1.png") )
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # 検出器に画像を渡し、検出結果を取得
    dets = detector(img, 0)

    #
    for i, det in enumerate(dets):
        # 検出範囲の長方形
        height = det.height()
        width = det.width()
        left_x = det.left()
        left_y = det.top()
        right_x = det.right()
        right_y = det.bottom()

        # face の検出
        shape = predictor(img, det)

        face_contours_x = []
        face_contours_y = []
        face_contours_xy = []
        for j in range(1, 17):
            point = shape.part(j)
            face_contours_x.append(point.x)
            face_contours_y.append(point.y)
            face_contours_xy.append((point.x,point.y)) 
    ```

- conda install command
    - `conda install -c menpo dlib`

- 事前学習済みモデルの場所
    - `shape_predictor_68_face_landmarks.dat` : http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
    - その他モデル : https://github.com/davisking/dlib-models#dlib-models

## 入出力データ

- xxx