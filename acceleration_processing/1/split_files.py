import os
import argparse
from tqdm import tqdm
import shutil


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument( "in_dir", help="input a directory", type=str )
    parser.add_argument( "out_dir", type=str )
    parser.add_argument('--n_split', help="number of split directory", type=int, default = 4)
    args = parser.parse_args()

    in_dir = args.in_dir
    out_dir = args.out_dir
    n_split = args.n_split

    if( os.path.exists(out_dir) == False ):
        os.mkdir( out_dir )

    split_dirs = []
    for i in range(0,n_split):
        # "%02d" でフォルダ名のインデックスを2桁で表示
        split_dirs.append( os.path.join(out_dir, "%02d" % i) )

    # 分割したフォルダを生成
    for dir in split_dirs:
        if( os.path.exists(dir) == False ):
            os.mkdir( dir )

    # 分割前のフォルダの全ファイル一覧を取得（ソートすること）
    files = sorted(os.listdir( in_dir ))    # @

    split_size = int( len(files)/n_split )  # 各フォルダの分割数
    print( "split_size :", split_size )

    split_files = []
    split_files.append( files[0:split_size] )   # 0番目のフォルダ
    print( "{} / len(split_files[0])={}".format( 0, len(split_files[0]) ) )
    print( "{} / split_files[0]={}".format( 0, split_files[0]) )

    # 0 番目 ~ n_split-1 番目のフォルダ
    for i in range(1,n_split-1):
        split_files.append( files[split_size*i:split_size*(i+1)] )  # @
        print( "{} / len(split_files[{}])={}".format( i, i, len(split_files[i]) ) )
        print( "{} / split_files[{}]={}".format( i, i, split_files[i] ) )

    # あまりファイルは最後のフォルダに追加
    split_files.append( files[split_size*(n_split-1):] )
    print( "{} / len(split_files[{}])={}".format( n_split-1, n_split-1, len(split_files[-1]) ) )
    print( "{} / split_files[{}]={}".format( n_split-1, n_split-1, split_files[-1]) )

    # in_dir にあるファイルを out_dir の分割したフォルダ split_dirs にコピー or 移動
    for s_dir, s_files in zip( tqdm(split_dirs), split_files ):
        for f in s_files:
            full_file_name = os.path.join(in_dir, f)
            if (os.path.isfile(full_file_name)):
                shutil.copy(full_file_name, os.path.join(s_dir, f) )
                #shutil.move(full_file_name, os.path.join(s_dir, f) )

    """
    # shutil.move() した場合の予備の動作として、残ったいるファイルを最後のフォルダに入れる。
    for f in sorted( os.listdir( in_dir ) ):
        full_file_name = os.path.join(in_dir, f)
        if (os.path.isfile(full_file_name)):
            shutil.move(full_file_name, os.path.join(split_dirs[-1], f) )
    """