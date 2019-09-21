import numpy as np
import os, argparse
from tqdm import tqdm
from PIL import Image

if __name__ == '__main__':
    """
    マスク画像を利用せずに、画像の対象物のアスペクト比を変えないまま resize する。
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("in_image_dir", type=str)
    parser.add_argument("out_image_dir", type=str)
    parser.add_argument('--width', type=int, default=512 )
    parser.add_argument('--height', type=int, default=512 )
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if not os.path.isdir(args.out_image_dir):
        os.mkdir(args.out_image_dir)

    image_names = sorted( [f for f in os.listdir(args.in_image_dir) if f.endswith(('.jpg','.jpeg','.png','.bmp'))] )
    for image_name in tqdm(image_names):
        img_org = Image.open( os.path.join(args.in_image_dir, image_name ) )

        # 元の画像を aspect を保ったまま resize する。
        aspect_org = float( img_org.size[0] / img_org.size[1] )
        new_width = int( aspect_org * args.height )
        new_height = args.height
        new_aspect = float( new_width / new_height )
        img_org = img_org.resize( (new_width, new_height), Image.LANCZOS )
        img_org.save( os.path.join(args.out_image_dir, "A-1_" + image_name.replace(".jpg",".png")) )

        if( args.debug ):
            print( "name={}, aspect_org={}, new_aspect={}, new_width={}, new_height={}".format(image_name, aspect_org, new_aspect, new_width, new_height) )
