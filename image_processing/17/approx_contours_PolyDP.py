import numpy as np
import os, argparse
from tqdm import tqdm
import cv2
from PIL import Image

IMG_EXTENSIONS = (
    '.jpg', '.jpeg', '.png', '.ppm', '.bmp', '.pgm', '.tif',
    '.JPG', '.JPEG', '.PNG', '.PPM', '.BMP', '.PGM', '.TIF',
)

if __name__ == '__main__':
    """
    画像の境界輪郭線を直線近似したマスク画像を生成する
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_dir", type=str, default="in_image")
    parser.add_argument("--out_dir", type=str, default="results")
    parser.add_argument('--binary_threshold', type=int, default=200)
    parser.add_argument('--binary_inverse', action='store_true')
    parser.add_argument('--approx_type', choices=['none', 'simple', 'tc89_l1', 'tc89_kcos'], default="simple", help="境界近似点の圧縮方法")
    parser.add_argument('--contour_type', choices=['outer', 'inner', "all_split"], default="outer", help="境界近似の種類")
    parser.add_argument('--epsilon', type=float, default=0.0025, help="境界近似の弧長")
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

        print( "OPenCV version : ", cv2.__version__ )

    if not os.path.isdir(args.out_dir):
        os.mkdir(args.out_dir)

    image_names = sorted( [f for f in os.listdir(args.in_dir) if f.endswith(IMG_EXTENSIONS)] )
    for image_name in tqdm(image_names):
        #-----------------------------------------------------------
        # 入力画像をバイナリマスク化
        #-----------------------------------------------------------
        in_image_full_path = os.path.join(args.in_dir, image_name)
        original_img = cv2.imread(in_image_full_path)

        #-----------------------------------------------------------
        # グレースケールに変換する。
        #-----------------------------------------------------------
        gray_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)

        #-----------------------------------------------------------
        # 元画像のグレースケール画像をバイナリ化する。
        #-----------------------------------------------------------
        if( args.binary_inverse ):
            _, binary_img = cv2.threshold( gray_img, args.binary_threshold, 255, cv2.THRESH_BINARY_INV )
        else:
            _, binary_img = cv2.threshold( gray_img, args.binary_threshold, 255, cv2.THRESH_BINARY )

        #-----------------------------------------------------------
        # バイナリマスクの輪郭を抽出する。
        # [mode 引数]
        #   cv2.RETR_EXTERNAL : 一番外側の輪郭のみ抽出する。
        #   cv2.RETR_LIST : すべての輪郭を抽出するが、階層構造は作成しない。
        #   cv2.RETR_TREE : すべての輪郭を抽出するが、階層構造を作成
        # [method 引数]
        #   cv2.CHAIN_APPROX_NONE : 輪郭上の全点の情報を保持
        #   cv2.CHAIN_APPROX_SIMPLE : 輪郭を圧縮して冗長な点の情報を大きく削除
        #   cv2.CHAIN_APPROX_TC89_L1 : 最適な文だけ冗長な点の情報を削除
        #   cv2.CHAIN_APPROX_TC89_KCOS :
        # [戻り値]
        #   labels : 画像のラベリング結果を保持している二次元配列。配列の要素は、各ピクセルのラベル番号となっている。
        #   contours : オブジェクトの輪郭座標を保持している配列。
        #   hierarchy : オブジェクトの階層構造情報を保持している配列。
        #-----------------------------------------------------------
        if( args.contour_type == "outer" ):
            contour_type = cv2.RETR_EXTERNAL
        else:
            contour_type = cv2.RETR_TREE

        if( args.approx_type == "none" ):
            approx_type = cv2.CHAIN_APPROX_NONE
        elif( args.approx_type == "simple" ):
            approx_type = cv2.CHAIN_APPROX_SIMPLE
        elif( args.approx_type == "tc89_l1" ):
            approx_type = cv2.CHAIN_APPROX_TC89_L1
        elif( args.approx_type == "tc89_kcos" ):
            approx_type = cv2.CHAIN_APPROX_TC89_KCOS
        else:
            NotImplementedError()

        if( int(cv2.__version__.split(".")[0]) >= 4 ):
            contours, hierarchy = cv2.findContours(binary_img, contour_type, approx_type)
        else:
            labels, contours, hierarchy = cv2.findContours(binary_img, contour_type, approx_type)

        if( args.debug ):
            print( "contours : ", len(contours) )
            print( "hierarchy : ", len(hierarchy) )

        #-----------------------------------------------------------
        # cv2.approxPolyDP で輪郭線を近似
        #-----------------------------------------------------------
        if( args.contour_type == "outer" ):
            binary_mask = np.zeros_like(original_img)
            # すべての輪郭で処理
            for i, cnt in enumerate(contours):
                binary_mask = np.zeros_like(original_img)

                # cv2.approxPolyDP で輪郭線を近似
                approx = cv2.approxPolyDP(cnt, args.epsilon * cv2.arcLength(cnt, True), True)

            cv2.drawContours( binary_mask, [approx], -1,color=(255, 255, 255), thickness=-1 )

            # gray scale で保存
            binary_mask = cv2.cvtColor(binary_mask, cv2.COLOR_BGR2GRAY)
            out_image_full_path = os.path.join(args.out_dir, image_name )
            cv2.imwrite( out_image_full_path, binary_mask )

        elif( args.contour_type == "inner" ):
            binary_mask = np.zeros_like(original_img)
            approx = cv2.approxPolyDP(contours[-1], args.epsilon * cv2.arcLength(contours[-1], True), True)
            cv2.drawContours( binary_mask, [approx], -1,color=(255, 255, 255), thickness=-1 )

            # gray scale で保存
            binary_mask = cv2.cvtColor(binary_mask, cv2.COLOR_BGR2GRAY)
            out_image_full_path = os.path.join(args.out_dir, image_name )
            cv2.imwrite( out_image_full_path, binary_mask )

        elif( args.contour_type == "all_split" ):
            # すべての輪郭で処理
            for i, cnt in enumerate(contours):
                binary_mask = np.zeros_like(original_img)

                # cv2.approxPolyDP で輪郭線を近似
                approx = cv2.approxPolyDP(cnt, args.epsilon * cv2.arcLength(cnt, True), True)

                # 輪郭内部を白で塗りつぶし
                cv2.drawContours(
                    binary_mask,            #
                    [approx],               #
                    -1,                     # 表示する輪郭 : 全表示 -1 
                    color=(255, 255, 255),  # 塗りつぶし色
                    thickness=-1            # 等高線の太さ
                )

                # gray scale で保存
                binary_mask = cv2.cvtColor(binary_mask, cv2.COLOR_BGR2GRAY)
                out_image_full_path = os.path.join(args.out_dir, image_name.split(".")[0] + "_cnt{}".format(i) + ".png" )
                cv2.imwrite( out_image_full_path, binary_mask )
        else:
            NotImplementedError()