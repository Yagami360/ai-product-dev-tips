import os
import argparse
from tqdm import tqdm
from PIL import Image

from multiprocessing import Pool
import multiprocessing as multi

def wrapper(args):
    return process(*args)

def process( image_dir, image_out_dir, image_name ):
    # 並列化処理を行わない場合の for ループ内の処理に対応
    image_path = os.path.join(image_dir, image_name)
    image_out_path = os.path.join(image_out_dir, image_name)
    img = Image.open(image_path)
    resized = img.resize(( img.size[0]//2, img.size[1]//2 ))
    resized.save(image_out_path)
    return 0    # 正常終了

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='resize oversize images')
    parser.add_argument('image_dir', type=str, help='path of input image dir')
    parser.add_argument('image_out_dir', type=str, help='path of ouput image dir')
    parser.add_argument("--process_num", type=int, default=None)    # None で利用可能な CPU の最大数
    args = parser.parse_args()

    image_dir = args.image_dir
    image_out_dir = args.image_out_dir
    if not os.path.isdir(image_out_dir):
        os.mkdir(image_out_dir)

    image_names = [f for f in os.listdir(image_dir) if f.endswith(('.jpeg', '.png'))]

    # process_image() に渡す、引数リスト
    args_list = [ [image_dir, image_out_dir, image_names[i]] for i in range(len(image_names)) ]

    print( "multi.cpu_count() :", multi.cpu_count() )
    with Pool(args.process_num) as p:
        imap = p.imap(wrapper, args_list)
        output = list( tqdm(imap, total=len(args_list)) )

    n_ok = output.count(0)
    n_ng = output.count(-1)

