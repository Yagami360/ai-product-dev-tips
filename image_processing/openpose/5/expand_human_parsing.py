import os
import argparse
from tqdm import tqdm
import json
import numpy as np
from PIL import Image
from PIL import ImageDraw

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
    "LeftForearm" : 22,
    "RightForearm" : 23,
    "LowerBody" : 24,
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
    "LeftForearm" : (255,228,225),
    "RightForearm" : (139,125,123),
    "LowerBody" : (188,143,143),
}

map_idx_to_rgb = {
    0 : (0,0,0),
    1 : (128,0,0),
    2 : (255,0,0),
    3 : (0,85,0),
    4 : (170,0,51),
    5 : (255,85,0),
    6 : (0,0,85),
    7 : (0,119,221),
    8 : (85,85,0),
    9 : (0,85,85),
    10 : (85,51,0),
    11 : (52,86,128),
    12 : (0,128,0),
    13 : (0,0,255),
    14 : (51,170,221),
    15 : (0,255,255),
    16 : (85,255,170),
    17 : (170,255,85),
    18 : (255,255,0),
    19 : (255,170,0),
    20 : (0,255,65),
    21 : (83,53,99),
    22 : (255,228,225),
    23 : (139,125,123),
    24 : (188,143,143),
}


def decode_labels(mask, num_images=1, num_classes=25):
    h, w = mask.shape
    outputs = np.zeros((h, w, 3), dtype=np.uint8)
    img = Image.new('RGB', (w, h))
    pixels = img.load()
    for i in range(h):
        for j in range(w):
            pixels[j, i] = map_idx_to_rgb[mask[i,j]]
    outputs = np.array(img)
    return outputs

def arm_clipper(elbow, shoulder, wrist, size, label):
    """
    腕部分のクロップ領域を計算するためのクリッパーを検出し Pillow オブジェクトで返す。
    """
    shoulder_elbow_vec = (shoulder - elbow)[:2]
    wrist_elbow_vec = (wrist - elbow)[:2]

    k1 = shoulder_elbow_vec[1] / shoulder_elbow_vec[0]
    k2 = wrist_elbow_vec[1] / wrist_elbow_vec[0]

    L_x = np.sqrt(shoulder_elbow_vec.dot(shoulder_elbow_vec))
    L_y = np.sqrt(wrist_elbow_vec.dot(wrist_elbow_vec))

    cos_angle = shoulder_elbow_vec.dot(wrist_elbow_vec) / (L_x * L_y)
    angle = np.arccos(cos_angle)
    angle2 = angle / 2

    if k1 > k2:
        angle_line = angle2 + np.arctan(k2)
    else:
        angle_line = angle2 + np.arctan(k1)

    k = np.tan(angle_line)

    return draw_region(elbow, wrist, size, label, k)

def leg_clipper(hip, knee, size, label):
    """
    足部分のクロップ領域を計算するためのクリッパーを検出し Pillow オブジェクトで返す。
    """
    mid = np.array([(hip[0]+knee[0])/2, (hip[1]+knee[1])/2])
    hip_knee_vec = np.array([(knee[0]-hip[0]), (knee[1]-hip[1])])

    k = -1 / (hip_knee_vec[1]/hip_knee_vec[0])

    return draw_region(mid, knee, size, label, k)

