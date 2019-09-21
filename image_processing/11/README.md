# 【Python】画像の対象物のアスペクト比を変えないまま adjust する。

## 機械学習の文脈での用途

- 機械学習のタスクにおいては、画像を特定の解像度やアスペクト比に落とし込んで学習を行うことがよくあるが、この際に単純に resize すると対象物のアスペクト比が変わってしまい横長や縦長の形状になってしまう。又、単純に crop すると、対象物が画面端で途切れてしまうことが多々ある。
- そのため、そのようなアスペクト比の変化や画面端での途切れが起こらない adjust 処理スクリプトを部品化しておくと便利である。

## 実現方法

- (A-1) マスク画像を利用せずに、画像の対象物のアスペクト比を変えないまま adjust する。
    1. 元画像の height or width を基準として、aspect 比を保ったまま元画像を resize する。

    ※ この方法では、基準として採用していない height or width への resize が行われないことに注意。
    ```python
    img_org = Image.open( os.path.join(args.in_image_dir, image_name ) )

    # 元画像の height を基準として、aspect を保ったまま resize する。
    aspect_org = float( img_org.size[0] / img_org.size[1] )
    new_width = int( aspect_org * args.height )
    new_height = args.height
    img_org = img_org.resize( (new_width, new_height), Image.LANCZOS )
    img_org.save( os.path.join(args.out_image_dir, image_name.replace(".jpg",".png")) )
    ```

- (A-2) マスク画像を利用せずに、画像の対象物のアスペクト比を変えないまま adjust する。
    1. resize したい (width, height) の画像サイズを持つ、貼り付け先となる空のベース画像を生成する。
    1. 空の画像の中央に、元画像を paste する。
    1. この際に、画像端は境界色か単色で埋め合わせする。

    ※ Pillow では、画像の貼り付け paste() メソッドを使えるので、OpenCV より Pillow を使うほうが簡単に実現出来る。<br>
    ※ この方法では、対象物の画面全体に対する大きさの割合が小さくなってしまうことに注意<br>
    ※ 又、この方法では、resize したい (width, height) の値が、元の対象物のサイズよりも小さい場合、画面端で途切れてしまう。
    ```python
    img_org = Image.open( os.path.join(args.in_image_dir, image_name ) )

    # resize したい (width, height) の画像サイズを持つ、貼り付け先となる空のベース画像を生成する。
    # 画像端は、単色で埋め合わせする。
    if( args.back_ground_color == "black" ):
        img_base = Image.new( "RGB", (args.width, args.height), (0,0,0) )
    elif( args.back_ground_color == "white" ):
        img_base = Image.new( "RGB", (args.width, args.height), (255,255,255) )
    else:
        img_base = Image.new( "RGB", (args.width, args.height), img_org.getpixel((0,0)) )

    # 空の画像の中央に、元画像を paste する。
    x_min = int( (args.width - img_org.size[0])/2  )
    x_max = int( args.width - (args.width - img_org.size[0])/2 )
    y_min = int( (args.height - img_org.size[1])/2  )
    y_max = int( args.height - (args.height - img_org.size[1])/2 )

    img_base.paste( img_org, ( x_min, y_min, x_max, y_max ) )
    img_base.save( os.path.join(args.out_image_dir, image_name.replace(".jpg",".png")) )
    ```

