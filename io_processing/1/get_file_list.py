import os
import argparse
import shutil

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument( "in_dir", help="input a directory", type=str )
    parser.add_argument( "out_dir", help="output a directory", type=str )
    args = parser.parse_args()

    in_dir = args.in_dir
    out_dir = args.out_dir

    # 出力ディレクトリは存在するかチェックし、存在しない場合はフォルダを作成する処理を入れること
    # フォルダの存在確認は、`os.path.isdir()` 又は `os.path.exists()` で行える。
    #if( os.path.isdir(out_dir) == False ):
    if ( os.path.exists(out_dir) == False ):
        # フォルダの作成は、`os.makedirs()` で行える。
        os.makedirs(out_dir)

    # フォルダ内の全ファイルは、`os.listdir()` で取得出来る。
    # ソートされていないことに注意（機械学習のタスクにおいてlistがソートされていないと，処理が中断された時に再開ができない）
    # サブディレクトリも取得されていることに注意
    files = os.listdir(in_dir)
    print( "files :", files )

    # a,b, .. 順にソート
    files_sorted = sorted( os.listdir(in_dir) )
    print( "files_sorted :", files_sorted )

    # ファイルのみの一覧を取得
    files_only = []
    for f in os.listdir(in_dir):
        if( os.path.isfile( os.path.join(in_dir,f) ) ):
            files_only.append(f)
    
    print( "files_only :", files_only )

    # ファイルのみ出力
    for f in files_only:
        full_path = os.path.join( in_dir, f )
        # コピーするときは、コピー元にファイルが存在するか `os.path.isfile()` で確認すること
        if( os.path.isfile(full_path) ):
            shutil.copy( full_path, out_dir )
