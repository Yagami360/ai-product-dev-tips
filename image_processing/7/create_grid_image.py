import os
import argparse
import numpy as np
from PIL import Image
import cv2

if __name__ == '__main__':
    """
    グリッド画像を生成する。
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("in_x_dir", type=str)
    parser.add_argument("in_y_dir", type=str)
    parser.add_argument("out_grid_dir", type=str)
    parser.add_argument("--n_grid_size", type=int, default="5")
    parser.add_argument("--height", type=int, default="128")
    parser.add_argument("--width", type=int, default="128")
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if not os.path.isdir(args.out_grid_dir):
        os.mkdir(args.out_grid_dir)
        
    if( args.debug ):
        print( "args.in_x_dir :", args.in_x_dir )
        print( "args.in_y_dir :", args.in_y_dir )
        print( "args.out_grid_dir :", args.out_grid_dir )
        print( "args.n_grid_size :", args.n_grid_size )
        print( "args.height :", args.height )
        print( "args.width :", args.width )

    image_x_names = sorted([f for f in os.listdir(args.in_x_dir) if f.endswith(('.png', ".jpeg", ".jpg"))])
    image_y_names = sorted([f for f in os.listdir(args.in_y_dir) if f.endswith(('.png', ".jpeg", ".jpg"))])

    # グリッド画像の貼り付け先となるベース画像
    image_base = Image.new("RGB", (args.width*(args.n_grid_size+1), args.height*(args.n_grid_size+1)), (255, 255, 255))

    for y in range(args.n_grid_size):
        image_y = Image.open( os.path.join(args.in_y_dir, image_y_names[y]) )
        image_y = image_y.resize( (args.width, args.width), Image.LANCZOS )
        image_base.paste( image_y, (0,(y+1)*args.height) )
        for x in range(args.n_grid_size):
            image_x = Image.open( os.path.join(args.in_x_dir, image_x_names[x]) )
            image_x = image_x.resize( (args.width, args.width), Image.LANCZOS )
            image_base.paste( image_x, ((x+1)*args.width,0) )

    image_base.save(os.path.join(args.out_grid_dir, "grid_image.png"))

