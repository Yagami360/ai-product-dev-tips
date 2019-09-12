import os
import argparse
import numpy as np
import cv2

map_name_to_idx = {
    "Background" : 0,
    "Hat" : 1,
    "Hair" : 2,
    "Glove" : 3,
    "Sunglasses" : 4,
    "UpperClothes" : 5,
    "Dress" : 6,
    "Coat" : 7,
    "Socks" : 8,
    "Pants" : 9,
    "Jumpsuits" : 10,
    "Scarf" : 11,
    "Skirt" : 12,
    "Face" : 13,
    "LeftArm" : 14,
    "RightArm" : 15,
    "LeftLeg" : 16,
    "RightLeg" : 17,
    "LeftShoe" : 18,
    "RightShoe" : 19,
    "RightHand" : 20,
    "LeftHand" : 21,
}

map_name_to_rgb = {
    "Background" : (0,0,0),
    "Hat" : (128,0,0),
    "Hair" : (255,0,0),
    "Glove" : (0,85,0),
    "Sunglasses" : (170,0,51),
    "UpperClothes" : (255,85,0),
    "Dress" : (0,0,85),
    "Coat" : (0,119,221),
    "Socks" : (85,85,0),
    "Pants" : (0,85,85),
    "Jumpsuits" : (85,51,0),
    "Scarf" : (52,86,128),
    "Skirt" : (0,128,0),
    "Face" : (0,0,255),
    "LeftArm" : (51,170,221),
    "RightArm" : (0,255,255),
    "LeftLeg" : (85,255,170),
    "RightLeg" : (170,255,85),
    "LeftShoe" : (255,255,0),
    "RightShoe" : (255,170,0),
    "RightHand" : (0,255,65),
    "LeftHand" : (83,53,99),
}

if __name__ == '__main__':
    """
    セグメンテーションセグメンテーション画像から、ラベル値を取得する。（for ループを使用）
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("in_image_path", type=str)
    parser.add_argument("--rgb", action='store_true' )
    args = parser.parse_args()

    image = cv2.imread(args.in_image_path)

    if( args.rgb ):
        pass
    else:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)   # グレースケールに変換
        #cv2.imwrite( args.in_image_path.replace(".png", "_Gray.png"), image )
        pass

    height, width = image.shape[0], image.shape[1]

    n_background = 0
    n_hat = 0
    n_hair = 0
    n_face = 0
    for i in range(height) :
        for j in range(width):
            if( args.rgb ):
                label = image[i][j]
            else:
                label = image[i][j][0]
                
            if( args.rgb ):
                if( all(label == map_name_to_rgb["Background"]) ):
                    print( "0 : Background" )
                    n_background += 1
                elif( all(label == map_name_to_rgb["Hat"]) ):
                    print( "1 : Hat" )
                    n_hat += 1
                elif( all(label == map_name_to_rgb["Hair"]) ):
                    print( "2 : Hair" )
                    n_hair += 1
                elif( all(label == map_name_to_rgb["Face"]) ):
                    print( "13 : Face" )
                    n_face += 1
                else:
                    pass
            else:
                if( all(label == map_name_to_idx["Background"]) ):
                    print( "0 : Background" )
                    n_background += 1
                elif( all(label == map_name_to_idx["Hat"]) ):
                    print( "1 : Hat" )
                    n_hat += 1
                elif( all(label == map_name_to_idx["Hair"]) ):
                    print( "2 : Hair" )
                    n_hair += 1
                elif( all(label == map_name_to_idx["Face"]) ):
                    print( "13 : Face" )
                    n_face += 1
                else:
                    pass

    print( "n_background :", n_background )
    print( "percent_background :", n_background / (height*width) )
    print( "n_hat :", n_hat )
    print( "percent_hat :", n_hat / (height*width) )
    print( "n_hair :", n_hair )
    print( "percent_hair :", n_hair / (height*width) )
    print( "n_face :", n_face )
    print( "percent_face :", n_face / (height*width) )