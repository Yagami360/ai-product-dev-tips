import numpy as np
import os, argparse
from tqdm import tqdm
from PIL import Image

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("in_image_dir", type=str)
    parser.add_argument("out_image_dir", type=str)
    parser.add_argument('--n_rotate', type=int, default=5 )
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if not os.path.isdir(args.out_image_dir):
        os.mkdir(args.out_image_dir)

    image_names = sorted( [f for f in os.listdir(args.in_image_dir) if f.endswith(('.jpg','.jpeg','.png','.bmp'))] )

    for image_name in tqdm(image_names):
        img_org = Image.open( os.path.join(args.in_image_dir, image_name ) )

        rotate = 0
        n_rotate_rate = -int( 360/(args.n_rotate+1) )
        for i in range(args.n_rotate):
            rotate += n_rotate_rate

            if( args.debug ):
                print( "rotate={}, n_rotate_rate={}".format(rotate,n_rotate_rate) )

            # Pillow の `rotate()` メソッドを使用して回転する。
            img_rotate = img_org.rotate(rotate)
            img_rotate.save( os.path.join(args.out_image_dir, "rot{}_".format(i) + image_name.replace(".jpg",".png")) )
        