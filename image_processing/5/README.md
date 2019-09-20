# 【Python】セマンティックセグメンテーション画像からラベル値を取得する。

## 機械学習の文脈での用途

## 実現方法

- セマンティックセグメンテーション画像からラベル値を取得する際は、画像の縦横の全ピクセルに対して for ループを回して、各ピクせルのラベル値を取得する方法もあるが、この方法では処理に時間がかかり非効率的である。
    ```python
    image = cv2.imread( "1.png" )
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)   # グレースケールに変換
    height, width = image.shape[0], image.shape[1]

    n_background = 0
    n_hat = 0
    n_hair = 0
    for i in range(height) :
        for j in range(width):
            label = image[i][j]
            if(label == 0):
                n_background += 1
            elif(label == 1):
                n_hat += 1
            elif(label == 2):
                n_hair += 1
            ...

    print( "n_background :", n_background )
    print( "percent_background :", n_background / (height*width) )
    print( "n_hat :", n_hat )
    print( "n_hair :", n_hair )
    ```

- これに対して以下のコードのような、画像全体に対しての `==` 演算、及び bool 値の行列演算を利用した方法では、圧倒的に高速にセグメンテーションマスク画像のラベル値を検出出来る。
    - 更にこの方法では、画像全体に対しての該当するラベル値の割合を計算できるので、例えば該当するラベル値が画像全体に対して数ピクセルしか含まれないようなノイズを除外することが出来る。
    ```python
    image = cv2.imread( "1.png" )
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)   # グレースケールに変換
    height, width = image.shape[0], image.shape[1]

    # == 演算子で 画像全体を比較
    # 各要素の True -> 対応するピクセルのラベル値が 0 ; True -> 対応するピクセルのラベル値が 0 でない
    b_matrix0 = ( image ==  0 )

    # 行列の True 要素の数の和を取る。この値が該当するラベルの総ピクセル数となる。
    #n_true0 = np.sum( b_matrix0[:,:,0] )   # for RGB
    n_true0 = np.sum( b_matrix0[:,:] )      # for Gray scale

    # 画像全体に対してのラベル値が 0 の割合
    parcent0 = 100 * ( n_true0 / ( height * width ) )

    # ある一定以上の割合で、ラベル 0 が存在する場合
    threshold = 1
    if( parcent0 >= threshold ):
        print( "0 : Background" ) 
    ```

- 又、セグメンテーションマスク画像のラベル値を取得する際には、`dict` 型で、ラベル値とその意味に関してのマップ情報を定義するようにすると便利である。
    ```python
    # Graphonomy のラベル定義
    map_name_to_idx = {
        "Background" : 0,
        "Hat" : 1,
        "Hair" : 2,
        "Glove" : 3,
        "Sunglasses" : 4,
        "UpperClothes" : 5,
        "Dress" : 6,
        "Coat" : 7,
        "Socks" : 8,
        "Pants" : 9,
        "Jumpsuits" : 10,
        "Scarf" : 11,
        "Skirt" : 12,
        "Face" : 13,
        "LeftArm" : 14,
        "RightArm" : 15,
        "LeftLeg" : 16,
        "RightLeg" : 17,
        "LeftShoe" : 18,
        "RightShoe" : 19,
        "RightHand" : 20,
        "LeftHand" : 21,
    }

    image = cv2.imread( "1.png" )
    height, width = image.shape[0], image.shape[1]
    for i in range(height) :
        for j in range(width):
            label = image[i][j]
            # ラベル値ではなく、ラベルの意味で指定できる。
            if(label == map_name_to_idx["Background"] ):
                print( "0 : Background" )
    ```