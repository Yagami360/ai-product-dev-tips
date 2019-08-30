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
    args = parser.parse_args()

    image = cv2.imread(args.in_image_path)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)   # グレースケールに変換
    #cv2.imwrite( args.in_image_path.replace(".png", "_Gray.png"), image )
    height, width = image.shape[0], image.shape[1]

    # == 演算子で 画像全体を比較
    # 各要素の True -> 対応するピクセルのラベル値が 0 ; True -> 対応するピクセルのラベル値が 0 でない
    b_matrix = ( image ==  map_name_to_idx["Background"] )
    #b_matrix = ( image ==  map_name_to_rgb["Background"] )
    print( "b_matrix :", b_matrix )
    print( "b_matrix.shape :", b_matrix.shape )

    # 行列の True 要素の数の和を取る。この値が該当するラベルの総ピクセル数となる。
    #n_true = np.sum( b_matrix[:,:,0] )   # for RGB
    n_true = np.sum( b_matrix[:,:] )      # for Gray scale
    print( "n_true :", n_true )

    # 画像全体に対してのラベル値が 0 の割合
    parcent = 100 * ( n_true / ( height * width ) )
    print( "parcent :", parcent )

    # ある一定以上の割合で、ラベル 0 が存在する場合
    threshold = 1
    if( parcent >= threshold ):
        print( "0 : Background" ) 

    # 別のラベルに対しても検出
    b_matrix = ( image ==  map_name_to_idx["Face"] )
    #b_matrix = ( image ==  map_name_to_rgb["Face"] )
    print( "b_matrix :", b_matrix )
    print( "b_matrix.shape :", b_matrix.shape )
    n_true = np.sum( b_matrix[:,:] )
    #n_true = np.sum( b_matrix[:,:,0] )
    parcent = 100 * ( n_true / ( height * width ) )
    threshold = 1
    if( parcent >= threshold ):
        print( "13 : Face" ) 
