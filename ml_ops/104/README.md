# Hugging Face Hub の基本的な使用方法

## 使用方法

### 事前準備

1. Hugging Face のアカウント作成<br>
    Hugging Face の公式ページからアカウントを作成する

1. Hugging Face の Python SDK と CLI をインストールする<br>
    ```sh
    pip3 install huggingface_hub
    ```

### HuggingFace Hub レポジトリを作成する

1. 【オプション】Hugging Face にログインする<br>
    - コンソール UI を使用する場合<br>
        コンソール UI の[ログインページ](https://huggingface.co/login)からログインする

    - CLI を使用する場合
        ```sh
        huggingface-cli login

        # or using an environment variable
        huggingface-cli login --token $HUGGINGFACE_TOKEN
        ```

    - Python SDK を使用する場合
        ```python
        from huggingface_hub import login
        login()
        ```

1. HuggingFace Hub レポジトリを作成する
    - コンソール UI を使用する場合<br>
        <img width="500" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/9b2e1e21-2a14-47c3-abff-f95b99294993"><br>
        <img width="671" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/2bbd55b2-628d-4a12-baff-61d55b3a3286"><br>
        https://huggingface.co/new からレポジトリを作成する<br>

    - CLI を使用する場合
        ```sh
        huggingface-cli repo create ${REPO_NAME} --type ${REPO_TYPE} --
        ```
        - `--type`: レポジトリのタイプ
            - `model`: 機械学習モデルのレポジトリ
            - `dataset`: データセットのレポジトリ
            - `space`: アプリケーションのレポジトリ

    - Python SDK を使用する場合
        ```python
        ```

### HuggingFace Hub レポジトリにファイルを git push する

1. HuggingFace Hub レポジトリを git clone する
    ```sh
    git clone https://huggingface.co/<your-username>/<your-model-name>
    cd <your-model-name>
    ```

    - 例
        ```sh
        git clone https://huggingface.co/Yagami360/huggingface_repo_model_test
        cd huggingface_repo_model_test
        ```

1. 【オプション】巨大ファイルをレポジトリで管理する場合は、以下のコマンドを実行する
    ```sh
    git lfs install                             # git lfs で 10MB 以上のファイル管理
    huggingface-cli lfs-enable-largefiles .     # 5GB より大きいファイルを管理
    ```

1. CHuggingFace Hub レポジトリにファイルを追加して git push する
    ```sh
    git add .
    git commit -m "first commit"
    git push
    ```
    
### Hugging Face のレポジトリからファイル（モデル等）をダウンロードする

例えば、[Pegasus](https://huggingface.co/google/pegasus-xsum) という名前のモデルから、Tensorflow での学習済みモデルのファイル `tf_model.h5` をダウンロードする

- コンソール UI を使用する場合<br>

- CLI を使用する場合<br>
    ```sh
    ```

- Python SDK を使用する場合<br>
    ```python
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
    ```

## 参考サイト

- https://huggingface.co/docs/hub/repositories-getting-started
- https://huggingface.co/docs/huggingface_hub/package_reference/overview
