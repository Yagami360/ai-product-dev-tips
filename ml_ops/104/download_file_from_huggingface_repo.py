import os
import argparse

from huggingface_hub import hf_hub_download

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo_id', type=str, default="google/pegasus-xsum")
    parser.add_argument('--file_name', type=str, default="tf_model.h5")
    parser.add_argument('--out_dir', type=str, default="out_dir/")
    args = parser.parse_args()

    if not os.path.exists(args.out_dir):
        os.mkdir(args.out_dir)

    # レポジトリからファイルをダウンロード
    try:
        hf_hub_download(repo_id=args.repo_id, filename=args.file_name, local_dir=args.out_dir)
    except Exception as e:
        print(f"Exception was occured | {e}")
        exit(1)

    exit(0)