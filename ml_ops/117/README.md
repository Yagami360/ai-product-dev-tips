# DVC [Data Version Control] を使用して機械学習モデルの学習用データセットのバージョン管理を行う（リモートストレージとしてS3を使用する場合）

DVC [Data Version Control] は、リモートストレージ（S3や NASなど）と Git と連携して、機械学習モデルや学習用データセットのバージョン管理を行うためのツールでデータやモデルなどの大容量ファイルに特化した機能を提供している。

以下のような特徴がある。

- Git レポジトリと連携したデータセットバージョン管理
    - Git レポジトリとの連携し、大容量のデータセットを効率的に管理しながらバージョン管理を行うことができる。
    - データの変更履歴を追跡
    - チーム間でデータを共有

- リモートストレージと連携したデータセットバージョン管理
    - NAS [Network Attached Storage] や S3 [Simple Storage Service] などのリモートストレージと連携して、復数の開発者間でのデータセットの登録・取得・バージョン管理を行うことができる。
    - なお、リモートストレージを使用せずに DVC を利用することもできるが、登録したデータセットを他の開発者が取得できなくなるので、リモートストレージを使用することを推奨。

<img width="300" alt="image" src="https://github.com/user-attachments/assets/c91b0225-c771-4a38-a648-577a33edb911" />

## ディレクトリ構造

DVC 管理化の GitHub レポジトリのディレクトリ構造の例は、以下のようになる

```sh
${レポジトリ名}/
├── .git/                       # Gitリポジトリ（git init で生成）
├── .dvc/                       # DVCの設定とキャッシュ（dvc init で生成）
|   |-- .config                 # DVCの設定
|   |-- cache                   # DVCのキャッシュ（Gitで追跡しない）
|   |-- tmp                     # DVCの一時ファイル（Gitで追跡しない）
|   |-- .gitignore              # .dvcディレクトリ内のGitの除外設定
├── datasets/
│   ├── dataset.csv             # 実データ（Gitで追跡しない）
│   └── dataset.csv.dvc         # DVCファイル（Gitで追跡する）
├── .gitignore                  # Gitの除外設定
└── .dvcignore                  # DVCの除外設定
```

今回の例では、https://github.com/Yagami360/dvc-exercises に保存しています。

## 使用方法

1. DVC をインストールする
    ```bash
    pip install dvc
    ```

    今回のケースでは、DVC リモートストレージとして S3 を使用するので、S3 のバケット名を指定したものもインストールする。
    ```bash
    pip install dvc[s3]
    ```

1. DVC のバージョンを確認する
    ```bash
    dvc --version
    ```

1. Git リポジトリを作成する

    学習用データセットを利用する機械学習モデルのリポジトリを作成し、git リポジトリとして初期化する。（DVC は、Git リポジトリの中で動作するため、まず Git リポジトリを作成する必要がある。）
    ```bash
    git init
    ```

1. DVC を初期化する
    ```bash
    dvc init
    ``
    `dvc init` コマンド実行後に `.dvc` ディレクトリが生成される。
    `.dvc` ディレクトリの中には、DVCの設定とキャッシュが保存されており、Git で管理される。

1. S3 利用のための AWS の認証情報を設定する
    ```bash
    export AWS_ACCESS_KEY_ID="your-access-key"
    export AWS_SECRET_ACCESS_KEY="your-secret-key"
    ```

1. S3 バケットを作成する

1. DVC リモートストレージ（S3）用の DVC 設定を追加する
    ```bash
    dvc remote add -d s3 s3://${S3バケット名}/フォルダ名
    ```
    `dvc remote add` コマンド実行後に、`.dvc/config` ファイルに、リモートストレージの設定が追加される。

1. データセットを DVC バージョン管理化に追加する
    ```bash
    dvc add datasets/dataset.csv
    ```

    `dvc add` コマンド実行後に、`dataset.csv.dvc` ファイルが生成される。`dataset.csv.dvc` ファイルが Git で管理され、元の `dataset.csv` ファイルは Git で管理されない動作になる。（内部的な動作としては、`datasets/.gitignore` ファイルに `dataset.csv` ファイルが追加され、Git で管理されないようになる）

    なお、`*.dvc` ファイルの中身は、以下のようになっており、データのバージョン管理や共有を行なうための各種情報が保存されている。
    ```yml
    outs:
    - md5: f98e49a65ba24fb2b43f1a67b545f568
        size: 3867
        hash: md5
        path: dataset.csv
    ```

    また、`dvc add` コマンド実行後に、`.dvc/cache` ディレクトリに `dataset.csv` ファイルのキャッシュ（ハッシュ値）が保存される。
    このキャッシュは、`dvc pull` コマンド実行時に、リモートストレージ等からデータセットをダウンロードする際に使用される。

1. DVC リモートストレージ（S3）にデータセットを保存する
    ```bash
    dvc push
    ```

1. Git リポジトリにデータセット追加の変更をコミットする
    ```bash
    git add .
    git commit -m "Add dataset by DVC"
    git push origin master
    ```

1. データセットをダウンロードする
    ```bash
    dvc pull
    ```
    `dvc pull` コマンドを実行することで、DVCリモートストレージ（S3）からデータセットがダウンロードされ、ローカルストレージの `datasets/` ディレクトリに保存される。

## 参考サイト

- https://qiita.com/meow_noisy/items/a644547930e6f2dea12d
