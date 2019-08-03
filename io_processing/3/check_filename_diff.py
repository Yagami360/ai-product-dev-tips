import os
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument( "dir1", type=str )
    parser.add_argument( "dir2", type=str )
    args = parser.parse_args()

    dir1 = args.dir1
    dir2 = args.dir2

    # os.listdir() で取得してきたファイル一覧を set 型にする。
    files_set1 = set( os.listdir("dir1") )
    files_set2 = set( os.listdir("dir2") )

    print( "files_set1 :", files_set1 )
    print( "files_set2 :", files_set2 )

    # set 型の差を取り、差分を確認出来る。
    print( "len( files_set1 - files_set2 ) :", len( files_set1 - files_set2 ) )
    print( "len( files_set2 - files_set1 ) :", len( files_set2 - files_set1 ) )
    print( "dir1 に存在して dir2 に存在しないファイル :", files_set1 - files_set2 )
    print( "dir2 に存在して dir1 に存在しないファイル :", files_set2 - files_set1 )
