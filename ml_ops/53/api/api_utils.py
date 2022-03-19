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

def graph_cut(img_pillow, binary_threshold=250, back_ground_color="black"):
    # Pillow -> OpenCV への変換
    img_org_cv = conv_pillow_to_cv2(img_pillow, mask = False)

    #
    mask = np.zeros(img_org_cv.shape[:2],np.uint8)

    bgdModel = np.zeros((1,65),np.float64)
    fgdModel = np.zeros((1,65),np.float64)

    rect = (50,50,450,290)
    cv2.grabCut(img_org_cv,mask,rect,bgdModel,fgdModel,5,cv2.GC_INIT_WITH_RECT)

    mask2 = np.where((mask==2)|(mask==0),0,1).astype('uint8')
    img = img_org_cv * mask2[:,:,np.newaxis]

    # OpenCV -> Pillow に変換
    binary_mask_pillow = conv_cv2_to_pillow(mask2, mask=True)
    img_none_bg_pillow = conv_cv2_to_pillow(img, mask=False)

    return binary_mask_pillow, img_none_bg_pillow