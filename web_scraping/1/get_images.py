import os, argparse
from tqdm import tqdm
from PIL import Image

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("in_human_dir", type=str)
    parser.add_argument("in_human_parsing_dir", type=str)
    parser.add_argument("--out_dir", type=str, default="results")
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

    if not os.path.isdir(args.out_dir):
        os.mkdir(args.out_dir)

