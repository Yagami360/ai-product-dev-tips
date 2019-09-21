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
    parser.add_argument('--back_ground_color', choices=['black', 'white', 'border'])
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if not os.path.isdir(args.out_image_dir):
        os.mkdir(args.out_image_dir)

    image_names = sorted( [f for f in os.listdir(args.in_image_dir) if f.endswith(('.jpg','.jpeg','.png','.bmp'))] )
    for image_name in tqdm(image_names):
        img_org = Image.open( os.path.join(args.in_image_dir, image_name ) )

        # resize したい (width, height) の画像サイズを持つ、貼り付け先となる空のベース画像を生成する。
        # 画像端は、単色で埋め合わせする。
        if( args.back_ground_color == "black" ):
            img_base = Image.new( "RGB", (args.width, args.height), (0,0,0) )
        elif( args.back_ground_color == "white" ):
            img_base = Image.new( "RGB", (args.width, args.height), (255,255,255) )
        else:
            img_base = Image.new( "RGB", (args.width, args.height), (0,0,0) )

        # 境界色で埋め合わせ
        pass

        # 空の画像の中央に、元画像を paste する。
        x_min = int( (args.width - img_org.size[0])/2  )
        x_max = int( args.width - (args.width - img_org.size[0])/2 )
        y_min = int( (args.height - img_org.size[1])/2  )
        y_max = int( args.height - (args.height - img_org.size[1])/2 )

        if( args.debug ):
            print( "name={}, x_min={}, x_max={}, y_min={}, y_max={}".format(image_name, x_min, x_max, y_min, y_max) )

        img_base.paste( img_org, ( x_min, y_min, x_max, y_max ) )
        img_base.save( os.path.join(args.out_image_dir, "A-2_"+image_name.replace(".jpg",".png")) )

