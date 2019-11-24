import os
import argparse
from tqdm import tqdm
import json
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("in_human_dir", type=str)
    parser.add_argument("in_human_parse_dir", type=str)
    parser.add_argument("in_human_keypoints_dir", type=str)
    parser.add_argument("--out_dir", type=str, default="results")
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

    out_OK_dir = os.path.join(args.out_dir, "OK")
    out_NG_dir = os.path.join(args.out_dir, "NG")
    if not os.path.isdir(args.out_dir):
        os.mkdir(args.out_dir)
    if not os.path.isdir(out_OK_dir):
        os.mkdir(out_OK_dir)
    if not os.path.isdir(out_NG_dir):
        os.mkdir(out_NG_dir)

    human_names  = sorted( [f for f in os.listdir(args.in_human_dir) if f.endswith(('.jpg','.jpeg','.png','.bmp'))] )
    human_parse_names  = sorted( [f for f in os.listdir(args.in_human_dir) if f.endswith(('.jpg','.jpeg','.png','.bmp'))] )
    human_keypoints_names  = sorted( [f for f in os.listdir(args.in_human_keypoints_dir) if f.endswith(('.json'))] )

    n_all = len(human_names)
    n_ok = 0
    n_ng = 0
    n_keypoints_format_ng = 0
    n_debug_print = 1

    for human_name in tqdm(human_names):
        with open( os.path.join(args.in_human_keypoints_dir, human_name.split(".")[0]+".json"), 'r') as f:
            json_data = json.load(f)
            if( len(json_data['people']) != 0 ):
                key_points = json_data['people'][0]["pose_keypoints_2d"]
                key_points = np.array(key_points).reshape((-1, 3)).astype(np.int32)
            else:
                n_keypoints_format_ng += 1
                n_ng += 1
                continue

        human_img = cv2.imread( os.path.join(args.in_human_dir, human_name) )
        human_parsing_img = cv2.imread( os.path.join(args.in_human_parse_dir, human_name) )
        human_parsing_img = cv2.cvtColor(human_parsing_img, cv2.COLOR_BGR2GRAY)

        right_elbow = key_points[3][:2]
        left_elbow = key_points[6][:2]

        b_right_elbow = 0
        b_left_elbow = 0        
        if human_parsing_img[right_elbow[1]][right_elbow[0]] in [ map_name_to_idx["RightArm"], map_name_to_idx["LeftArm"] ]:
            b_right_elbow = True
        if human_parsing_img[left_elbow[1]][left_elbow[0]] in [ map_name_to_idx["RightArm"], map_name_to_idx["LeftArm"] ]:
            b_left_elbow = True

        if( args.debug and (n_debug_print>0) ):
            print( "right_elbow :", right_elbow )
            print( "left_elbow :", left_elbow )
            print( "b_right_elbow :", b_right_elbow )
            print( "b_left_elbow :", b_left_elbow )

        # パース画像の右ひじ or 左座標でのピクセル値が、（服ではない）ひじのラベルになっている場合
        if( b_right_elbow or b_left_elbow ):
            n_ok += 1
            cv2.imwrite(os.path.join(out_OK_dir,human_name), human_img)
        else:
            n_ng += 1
            cv2.imwrite(os.path.join(out_NG_dir,human_name), human_img)

        n_debug_print -= 1

    print("Summary in check_human_backpose.py")
    print("n_all :", n_all)
    print("n_ok :", n_ok)
    print("n_ng :", n_ng)
    print("n_keypoints_format_ng :", n_keypoints_format_ng)
