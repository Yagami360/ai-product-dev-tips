import numpy as np
import os, argparse
from tqdm import tqdm
from PIL import Image
import cv2

if __name__ == '__main__':
    """
    マスク画像を利用せずに、画像の対象物のアスペクト比を変えないまま adjust する。
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

        #------------------------------------------------------------------------------------
        # 元画像の width, height の小さいほうを基準として、aspect 比を保ったまま元画像を resize する。
        #------------------------------------------------------------------------------------
        width_org = img_org.size[0]
        height_org = img_org.size[1]
        aspect_org = float( width_org / height_org )

        # 元画像の with, height の小さいほうを基準とする。
        if( width_org < height_org ):
            new_width = int( aspect_org * args.height )
            new_height = args.height
        else:
            new_width = args.width
            new_height = int( (1/aspect_org) * args.width )

        new_aspect = float( new_width / new_height )

        if( args.debug ):
            print( "name={}, aspect_org={}, new_aspect={}, new_width={}, new_height={}".format(image_name, aspect_org, new_aspect, new_width, new_height) )

        img_org = img_org.resize( (new_width, new_height), Image.LANCZOS )

        #------------------------------------------------------------------------------------
        # resize したい (width, height) の画像サイズを持つ、貼り付け先となる空のベース画像を生成する。
        #------------------------------------------------------------------------------------
        # 画像端は、単色で埋め合わせする。
        if( args.back_ground_color == "black" ):
            img_base = Image.new( "RGB", (args.width, args.height), (0,0,0) )
        elif( args.back_ground_color == "white" ):
            img_base = Image.new( "RGB", (args.width, args.height), (255,255,255) )
        else:
            img_base = Image.new( "RGB", (args.width, args.height), img_org.getpixel((0,0)) )

        #-------------------------------------------------
        # 空の画像の中央に、元画像を paste する。
        #-------------------------------------------------
        x_min = int( (args.width - img_org.size[0])/2  )
        x_max = int( args.width - (args.width - img_org.size[0])/2 )
        y_min = int( (args.height - img_org.size[1])/2  )
        y_max = int( args.height - (args.height - img_org.size[1])/2 )

        if( x_min < 0 or x_max > args.width ):
            x_min = 0
            x_max = args.width - 1

        if( y_min < 0 or y_max > args.height ):
            y_min = 0
            y_max = args.height - 1

        if( args.debug ):
            print( "name={}, x_min={}, x_max={}, y_min={}, y_max={}".format(image_name, x_min, x_max, y_min, y_max) )
            print( "img_base.size={}".format(img_base.size) )
            print( "img_org.size={}".format(img_org.size) )

        img_base.paste( img_org, ( x_min, y_min, x_max, y_max ) )

        # 境界色で埋め合わせ（実装中...）
        if( args.back_ground_color == "border" ):
            img_org_cv = cv2.cvtColor(np.asarray(img_org), cv2.COLOR_RGB2BGR)
            upper_line = img_org_cv[0, :]
            bottom_line = img_org_cv[-1, :]
            right_line = img_org_cv[:, 0]
            left_line = img_org_cv[:, -1]

            if( args.debug ):
                print( "upper_line.shape={}, bottom_line.shape={}, right_line.shape={}, left_line.shape={}".format(upper_line.shape, bottom_line.shape, right_line.shape, left_line.shape) )

            img_base_cv = cv2.cvtColor(np.asarray(img_base), cv2.COLOR_RGB2BGR)
            img_base_cv[0:y_min] = upper_line[0:img_base_cv.shape[0]]
            img_base_cv[y_max:-1] = bottom_line[0:img_base_cv.shape[0]]
            #img_base_cv[0:x_min] = left_line[0:img_base_cv.shape[1]]
            #img_base_cv[x_max:-1] = right_line[0:img_base_cv.shape[1]]            
            img_base = Image.fromarray( cv2.cvtColor(img_base_cv, cv2.COLOR_BGR2RGB) )

        img_base.save( os.path.join(args.out_image_dir, image_name.replace(".jpg",".png")) )

