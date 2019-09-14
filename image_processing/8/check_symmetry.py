import os
import argparse
from tqdm import tqdm
import numpy as np
from PIL import Image
import cv2


def create_binary_mask( original_image_path ):
    """
    バイナリマスク画像を生成する。（背景色が白になっている必要あり）
    [args]
        original_image_path : [str] 元の画像のパス
    [resturns]
        original_mask : [ndarry] バイナリマスク画像（OpenCV の ndarray）
    """
    img = Image.open(original_image_path).convert('RGB')
    img_array = np.asarray(img)
    H, W, C = img_array.shape
    
    mask_array = np.zeros((H, W), dtype=np.uint8)
    background_color_value = img_array[0, 0, 0]
    print( "background_color_value :", background_color_value )
    assert background_color_value == 246 or background_color_value == 255
    background_color = [background_color_value, background_color_value, background_color_value]
    
    # True → 対象物, False → 背景
    background_region = (img_array[:, :, 0] == background_color[0]) & (img_array[:, :, 1] == background_color[1]) & (img_array[:, :, 2] == background_color[2])
    #print( "background_region :", background_region )

    mask_array[~background_region] = 255
    mask_img = Image.fromarray(mask_array.astype(np.uint8))

    # Pillow -> OpenCV
    original_mask = np.asarray(mask_img)
    return original_mask


if __name__ == '__main__':
    """
    画像の左右対称性を検出する。
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("in_image_dir", type=str)
    parser.add_argument("out_image_dir", type=str)
    parser.add_argument('--symmetry_rate_threshold', type=float, default=0.915 )
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if not os.path.isdir(args.out_image_dir):
        os.mkdir(args.out_image_dir)

    image_names = sorted( [f for f in os.listdir(args.in_image_dir) if f.endswith(('.jpg','.jpeg','.png','.gif','.bmp'))] )

    for image_name in tqdm(image_names):
        in_image_full_path = os.path.join(args.in_image_dir, image_name)
        
        # バイナリマスクの生成
        original_mask = create_binary_mask( original_image_path = in_image_full_path )
        cv2.imwrite( os.path.join(args.out_image_dir, "binary_mask_" + image_name), original_mask )

        H, W = original_mask.shape
        if( args.debug ):
            print( "H={},W={}".format(H,W) )

        # 1 : y軸を中心に反転（ようするに左右反転）
        flipped_mask = cv2.flip(original_mask, 1)
        cv2.imwrite( os.path.join(args.out_image_dir, "flipped_mask_" + image_name), flipped_mask )

        # バイナリマスク値 (0 or 1) なので、0 or 1 のサムで対称性を計算可能（1.0に近いほど対称性が高い）
        symmetry_rate = ( sum(sum(original_mask == flipped_mask) ) ) / H / W

        if( symmetry_rate >= args.symmetry_rate_threshold ):
            print("対称画像 : symmetry_rate={}".format(symmetry_rate) )
        else:
            print("非対称画像 : symmetry_rate={}".format(symmetry_rate) )
