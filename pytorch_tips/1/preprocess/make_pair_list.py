import os
import argparse
from tqdm import tqdm
import random
import itertools

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_dir", type=str, default="../dataset/sample_dataset_n10")
    parser.add_argument("--pairs_list_name", type=str, default="pairs.csv")
    parser.add_argument("--valid_rate", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=8)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

    inputA_dir = os.path.join( args.dataset_dir, "inputA" )
    inputB_dir = os.path.join( args.dataset_dir, "inputB" )
    inputC_dir = os.path.join( args.dataset_dir, "inputC" )
    target_dir = os.path.join( args.dataset_dir, "target" )

    inputA_names = sorted( [f for f in os.listdir(inputA_dir) if f.endswith(('.jpg', '.png'))] )
    inputB_names = sorted( [f for f in os.listdir(inputB_dir) if f.endswith(('.jpg', '.png'))] )
    inputC_names = sorted( [f for f in os.listdir(inputC_dir) if f.endswith(('.jpg', '.png'))] )
    target_names = sorted( [f for f in os.listdir(target_dir) if f.endswith(('.jpg', '.png'))] )

    pair_names = []
    for i in tqdm(range(len(inputA_names))):
        pair_names.append( [inputA_names[i], inputB_names[i], inputC_names[i], target_names[i]] )

    pair_names_valid = random.sample(pair_names, int(len(pair_names) * args.valid_rate))

    with open( os.path.join( args.dataset_dir, "train_" + args.pairs_list_name ), "w" ) as f:
        f.write( "inputA_name,inputB_name,inputC_name,target_name\n" )
        for pair_name  in tqdm(pair_names):
            f.write( pair_name[0] + "," + pair_name[1] + "," + pair_name[2] + "," + pair_name[3] + "\n")

    with open( os.path.join( args.dataset_dir, "valid_" + args.pairs_list_name ), "w" ) as f:
        f.write( "inputA_name,inputB_name,inputC_name,target_name\n" )
        for pair_name  in tqdm(pair_names_valid):
            f.write( pair_name[0] + "," + pair_name[1] + "," + pair_name[2] + "," + pair_name[3] + "\n")
