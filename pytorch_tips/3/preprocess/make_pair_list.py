import os
import argparse
from tqdm import tqdm
import random
import itertools

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_dir", type=str, default="../dataset/templete_dataset")
    parser.add_argument("--pairs_list_name", type=str, default="pairs.csv")
    parser.add_argument("--valid_rate", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=8)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

    image_dir = os.path.join( args.dataset_dir, "image" )
    target_dir = os.path.join( args.dataset_dir, "target" )
    image_names = sorted( [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.png'))] )
    target_names = sorted( [f for f in os.listdir(target_dir) if f.endswith(('.jpg', '.png'))] )

    pair_names = []
    for i in tqdm(range(len(image_names))):
        pair_names.append( [image_names[i], target_names[i]] )

    pair_names_valid = random.sample(pair_names, int(len(pair_names) * args.valid_rate))

    with open( os.path.join( args.dataset_dir, "train_" + args.pairs_list_name ), "w" ) as f:
        f.write( "image_name,target_name\n" )
        for pair_name  in tqdm(pair_names):
            f.write( pair_name[0] + "," + pair_name[1] + "\n")

    with open( os.path.join( args.dataset_dir, "valid_" + args.pairs_list_name ), "w" ) as f:
        f.write( "image_name,target_name\n" )
        for pair_name  in tqdm(pair_names_valid):
            f.write( pair_name[0] + "," + pair_name[1] + "\n")