def draw_region(root, point, size, label, k):
    im = Image.new('L', size=size)
    draw = ImageDraw.Draw(im)

    xmax = (size[1]-root[1])/k + root[0]
    xmin = (-root[1] / k) + root[0]
    ymax = k*(size[0]-root[0]) + root[1]
    ymin = k * (-root[0]) + root[1]

    is_upper = ((k * (point[0] - root[0]) + root[1]) > point[1])

    if xmax >= size[0]:
        if ymin >= 0:
            if is_upper:
                draw.polygon(((0,0), (0,ymin), (size[0],ymax), (size[0], 0)), fill=label, outline=label)
            else:
                draw.polygon(((0,ymin), (0,size[1]), (size[0],size[1]),(size[0], ymax)), fill=label, outline=label)
        else:
            if is_upper:
                draw.polygon(((xmin, 0), (size[0], ymax), (size[0], 0)), fill=label, outline=label)
            else:
                draw.polygon(((0, 0), (0, size[1]), (size[0], size[1]), (size[0], ymax), (xmin, 0)), fill=label,
                             outline=label)

    elif xmax < size[0] and xmax >= 0:
        if xmin >= size[0]:
            if is_upper:
                draw.polygon(((0, 0), (0, size[1]), (xmax, size[1]), (size[0],ymax),(size[0],0)), fill=label, outline=label)
            else:
                draw.polygon(((xmax, size[1]), (size[0], size[1]), (size[0], ymax)), fill=label, outline=label)

        elif xmin<size[0] and xmin >=0:
            if is_upper:
                draw.polygon(((0, 0), (0, size[1]), (xmax, size[1]), (xmin, 0)), fill=label,
                             outline=label)
            else:
                draw.polygon(((xmax, size[1]), (size[0], size[1]), (size[0], 0), (xmin, 0)), fill=label,
                             outline=label)
    elif xmax < 0:
        if ymax >= 0:
            if is_upper:
                draw.polygon(((0, 0), (0, ymin), (size[0], ymax), (size[0], 0)), fill=label,
                         outline=label)
            else:
                draw.polygon(((0, ymin), (0, size[1]), (size[0], size[1]), (size[0], ymax)), fill=label,
                         outline=label)
        else:
            if is_upper:
                draw.polygon(((0, 0), (0, ymin), (xmin, 0)), fill=label,
                         outline=label)
            else:
                draw.polygon(((0, ymin), (0, size[1]), (size[0], size[1]), (size[0], 0),(xmin,0)), fill=label,
                         outline=label)
    return im


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("in_human_parse_dir", type=str)
    parser.add_argument("in_human_keypoints_dir", type=str)
    parser.add_argument("--out_dir", type=str, default="results")
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

    if not os.path.isdir(args.out_dir):
        os.mkdir(args.out_dir)
    if( args.debug ):
        if not os.path.isdir( os.path.join(args.out_dir, "debug") ):
            os.mkdir( os.path.join(args.out_dir, "debug") )

    human_parse_names  = sorted( [f for f in os.listdir(args.in_human_parse_dir) if f.endswith(('.jpg','.jpeg','.png','.bmp'))] )
    human_keypoints_names  = sorted( [f for f in os.listdir(args.in_human_keypoints_dir) if f.endswith(('_keypoints.json'))] )

    n_all = len(human_parse_names)
    n_ok = 0
    n_ng = 0
    n_keypoints_format_ng = 0
    n_debug_print = 1

    for human_name in tqdm(human_parse_names):
        with open( os.path.join(args.in_human_keypoints_dir, human_name.split(".")[0]+"_keypoints.json"), 'r') as f:
            json_data = json.load(f)
            if( len(json_data['people']) != 0 ):
                key_points = json_data['people'][0]["pose_keypoints_2d"]
                key_points = np.array(key_points).reshape((-1, 3)).astype(np.int32)
            else:
                n_keypoints_format_ng += 1
                n_ng += 1
                continue

        right_shoulder = key_points[2]
        left_shoulder = key_points[5]

        right_elbow = key_points[3]
        left_elbow = key_points[6]

        right_wrist = key_points[4]
        left_wrist = key_points[7]

        right_hip = key_points[8]
        left_hip = key_points[11]

        right_knee = key_points[9]
        left_knee = key_points[12]

        if( args.debug and (n_debug_print>0) ):
            print( "right_shoulder :", right_shoulder )
            print( "left_shoulder :", left_shoulder )
            print( "right_elbow :", right_elbow )
            print( "left_elbow :", left_elbow )
            print( "right_wrist :", right_wrist )
            print( "left_wrist :", left_wrist )
            print( "right_hip :", right_hip )
            print( "left_hip :", left_hip )
            print( "right_knee :", right_knee )
            print( "left_knee :", left_knee )

        human_parsing_img = Image.open( os.path.join(args.in_human_parse_dir, human_name) )
        human_parsing_np = np.array(human_parsing_img).astype(np.int32)

        right_arm_np = (human_parsing_np == 15).astype(np.int32)
        left_arm_np = (human_parsing_np == 14).astype(np.int32)
        right_leg_np = (human_parsing_np == 17).astype(np.int32)
        left_leg_np = (human_parsing_np == 16).astype(np.int32)
        pants_np = (human_parsing_np == 9).astype(np.int32)
        skirt_np = (human_parsing_np == 12).astype(np.int32)

        # 特定のラベルの領域を消す（後で追加のラベル領域を上書きするため）
        human_parsing_np = human_parsing_np - right_arm_np * 15 - left_arm_np * 14 - pants_np * 9 - skirt_np * 12

        if( args.debug and (n_debug_print>0) ):
            expand_human_parsing_np_rgb = decode_labels(human_parsing_np.astype(np.int32))
            expand_human_parsing_img_rbg = Image.fromarray(expand_human_parsing_np_rgb)
            expand_human_parsing_img_rbg.save(os.path.join(args.out_dir, "debug", "vis_" + human_name))

        #---------------------------
        # 腕部分のクロップ
        #---------------------------
        # 腕部分のクロップ領域を計算するためのクリッパーを取得
        right_arm_clipper = arm_clipper(right_elbow, right_shoulder, right_wrist, human_parsing_img.size, 1)
        left_arm_clipper = arm_clipper(left_elbow, left_shoulder, left_wrist, human_parsing_img.size, 1)
        right_arm_clipper_np = np.array(right_arm_clipper).astype(np.int32)
        left_arm_clipper_np = np.array(left_arm_clipper).astype(np.int32)

        # クロップ対象領域（クリッパー）でクロップ
        right_forearm_np = right_arm_np * right_arm_clipper_np
        left_forearm_np = left_arm_np * left_arm_clipper_np

        right_arm_np = right_arm_np - right_forearm_np
        left_arm_np = left_arm_np - left_forearm_np

        if( args.debug and (n_debug_print>0) ):
            print( "right_arm_clipper :",right_arm_clipper )
            right_arm_clipper_np_rgb = decode_labels(np.array(right_arm_clipper).astype(np.int32))
            right_arm_clipper_np_img = Image.fromarray(right_arm_clipper_np_rgb)
            right_arm_clipper_np_img.save(os.path.join(args.out_dir, "debug", "right_arm_clipper_" + human_name))
            left_arm_clipper_np_rgb = decode_labels(np.array(left_arm_clipper).astype(np.int32))
            left_arm_clipper_np_img = Image.fromarray(left_arm_clipper_np_rgb)
            left_arm_clipper_np_img.save(os.path.join(args.out_dir, "debug", "left_arm_clipper_" + human_name))

            right_forearm_np_rgb = decode_labels(right_forearm_np)
            right_forearm_np_rgb_img = Image.fromarray(right_forearm_np_rgb)
            right_forearm_np_rgb_img.save(os.path.join(args.out_dir, "debug", "right_forearm_" + human_name))

        #---------------------------
        # 下半身領域のクロップ
        #---------------------------
        # クロップ領域を取得
        right_leg_clipper = leg_clipper(right_hip, right_knee, human_parsing_img.size, 1)
        left_leg_clipper = leg_clipper(left_hip, left_knee, human_parsing_img.size, 1)
        right_leg_clipper_np = np.array(right_leg_clipper).astype(np.int32)
        left_leg_clipper_np = np.array(left_leg_clipper).astype(np.int32)

        right_clipper_pants_np = pants_np * right_leg_clipper_np
        right_clipper_skirt_np = skirt_np * right_leg_clipper_np
        left_clipper_pants_np = pants_np  * left_leg_clipper_np
        left_clipper_skirt_np = skirt_np * left_leg_clipper_np

        pants_clipper_np = ((right_clipper_pants_np + left_clipper_pants_np)>0).astype(np.int32)
        skirt_clipper_np = ((right_clipper_skirt_np + left_clipper_skirt_np)>0).astype(np.int32)

        # クロップ対象領域でクロップ
        pants_np = pants_np - pants_clipper_np
        skirt_np = skirt_np - skirt_clipper_np

        #----------------------------------------------------------
        # 特定のラベルの領域を消していたパース画像に、追加の部位ラベルを上書き
        #----------------------------------------------------------
        human_parsing_np = \
            human_parsing_np + right_arm_np * 15 + left_arm_np * 14 + \
            right_forearm_np * 23 + left_forearm_np * 22 + pants_np * 9 + skirt_np * 12 + \
            pants_clipper_np * 24 + skirt_clipper_np * 24

        new_human_parsing_img = Image.fromarray(human_parsing_np.astype(np.int32))
        new_human_parsing_img.save(os.path.join(args.out_dir, human_name))

        human_parsing_np_rgb = decode_labels(human_parsing_np)
        human_parsing_np_rgb_img = Image.fromarray(human_parsing_np_rgb)
        human_parsing_np_rgb_img.save(os.path.join(args.out_dir, "vis_" + human_name))

        n_debug_print -= 1

    print("Summary in expand_human_parsing.py")
    print("n_all :", n_all)
    print("n_ok :", n_ok)
    print("n_ng :", n_ng)
    print("n_keypoints_format_ng :", n_keypoints_format_ng)
