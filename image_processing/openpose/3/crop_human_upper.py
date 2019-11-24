import os
import argparse
from tqdm import tqdm
import json
import numpy as np
import cv2

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("in_human_dir", type=str)
    parser.add_argument("in_human_keypoints_dir", type=str)
    parser.add_argument("--out_dir", type=str, default="results")
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

    if not os.path.isdir(args.out_dir):
        os.mkdir(args.out_dir)

    human_names  = sorted( [f for f in os.listdir(args.in_human_dir) if f.endswith(('.jpg','.jpeg','.png','.bmp'))] )
    human_keypoints_names  = sorted( [f for f in os.listdir(args.in_human_keypoints_dir) if f.endswith(('.json'))] )

    n_all = len(human_names)
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
                continue

        # 各人体部位の座標値 (x,y) を取得
        Nose = key_points[0][:2]
        RShoulder = key_points[2][:2]
        LShoulder = key_points[5][:2]
        RHip = key_points[8][:2]
        LHip = key_points[11][:2]
        Rknee = key_points[9][:2]
        Lknee = key_points[12][:2]
        Neck = key_points[1][:2]
        REar = key_points[16][:2]
        LEar = key_points[17][:2]

        if( args.debug and (n_debug_print>0) ):
            print("Nose :", Nose)
            print("RShoulder :", RShoulder)
            print("LShoulder :", LShoulder)
            print("RHip :", RHip)
            print("LHip :", LHip)
            print("Rknee :", Rknee)
            print("Lknee :", Lknee)
            print("Neck :", Neck)
            print("REar :", REar)
            print("LEar :", LEar)

        human_img = cv2.imread( os.path.join(args.in_human_dir, human_name) )

        # 両肩と両尻を囲む長方形
        x, y, width, height = cv2.boundingRect(np.array([[Nose], [RHip], [LHip], [RShoulder], [LShoulder]]))
        
        # 上半身の crop y 座標を算出
        y1 = y - abs(LEar[0]-REar[0])*2
        y2 = int(y + height + abs(Rknee[1]-RHip[1])/3 * 2)
        if y1 < 0:
            y1 = 0

        height_crop = y2 - y1

        # x 座標は crop y 座標を基準に aspect 比を保つように決定
        aspect = float( human_img.shape[1] / human_img.shape[0] )
        width_crop = int(height_crop * aspect)
        x1 = x - int(abs(width_crop-width)/2)
        x2 = x1 + width_crop

        if( args.debug and (n_debug_print>0) ):
            print("x1={}, x2={} :".format(x1,x2) )
            print("y1={}, y2={} :".format(y1,y2) )

        crop_human_img = human_img[y1:y2,x1:x2]
        cv2.imwrite(os.path.join(args.out_dir,human_name), crop_human_img)

        if( args.debug ):
            cv2.rectangle(human_img, (x, y), (x+width, y+height), (0, 0, 255))
            cv2.rectangle(human_img, (x1, y1), (x2, y2), (255, 0, 0))
            cv2.imwrite(os.path.join(args.out_dir, "org_" + human_name), human_img)

        n_debug_print -= 1

    print("Summary in check_human_backpose.py")
    print("n_all :", n_all)
    print("n_keypoints_format_ng :", n_keypoints_format_ng)
