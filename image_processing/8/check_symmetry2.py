import os
import argparse
from tqdm import tqdm
import numpy as np
from PIL import Image
import cv2


if __name__ == '__main__':
    """
    画像の左右対称性を検出する。
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("in_image_dir", type=str)
    parser.add_argument("out_image_dir", type=str)
    parser.add_argument('--symmetry_rate_threshold', type=float, default=0.915 )
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if not os.path.isdir(args.out_image_dir):
        os.mkdir(args.out_image_dir)

    image_names = sorted( [f for f in os.listdir(args.in_image_dir) if f.endswith(('.jpg','.jpeg','.png','.gif','.bmp'))] )

    for image_name in tqdm(image_names):
        in_image_full_path = os.path.join(args.in_image_dir, image_name)
        original_img = cv2.imread( in_image_full_path )
        H, W, C = original_img.shape

        if( args.debug ):
            print( "H={},W={},C={}".format(H,W,C) )

        # 1 : y軸を中心に反転（ようするに左右反転）
        flipped_img = cv2.flip(original_img, 1)
        cv2.imwrite( os.path.join(args.out_image_dir, "flipped_img_" + image_name), flipped_img )

        # バイナリマスク値 (0 or 1) なので、0 or 1 のサムで対称性を計算可能（1.0に近いほど対称性が高い）
        symmetry_rate = ( sum(sum(sum(original_img == flipped_img))) ) / H / W / C

        if( symmetry_rate >= args.symmetry_rate_threshold ):
            print("対称画像 : symmetry_rate={}".format(symmetry_rate) )
        else:
            print("非対称画像 : symmetry_rate={}".format(symmetry_rate) )