- (A-3) マスク画像を利用せずに、画像の対象物のアスペクト比を変えないまま adjust する。
    上記 (A-1) と (A-2) の組み合わせ手法。

    1. 元画像の width, height の小さいほうを基準として、aspect 比を保ったまま元画像を resize する。
    1. resize したい (width, height) の画像サイズを持つ、貼り付け先となる空のベース画像を生成する。
    1. 空の画像の中央に、元画像を paste する。
    1. この際に、画像端は境界色か単色で埋め合わせする。
    ```python
    img_org = Image.open( os.path.join(args.in_image_dir, image_name ) )

    #-----------------------------------------------
    # 元画像の width, height の小さいほうを基準として、aspect 比を保ったまま元画像を resize する。
    #-----------------------------------------------
    width_org = img_org.size[0]
    height_org = img_org.size[1]
    aspect_org = float( width_org / height_org )

    # 元画像の with, height の小さいほうを基準とする。
    if( width_org < height_org ):
        new_width = int( aspect_org * args.height )
        new_height = args.height
    else:
        new_width = args.width
        new_height = int( (1/aspect_org) * args.width )

    img_org = img_org.resize( (new_width, new_height), Image.LANCZOS )

    #----------------------------------------------
    # resize したい (width, height) の画像サイズを持つ、貼り付け先となる空のベース画像を生成する。
    #----------------------------------------------
    # 画像端は、単色で埋め合わせする。
    if( args.back_ground_color == "black" ):
        img_base = Image.new( "RGB", (args.width, args.height), (0,0,0) )
    elif( args.back_ground_color == "white" ):
        img_base = Image.new( "RGB", (args.width, args.height), (255,255,255) )
    else:
        img_base = Image.new( "RGB", (args.width, args.height), img_org.getpixel((0,0)) )

    #---------------------------------------------
    # 空の画像の中央に、元画像を paste する。
    #---------------------------------------------
    x_min = int( (args.width - img_org.size[0])/2  )
    x_max = int( args.width - (args.width - img_org.size[0])/2 )
    y_min = int( (args.height - img_org.size[1])/2  )
    y_max = int( args.height - (args.height - img_org.size[1])/2 )

    if( x_min < 0 or x_max > args.width ):
        x_min = 0
        x_max = args.width - 1

    if( y_min < 0 or y_max > args.height ):
        y_min = 0
        y_max = args.height - 1

    
    img_base.paste( img_org, ( x_min, y_min, x_max, y_max ) )
    img_base.save( os.path.join(args.out_image_dir, image_name.replace(".jpg",".png")) )
    ```

- (B) マスク画像を利用して、adjust する。
    上記 (A) の方法では、対象物の画面全体に対する大きさの割合が小さくなってしまう問題があるので、マスク画像やセグメンテーション画像の短形から、adjust する方法のほうが望ましい。

    1. マスク画像を囲む短形座標を取得する。
    1. xxx

## 入出力データ

- 入力データ (620x420)<br>
    ![messi](https://user-images.githubusercontent.com/25688193/65367017-73daba00-dc66-11e9-84f8-945a92c35e8c.png)<br>

- 手法 (A-1) での出力データ
    - 512 x 512<br>
        ![A-1_messi](https://user-images.githubusercontent.com/25688193/65367055-e2b81300-dc66-11e9-9bb2-7640b21e406e.png)
    - 256 x 256<br>
        ![A-1_messi](https://user-images.githubusercontent.com/25688193/65367054-e055b900-dc66-11e9-963b-fa8402c342cf.png)

- 手法 (A-2) での出力データ
    - 512 x 512 : `--back_ground_color white`<br>
        ![A-2_messi](https://user-images.githubusercontent.com/25688193/65367058-e8155d80-dc66-11e9-9102-9134c07fbe6a.png)

    - 512 x 512 : `--back_ground_color border`<br>
        ![messi](https://user-images.githubusercontent.com/25688193/65367564-3b3ede80-dc6e-11e9-9b8f-385c239172f8.png)

    - 256 x 256 : <br>
        ![A-2_messi](https://user-images.githubusercontent.com/25688193/65367057-e51a6d00-dc66-11e9-8a5d-e79d4fe72be7.png)


- 手法 (A-3) での出力データ
    - 512 x 512 : `--back_ground_color white`<br>
        ![A-3_messi](https://user-images.githubusercontent.com/25688193/65367092-40e4f600-dc67-11e9-99f7-f9ba4f22c5b0.png)

    - 256 x 256 : `--back_ground_color white`<br>
        ![A-3_messi](https://user-images.githubusercontent.com/25688193/65367089-3dea0580-dc67-11e9-80e1-ee12df56fe97.png)

    - 256 x 256 : `--back_ground_color border`<br>
        ![messi](https://user-images.githubusercontent.com/25688193/65367566-3f6afc00-dc6e-11e9-8e68-dabbf6773988.png)

- 手法 (B-1) での出力データ