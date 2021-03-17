import numpy as np
import os, argparse
from tqdm import tqdm
from PIL import Image
import cv2

if __name__ == '__main__':
    """
    OpenCV の機能を用いて画像のバイナリマスク画像を生成する。
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_image_dir", type=str, default="in_images")
    parser.add_argument("--out_image_dir", type=str, default="out_images")
    parser.add_argument('--binary_threshold', type=int, default=250)
    args = parser.parse_args()

    if not os.path.isdir(args.out_image_dir):
        os.mkdir(args.out_image_dir)

    image_names = sorted( [f for f in os.listdir(args.in_image_dir) if f.endswith(('.jpg','.jpeg','.png','.gif','.bmp'))] )

    for image_name in tqdm(image_names):
        in_image_full_path = os.path.join(args.in_image_dir, image_name)
        original_img = cv2.imread(in_image_full_path)
    
        # グレースケールに変換する。
        gray_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)

        # 元画像のグレースケール画像をバイナリ化する。
        #_, binary_img = cv2.threshold( gray_img, args.binary_threshold, 255, cv2.THRESH_BINARY )
        _, binary_img = cv2.threshold( gray_img, args.binary_threshold, 255, cv2.THRESH_BINARY_INV )

        # バイナリマスクの輪郭を抽出する。
        # [mode 引数]
        #   cv2.RETR_EXTERNAL : 一番外側の輪郭のみ抽出する。
        #   cv2.RETR_LIST : すべての輪郭を抽出するが、階層構造は作成しない。
        # [method 引数]
        #   cv2.CHAIN_APPROX_SIMPLE : 
        #   cv2.CHAIN_APPROX_TC89_KCOS :
        contours, hierarchy = cv2.findContours(binary_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        #_, contours, hierarchy = cv2.findContours(binary_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        #_, contours, hierarchy = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_KCOS)
        #_, contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # バイナリマスクの輪郭内部を 白 = (255, 255, 255) で塗りつぶす。
        binary_mask = np.zeros_like(original_img)
        cv2.drawContours(binary_mask, contours, -1, color=(255, 255, 255), thickness=-1)

        # gray scale で保存
        binary_mask = cv2.cvtColor(binary_mask, cv2.COLOR_BGR2GRAY)
        out_image_full_path = os.path.join(args.out_image_dir, image_name)
        cv2.imwrite( out_image_full_path, binary_mask )