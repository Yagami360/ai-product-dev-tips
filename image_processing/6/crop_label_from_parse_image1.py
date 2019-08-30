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
    セグメンテーションセグメンテーション画像から、特定のラベル部分を crop する。（for ループを使用）
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("in_image_path", type=str)
    args = parser.parse_args()

    image = cv2.imread(args.in_image_path)
    height, width = image.shape[0], image.shape[1]

    # crop 先の空の画像
    image_base_np = np.zeros((height, width, 3))

    for i in range(height) :
        for j in range(width):
            label = image[i][j]
            if( all(label == map_name_to_rgb["Background"]) ):
                pass
            elif( all(label == map_name_to_rgb["Face"]) ):
                image_base_np[i][j] = label
            else:
                pass

    out_file_path = args.in_image_path.split("/")[-1].replace(".png", "_cropped.png") 
    cv2.imwrite(out_file_path, image_base_np)