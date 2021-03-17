import numpy as np
import os, argparse
from tqdm import tqdm
from PIL import Image
import cv2

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_image_dir", type=str, default="in_images")
    parser.add_argument("--out_image_dir", type=str, default="out_images")
    parser.add_argument('--iter_count', type=int, default=5)
    args = parser.parse_args()

    if not os.path.isdir(args.out_image_dir):
        os.mkdir(args.out_image_dir)

    image_names = sorted( [f for f in os.listdir(args.in_image_dir) if f.endswith(('.jpg','.jpeg','.png','.gif','.bmp'))] )

    for image_name in tqdm(image_names):
        in_image_full_path = os.path.join(args.in_image_dir, image_name)
        original_img = cv2.imread(in_image_full_path)    
        mask = np.zeros(original_img.shape[:2], dtype="uint8")
        rect = (1, 1, mask.shape[1], mask.shape[0])
        fgModel = np.zeros((1, 65), dtype="float")
        bgModel = np.zeros((1, 65), dtype="float")

        (mask, bgModel, fgModel) = cv2.grabCut( original_img, mask, rect, bgModel, fgModel, iterCount=args.iter_count, mode=cv2.GC_INIT_WITH_RECT )
        binary_mask = np.where((mask == cv2.GC_BGD) | (mask == cv2.GC_PR_BGD),0, 1)
        binary_mask = (binary_mask * 255).astype("uint8")

        out_image_full_path = os.path.join(args.out_image_dir, image_name)
        cv2.imwrite( out_image_full_path, binary_mask )
