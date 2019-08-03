import os
import argparse
import shutil
from tqdm import tqdm

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_dir', type=str )
    parser.add_argument('out_dir', type=str )
    parser.add_argument('--n_split', type=int, default = 4 )
    args = parser.parse_args()

    in_dir = args.in_dir
    out_dir = args.out_dir
    n_split = args.n_split

    if( os.path.exists(out_dir) == False ):
        os.mkdir( out_dir )

    in_dirs = []
    for i in range(0,n_split):
        in_dirs.append( os.path.join(in_dir, "%02d" % i) )

    files = []
    for i_dir in in_dirs:
        in_files = sorted( os.listdir( i_dir ) )
        files.append( in_files )

    for i_dir, in_files in zip( tqdm(in_dirs), files ):
        for f in in_files:
            full_file_name = os.path.join(i_dir, f)
            if (os.path.isfile(full_file_name)):
                shutil.move(full_file_name, out_dir )

    for i_dir in in_dirs:
        if (os.path.isdir(i_dir) == True ):
            os.rmdir( i_dir )
