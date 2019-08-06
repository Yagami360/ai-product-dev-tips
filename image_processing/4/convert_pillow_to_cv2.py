import os
import argparse
import numpy as np
from PIL import Image
import cv2

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument( "in_image_path", type=str )
    parser.add_argument( "out_image_path", type=str )
    args = parser.parse_args()

    in_image_path = args.in_image_path
    out_image_path = args.out_image_path

    img_pillow = Image.open(in_image_path)
    img_np = np.asarray(img_pillow)
    img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    cv2.imwrite(out_image_path, img_cv)
