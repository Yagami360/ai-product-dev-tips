import numpy as np
import os, argparse
from tqdm import tqdm
from PIL import Image

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("in_image_dir", type=str)
    parser.add_argument("out_image_dir", type=str)
    parser.add_argument('--n_offset', type=int, default=5 )
    parser.add_argument('--offset_init_width', type=int, default=0 )
    parser.add_argument('--offset_init_height', type=int, default=0 )
    parser.add_argument('--offset_width', type=int, default=10 )
    parser.add_argument('--offset_height', type=int, default=10 )
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if not os.path.isdir(args.out_image_dir):
        os.mkdir(args.out_image_dir)

    image_names = sorted( [f for f in os.listdir(args.in_image_dir) if f.endswith(('.jpg','.jpeg','.png','.bmp'))] )

    for image_name in tqdm(image_names):
        img_org = Image.open( os.path.join(args.in_image_dir, image_name ) )

        offset_width = args.offset_init_width
        offset_height = args.offset_init_height
        for i in range(args.n_offset):
            offset_width += args.offset_width
            offset_height += args.offset_height

            if( args.debug ):
                print( "offset_width={}, offset_height={}".format(offset_width,offset_height) )

            # Pillow の `rotate()` メソッドの `translate` 引数を使用して平行移動する。
            img_offset = img_org.rotate( 0, translate=(offset_width, offset_height) )
            img_offset.save( os.path.join(args.out_image_dir, "offset{}_".format(i) + image_name.replace(".jpg",".png")) )
        