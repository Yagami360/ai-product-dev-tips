import os
import argparse
from tqdm import tqdm
import numpy as np
import cv2
import dlib

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("in_image_dir", type=str)
    parser.add_argument("out_image_dir", type=str)
    parser.add_argument('--in_predictor_path', type=str, default="shape_predictor_68_face_landmarks.dat")
    parser.add_argument('--marker_size', type=int, default=10)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

    if not os.path.isdir(args.out_image_dir):
        os.mkdir(args.out_image_dir)

    # 検出器と識別器のオブジェクト作成
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(args.in_predictor_path)

    image_names = sorted( [f for f in os.listdir(args.in_image_dir) if f.endswith(('.jpg','.jpeg','.png','.bmp'))] )

    n_debug_print = 5
    for image_name in tqdm(image_names):
        img = cv2.imread( os.path.join(args.in_image_dir, image_name) )
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # 検出器に画像を渡し、検出結果を取得
        dets = detector(img, 0)
        if( args.debug and (n_debug_print > 0) ):
            print( "len(dets)={}".format(len(dets)) )

        for i, det in enumerate(dets):
            #---------------------------
            # Rect の検出
            #---------------------------
            img_height = img.shape[0]
            img_width = img.shape[1]

            height = det.height()
            width = det.width()

            left_x = det.left()
            left_y = det.top()
            right_x = det.right()
            right_y = det.bottom()
            large_left = left_x - width
            large_top = left_y - height
            large_right = right_x + width
            large_bottom = right_y + width

            if large_left < 0:
                large_left = 0
            if large_top < 0:
                large_top = 0
            if large_right > img_width:
                large_right = img_width
            if large_bottom > img_height:
                large_bottom = img_height

            # dlib.rectangle 型を取得
            large_det = dlib.rectangle(left_x - width, left_y - height, right_x + width, right_y + width)

            #---------------------------
            # face の検出
            #---------------------------
            shape = predictor(img, det)

            face_contours_x = []
            face_contours_y = []
            face_contours_xy = []
            for j in range(1, 17):
                point = shape.part(j)
                face_contours_x.append(point.x)
                face_contours_y.append(point.y)
                face_contours_xy.append((point.x,point.y))

            #-----------------
            # draw on image
            #-----------------
            cv2.rectangle(img, (left_x, left_y), (right_x, right_y), (0, 0, 255))
            cv2.rectangle(img, (large_left, large_top), (large_right, large_bottom), (0, 255, 0))

            for x,y in zip(face_contours_x, face_contours_y):
                cv2.drawMarker(img, (x,y), (255, 0, 0), markerType=cv2.MARKER_TILTED_CROSS, markerSize=args.marker_size)

            img_cv = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            cv2.imwrite( os.path.join(args.out_image_dir, "face_detected_" + image_name), img_cv)
