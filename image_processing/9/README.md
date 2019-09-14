# 【Python】画像のバイナリマスク画像を生成する。

- 機械学習の画像処理タスクにおいては、画像のバイナリマスクを用いて元画像の対象領域を認識させるケースが多々存在する。
- そのため、このようなバイナリマスク画像生成スクリプトを部品化しておくと便利である。

- OpenCV の機能を利用したバイナリマスクの生成方法
    1. OpenCV の `cv2.threshold()` メソッドで、元画像をバイナリ化する。
    1. OpenCV の `cv2.findContours()` メソッドで、バイナリマスクの輪郭を抽出する。
    1. OpenCV の `cv2.drawContours()`  メソッドで、バイナリマスクの輪郭内部を塗りつぶす。
    ```python
    parser = argparse.ArgumentParser()
    parser.add_argument('--binary_threshold', type=int, default=175)
    args = parser.parse_args()
    
    # 元画像を読み込み
    original_img = cv2.imread( "1.png" )
    
    # グレースケールに変換する。
    gray_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)

    # 元画像のグレースケール画像をバイナリ化する。
    _, binary_img = cv2.threshold(gray_img, args.binary_threshold, 255, cv2.THRESH_BINARY_INV)

    # バイナリマスクの輪郭を抽出する。
    # [mode 引数]
    #   cv2.RETR_EXTERNAL : 一番外側の輪郭のみ抽出する。
    #   cv2.RETR_LIST : すべての輪郭を抽出するが、階層構造は作成しない。
    # [method 引数]
    #   cv2.CHAIN_APPROX_SIMPLE : 
    #   cv2.CHAIN_APPROX_TC89_KCOS :
    contours, hierarchy = cv2.findContours(binary_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # バイナリマスクの輪郭内部を 白 = (255, 255, 255) で塗りつぶす。
    binary_mask = np.zeros_like(original_img)
    cv2.drawContours(binary_mask, contours, -1, color=(255, 255, 255), thickness=-1)

    # gray scale で保存
    binary_mask = cv2.cvtColor(binary_mask, cv2.COLOR_BGR2GRAY)
    cv2.imwrite( "1_binary_mask.png", binary_mask )
    ```

- 自前実装でのバイナリマスクの生成方法。
    1. xxx
    ```python
    def create_binary_mask( original_image_path ):
        """
        バイナリマスク画像を生成する。（背景色が白になっている必要あり）
        [args]
            original_image_path : [str] 元の画像のパス
        [resturns]
            original_mask : [ndarry] バイナリマスク画像（OpenCV の ndarray）
        """
        img = Image.open(original_image_path).convert('RGB')
        img_array = np.asarray(img)
        H, W, C = img_array.shape
    
        mask_array = np.zeros((H, W), dtype=np.uint8)
        background_color_value = img_array[0, 0, 0]
        print( "background_color_value :", background_color_value )
        assert background_color_value == 246 or background_color_value == 255
        background_color = [background_color_value, background_color_value, background_color_value]
    
        # True → 対象物, False → 背景
        background_region = (img_array[:, :, 0] == background_color[0]) & (img_array[:, :, 1] == background_color[1]) & (img_array[:, :, 2] == background_color[2])

        mask_array[~background_region] = 255
        mask_img = Image.fromarray(mask_array.astype(np.uint8))

        # Pillow -> OpenCV
        original_mask = np.asarray(mask_img)
        return original_mask


    ```
