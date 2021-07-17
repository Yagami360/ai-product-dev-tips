import os
import numpy as np
from PIL import Image
import cv2

def conv_pillow_to_cv2( img_pillow, mask = False ):
    if( mask ):
        img_cv = cv2.cvtColor(np.asarray(img_pillow))
    else:
        img_cv = cv2.cvtColor(np.asarray(img_pillow), cv2.COLOR_RGB2BGR)

    return img_cv

def conv_cv2_to_pillow( img_cv, mask = False ):
    if( mask ):
        img_pillow = Image.fromarray(img_cv)
    else:
        img_pillow = Image.fromarray( cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB) )

    return img_pillow

"""
# OpenCV を用いた背景くり抜き
def graph_cut(img_pillow, binary_threshold=100, back_ground_color="black"):
    # Pillow -> OpenCV への変換
    img_org_cv = conv_pillow_to_cv2(img_pillow, mask = False)

    # 人物セグメンテーション画像をグレースケールに変換する。
    img_org_gray = cv2.cvtColor(img_org_cv, cv2.COLOR_BGR2GRAY)

    # 人物セグメンテーション画像をバイナリ化する。
    _, img_org_binary = cv2.threshold( img_org_gray, binary_threshold, 255, cv2.THRESH_BINARY )

    # バイナリマスクの輪郭を抽出する。
    if( int(cv2.__version__.split(".")[0]) >= 4 ):
        contours, hierarchy = cv2.findContours(img_org_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    else:
        _, contours, hierarchy = cv2.findContours(img_org_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # バイナリマスクの輪郭内部を 白 = (255, 255, 255) で塗りつぶす。
    binary_mask = np.zeros_like(img_org_binary)
    cv2.drawContours(binary_mask, contours, -1, color=(255, 255, 255), thickness=-1)

    # グレースケールのバイナリマスクを RGB の３チャンネルに戻す
    img = cv2.merge((img_org_binary, img_org_binary, img_org_binary))

    # ブレンド式用に 0.0 ~ 1.0f のスケールに変換する。
    img  = img.astype('float32') / 255.0
    img_org_cv = img_org_cv.astype('float32') / 255.0

    # 元画像とバイナリマスク画像をブレンドする。
    if( back_ground_color == "black" ):
        bg_color = (0.0, 0.0, 0.0)
    elif( back_ground_color == "white" ):
        bg_color = (1.0, 1.0, 1.0)
    elif( back_ground_color == "green" ):
        bg_color = (0.0, 1.0, 0.0)
    else:
        bg_color = (0.0, 0.0, 0.0)

    masked = (img * img_org_cv) + ((1-img) * bg_color )

    # 0 ~255 のスケールに戻す
    masked = (masked * 255).astype('uint8')

    # OpenCV -> Pillow に変換
    binary_mask_pillow = conv_cv2_to_pillow(binary_mask, mask=True)
    img_none_bg_pillow = conv_cv2_to_pillow(masked, mask=False)
    return binary_mask_pillow, img_none_bg_pillow
"""

def graph_cut(img_pillow, iters=5):
    # Pillow -> OpenCV への変換
    img_org_cv = conv_pillow_to_cv2(img_pillow, mask = False)

    #
    mask = np.zeros(img_org_cv.shape[:2],np.uint8)

    bgdModel = np.zeros((1,65),np.float64)
    fgdModel = np.zeros((1,65),np.float64)

    rect = (50,50,450,290)
    cv2.grabCut(img_org_cv,mask,rect,bgdModel,fgdModel,iters,cv2.GC_INIT_WITH_RECT)

    mask2 = np.where((mask==2)|(mask==0),0,1).astype('uint8')
    img = img_org_cv * mask2[:,:,np.newaxis]

    # OpenCV -> Pillow に変換
    binary_mask_pillow = conv_cv2_to_pillow(mask2, mask=True)
    img_none_bg_pillow = conv_cv2_to_pillow(img, mask=False)

    return binary_mask_pillow, img_none_bg_pillow
