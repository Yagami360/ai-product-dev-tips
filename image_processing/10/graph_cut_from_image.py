import numpy as np
import os, argparse
from tqdm import tqdm
from PIL import Image
import cv2

if __name__ == '__main__':
    """
    人物セグメンテーション画像を使用せずに、背景をくり抜く。
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("in_image_dir", type=str)
    parser.add_argument("out_image_dir", type=str)
    parser.add_argument('--binary_threshold', type=int, default=175)
    parser.add_argument('--back_ground_color', choices=['black', 'white', 'green'])
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if not os.path.isdir(args.out_image_dir):
        os.mkdir(args.out_image_dir)

    image_names = sorted( [f for f in os.listdir(args.in_image_dir) if f.endswith(('.jpg','.jpeg','.png','.bmp'))] )

    for image_name in tqdm(image_names):
        img_org = cv2.imread( os.path.join(args.in_image_dir, image_name ) )

        # 人物セグメンテーション画像をグレースケールに変換する。
        img_org_gray = cv2.cvtColor(img_org, cv2.COLOR_BGR2GRAY)

        # 人物セグメンテーション画像をバイナリ化する。
        _, img_org_binary = cv2.threshold( img_org_gray, args.binary_threshold, 255, cv2.THRESH_BINARY )

        # バイナリマスクの輪郭を抽出する。
        contours, hierarchy = cv2.findContours(img_org_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        #_, contours, hierarchy = cv2.findContours(img_org_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        # バイナリマスクの輪郭内部を 白 = (255, 255, 255) で塗りつぶす。
        binary_mask = np.zeros_like(img_org_binary)
        cv2.drawContours(binary_mask, contours, -1, color=(255, 255, 255), thickness=-1)
        cv2.imwrite( os.path.join(args.out_image_dir, "binary_mask_" + image_name), binary_mask )

        # グレースケールのバイナリマスクを RGB の３チャンネルに戻す
        img = cv2.merge((img_org_binary, img_org_binary, img_org_binary))

        # ブレンド式用に 0.0 ~ 1.0f のスケールに変換する。
        img  = img.astype('float32') / 255.0
        img_org = img_org.astype('float32') / 255.0

        # 元画像とバイナリマスク画像をブレンドする。
        if( args.back_ground_color == "black" ):
            back_ground_color = (0.0, 0.0, 0.0)
        elif( args.back_ground_color == "white" ):
            back_ground_color = (1.0, 1.0, 1.0)
        elif( args.back_ground_color == "green" ):
            back_ground_color = (0.0, 1.0, 0.0)
        else:
            back_ground_color = (0.0, 0.0, 0.0)

        masked = (img * img_org) + ((1-img) * back_ground_color )

        # 0 ~255 のスケールに戻す
        masked = (masked * 255).astype('uint8')
        cv2.imwrite( os.path.join(args.out_image_dir, image_name), masked)