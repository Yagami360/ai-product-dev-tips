# 【Python】データオーギュメンションや品質評価のための画像の拡大縮小＆平行移動＆回転

## 機械学習の文脈での用途

- 機械学習のタスクにおいて、手軽なデータオーギュメンション（DA）を目的として、元画像を拡大縮小＆平行移動＆回転した画像を生成して、データをかさ増ししたいケースが存在する。
- 又、グリッド画像などによるモデルの拡大縮小＆平行移動＆回転へのロバスト性評価のために、元画像を拡大縮小＆平行移動＆回転した画像を使用したいケースが多々存在する。
- そのため、このような拡大縮小＆平行移動＆回転スクリプトを部品化しておくと便利である。

## 実現方法

- (A) Pillow で実現する方法
    - 平行移動：<br>
        Pillow の `rotate()` メソッドの `translate` 引数を使用して平行移動する。

        `offset_image_pillow.py`
        ```python
        img_org = Image.open( os.path.join(args.in_image_dir, image_name ) )

        # Pillow の `rotate()` メソッドの `translate` 引数を使用して平行移動する。
        img_offset = img_org.rotate( 0, translate=(offset_width, offset_height) )
        img_offset.save( os.path.join(args.out_image_dir, "offset{}_".format(i) + image_name.replace(".jpg",".png")) )
        ```

    - 回転処理：<br>
        Pillow の `rotate()` メソッドを使用して回転する。
        `rotate_image_pillow.py`
        ```python
        img_org = Image.open( os.path.join(args.in_image_dir, image_name ) )
        # Pillow の `rotate()` メソッドを使用して回転する。
        img_rotate = img_org.rotate(rotate)
        img_rotate.save( os.path.join(args.out_image_dir, "rot{}_".format(i) + image_name.replace(".jpg",".png")) )
        ```

    - 拡大縮小：<br>
        単純に、Pillow の`resize()` メソッドを使っただけでは、対象物のアスペクト比が変わってしまうので、 [「【Python】画像の対象物のアスペクト比を変えないまま adjust する。」](https://github.com/Yagami360/MachineLearning_Tips/tree/master/image_processing/11) で紹介しているものと同様の手法で画像の対象物のアスペクト比を変えないまま adjust する必要がある。<br>

        `scale_image_pillow.py`
        ```python
        ```

- (B) OpenCV で実現する方法

## 入出力データ

- 入力データ<br>
    ![messi](https://user-images.githubusercontent.com/25688193/65373636-11f86f80-dcbb-11e9-825d-88dc6d88a077.png)<br>

- 出力データ<br>
    - 平行移動<br>
        ![offset0_messi](https://user-images.githubusercontent.com/25688193/65373715-d01bf900-dcbb-11e9-985f-3f81f55f880a.png)<br>
        ![offset1_messi](https://user-images.githubusercontent.com/25688193/65373716-d01bf900-dcbb-11e9-9681-c517046dc9c5.png)<br>
        ![offset2_messi](https://user-images.githubusercontent.com/25688193/65373717-d0b48f80-dcbb-11e9-9f39-0d7ee94d60d4.png)<br>
        ![offset3_messi](https://user-images.githubusercontent.com/25688193/65373718-d0b48f80-dcbb-11e9-8a54-df8d1f7021d2.png)<br>
        ![offset4_messi](https://user-images.githubusercontent.com/25688193/65373719-d0b48f80-dcbb-11e9-9b68-58d0d888d317.png)<br>

    - 回転<br>
        ![rot0_messi](https://user-images.githubusercontent.com/25688193/65373701-b5498480-dcbb-11e9-80a6-eb495d73f3bb.png)<br>
        ![rot1_messi](https://user-images.githubusercontent.com/25688193/65373702-b5e21b00-dcbb-11e9-86da-4cddc3625029.png)<br>
        ![rot2_messi](https://user-images.githubusercontent.com/25688193/65373703-b5e21b00-dcbb-11e9-9eff-e72d8c7f2b83.png)<br>
        ![rot3_messi](https://user-images.githubusercontent.com/25688193/65373705-b5e21b00-dcbb-11e9-944b-7d2fb4de7c99.png)<br>
        ![rot4_messi](https://user-images.githubusercontent.com/25688193/65373706-b5e21b00-dcbb-11e9-8884-218dcd718f9c.png)<br>

    - 拡大縮小<br>
        ![scale0_messi](https://user-images.githubusercontent.com/25688193/65373644-2472a900-dcbb-11e9-8c9a-3716e3b9a50e.png)<br>
        ![scale1_messi](https://user-images.githubusercontent.com/25688193/65373645-2472a900-dcbb-11e9-8e65-19a9c5efe8c9.png)<br>
        ![scale2_messi](https://user-images.githubusercontent.com/25688193/65373646-2472a900-dcbb-11e9-834e-091eba7fb673.png)<br>
        ![scale3_messi](https://user-images.githubusercontent.com/25688193/65373647-250b3f80-dcbb-11e9-85ab-47280b4f2d80.png)<br>
        ![scale4_messi](https://user-images.githubusercontent.com/25688193/65373648-250b3f80-dcbb-11e9-92ff-998bc0d07eec.png)<br>
