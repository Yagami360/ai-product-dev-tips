import os
import argparse
from tqdm import tqdm
from PIL import Image

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='resize oversize images')
    parser.add_argument('image_dir', type=str, help='path of input image dir')
    parser.add_argument('image_out_dir', type=str, help='path of ouput image dir')
    args = parser.parse_args()

    image_dir = args.image_dir
    image_out_dir = args.image_out_dir
    if not os.path.isdir(image_out_dir):
        os.mkdir(image_out_dir)

    image_names = [f for f in os.listdir(image_dir) if f.endswith(('.jpeg', '.png'))]

    for image_name in tqdm(image_names):
        image_path = os.path.join(image_dir, image_name)
        image_out_path = os.path.join(image_out_dir, image_name)
        img = Image.open(image_path)
        resized = img.resize(( img.size[0]//2, img.size[1]//2 ))
        resized.save(image_out_path)
