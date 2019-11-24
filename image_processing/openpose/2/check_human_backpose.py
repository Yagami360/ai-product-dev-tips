import os
import argparse
from tqdm import tqdm
import json
import numpy as np
import shutil

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("in_human_dir", type=str)
    parser.add_argument("in_human_keypoints_dir", type=str)
    parser.add_argument("--out_dir", type=str, default="results")
    parser.add_argument('--check_nose', action='store_true', help="鼻で判定するか否か")
    parser.add_argument('--check_shoulder', action='store_true', help="両肩で判定するか否か")
    parser.add_argument('--check_hip', action='store_true', help="お尻で判定するか否か")
    parser.add_argument('--check_knee', action='store_true', help="膝で判定するか否か")
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
    human_keypoints_names  = sorted( [f for f in os.listdir(args.in_human_keypoints_dir) if f.endswith(('.json'))] )

    n_all = len(human_keypoints_names)
    n_ok = 0
    n_ng = 0
    n_keypoints_format_ng = 0
    n_nose_ng = 0
    n_shoulder_ng = 0
    n_hip_ng = 0
    n_knee_ng = 0
    n_debug_print = 1

    for human_keypoints_name in tqdm(human_keypoints_names):
        with open( os.path.join(args.in_human_keypoints_dir, human_keypoints_name), 'r') as f:
            json_data = json.load(f)
            if( len(json_data['people']) != 0 ):
                key_points = json_data['people'][0]["pose_keypoints_2d"]
                key_points = np.array(key_points).reshape((-1, 3)).astype(np.int32)
            else:
                n_keypoints_format_ng += 1
                n_ng += 1
                continue

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

        # 両耳が取れていない
        if( args.check_nose ):
            if( Nose[0] == 0 and Nose[1] == 0 ):
                n_nose_ng += 1
                n_ng += 1
                in_full_path = os.path.join(args.in_human_dir, human_keypoints_name.replace(".json",".png"))
                out_full_path = os.path.join(out_NG_dir, human_keypoints_name.replace(".json",".png"))
                if( os.path.exists(in_full_path) ):
                    shutil.copyfile( in_full_path, out_full_path)
                continue

        # 両肩の x 座標が反転している
        if( args.check_shoulder ):
            if( RShoulder[0] > LShoulder[0] ):
                n_shoulder_ng += 1
                n_ng += 1
                in_full_path = os.path.join(args.in_human_dir, human_keypoints_name.replace(".json",".png"))
                out_full_path = os.path.join(out_NG_dir, human_keypoints_name.replace(".json",".png"))
                if( os.path.exists(in_full_path) ):
                    shutil.copyfile( in_full_path, out_full_path)
                continue

        # お尻の x 座標が反転している
        if( args.check_hip ):
            if( RHip[0] > LHip[0] ):
                n_hip_ng += 1
                n_ng += 1
                in_full_path = os.path.join(args.in_human_dir, human_keypoints_name.replace(".json",".png"))
                out_full_path = os.path.join(out_NG_dir, human_keypoints_name.replace(".json",".png"))
                if( os.path.exists(in_full_path) ):
                    shutil.copyfile( in_full_path, out_full_path)
                continue

        # 両肩の x 座標が反転している
        if( args.check_shoulder ):
            if( Rknee[0] > Lknee[0] ):
                n_knee_ng += 1
                n_ng += 1
                in_full_path = os.path.join(args.in_human_dir, human_keypoints_name.replace(".json",".png"))
                out_full_path = os.path.join(out_NG_dir, human_keypoints_name.replace(".json",".png"))
                if( os.path.exists(in_full_path) ):
                    shutil.copyfile( in_full_path, out_full_path)
                continue

        n_ok += 1
        in_full_path = os.path.join(args.in_human_dir, human_keypoints_name.replace(".json",".png"))
        out_full_path = os.path.join(out_OK_dir, human_keypoints_name.replace(".json",".png"))
        if( os.path.exists(in_full_path) ):
            shutil.copyfile( in_full_path, out_full_path)

        n_debug_print -= 1

    print("Summary in check_human_backpose.py")
    print("n_all :", n_all)
    print("n_ok :", n_ok )
    print("n_ng :", n_ng )
    print("n_keypoints_format_ng :", n_keypoints_format_ng)
    print("n_nose_ng :", n_nose_ng)
    print("n_shoulder_ng :", n_shoulder_ng)
    print("n_hip_ng :", n_hip_ng)
    print("n_knee_ng :", n_knee_ng)