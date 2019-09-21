import os
import argparse
from tqdm import tqdm
import cv2
from PIL import Image

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_image_dir', type=str )
    parser.add_argument('in_image_parse_dir', type=str)
    parser.add_argument('out_image_dir', type=str)
    parser.add_argument('--alpha', type=float, default=0.60)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if not os.path.exists(args.out_image_dir):
        os.mkdir(args.out_image_dir)

    image_names = sorted( [f for f in os.listdir(args.in_image_dir) if f.endswith(('.jpg','.jpeg','.png','.bmp'))] )
    for image_name in tqdm(image_names):
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