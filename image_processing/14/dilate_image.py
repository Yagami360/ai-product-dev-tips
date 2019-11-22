import numpy as np
import os, argparse
from tqdm import tqdm
import cv2

if __name__ == '__main__':
    """
    マスク画像を dilate（膨張）する。
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("in_image_dir", type=str)
    parser.add_argument("out_image_dir", type=str)
    parser.add_argument('--width', type=int, default=192 )
    parser.add_argument('--height', type=int, default=256 )
    parser.add_argument('--dilate_kernel_size', type=int, default=12 )
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

    if not os.path.isdir(args.out_image_dir):
        os.mkdir(args.out_image_dir)

    image_names = sorted( [f for f in os.listdir(args.in_image_dir) if f.endswith(('.jpg','.jpeg','.png','.bmp'))] )
    for image_name in tqdm(image_names):
        img = cv2.imread(os.path.join(args.in_image_dir, image_name ))

        # 画像をグレースケールに変換
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        # 畳み込み用カーネルを設定
        kernel = np.ones((args.dilate_kernel_size, args.dilate_kernel_size), np.uint8)

        # cv2.dilate() でマスク画像を膨張
        img = cv2.dilate(img, kernel )

        cv2.imwrite(os.path.join(args.out_image_dir, image_name.split(".")[0] + ".png" ), img)
