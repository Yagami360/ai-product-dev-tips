# GitHub Actions を用いた CI/CD
他の一般的な CI/CD ツールと同様にして、リポジトリに対するプッシュやプルリクエストといった操作、もしくは指定した時刻になるといったイベントをトリガーとして、あらかじめ定義しておいた処理を実行することで CI/CD を実現できる。<br> 
GitHub だけで CI/CD 的な機能を実現できるのがメリット。利用料金も無料。CI/CD ツールとしては、現状 GitHub Actions を使うのがベストっぽい。

- GitHub Actions を用いた CI/CD のサンプルコード<br>
  -  https://github.com/Yagami360/github-actions_exercises<br>

## ■ GitHub Actions の基礎事項

- Workflow（ワークフロー）<br>
    実行する処理とその処理を実行する条件を定義したもの。<br>
    ワークフローは yaml ファイルで記述し、リポジトリ内の `.github/workflows/` ディレクトリ内に保存することで実行できるようになる。<br>

- jobs（ジョブ）<br>
    ワークフローの中で実行される処理のひとまとまり。<br>
    Workflow ファイル（yaml形式）の `jobs` タグで指定される。<br>
    - steps（ステップ）<br>
        ジョブの中で実行される一連のタスク。Workflow ファイル（yaml形式）の `jobs` タグ内の `steps` タグで指定される。<br>

- Action（アクション）<br>
    あらかじめ定義済みの一連の処理。<br>
    例えば、"checkout" という Action では、指定したリポジトリからソースコードをチェックアウトする処理が定義されている。ユーザーが独自の Action を作成することも可能<br>
    定義済みの Actions は、Workflow ファイル（yaml形式）内の、 `steps.uses` タグ内で使用することができる。

## ■ GitHub Actions での CI/CD 構築手順

1. Workflow ファイルを作成する<br>
    Workflow ファイル（yaml 形式）をリポジトリ内の `.github/workflows/` ディレクトリ上に作成する<br>
1. 作成した Workflow ファイルをレポジトリに git push する<br>
1. Workflow ファイルで定義したトリガーイベントが git push であれば、Workflow ファイルをレポジトリに git push した時点でワークフローが自動的に実行される。<br>
1. GitHub リポジトリの Actions タブから、実行されたワークフローのログを確認<br>
    <img src="https://user-images.githubusercontent.com/25688193/106348714-90cbd680-630b-11eb-833c-d242256392d4.png" width="500"><br>
    <img src="https://user-images.githubusercontent.com/25688193/106348762-0172f300-630c-11eb-997a-8f2515714790.png" width="500"><br>
1. ワークフローステータスのバッジ（badge）を表示したい場合は、各ワークフローの「Create status badge」ボタンをクリックして画像リンクを取得して、`README.md` などに貼り付ける。<br>
    <img src="https://user-images.githubusercontent.com/25688193/106349657-ff606280-6312-11eb-8d07-a00ec899e05b.png" width="500"><br>
    この際に、得られた画像リンクを `[${画像リンク}](${ワークフローのリンク})` の形式に置き換えることにより、画像ボタンをクリックすることで該当するワークフローに飛べるようにしておくと便利。

## ■ Workflow ファイル（yaml形式）の中身

- Workflow ファイルの設定例
    ```yml
    name: build and deploy on mac   # ワークフローの名前
    on: [push]                      # ワークフローをトリガーするイベントを定義 / 新しいコードが push された時にトリガー
    jobs:                           # job（ワークフローの中で実行される処理のひとまとまり）を定義。
    build:                          # Build ジョブを定義 
      name: Build         
      runs-on: macos-latest         # ジョブを実行するマシン
      steps:
      - uses:                           # use タグで使用する Actions を指定
        actions/checkout@v2                 # actions/v2 という GitHub リポジトリにあるアクションの v2 ブランチのコードを使用
      - name: Setup python 3.6          # python 環境の構築
        uses: actions/setup-python@v2
        with:
        python-version: '3.6.9'
        architecture: x64
      - name: Install dependencies      # 依存ライブラリのインストール
        run:                                # run タグで使用するシェルコマンドを指定 / 
          python -m pip install --upgrade pip
          pip install tqdm
          pip install Pillow
          pip install opencv-python
      - name: Run test scripts          # 独自のテストスクリプトの自動実行
        run:
          python src/test.py --debug
    ```

### ◎ on トリガー（ワークフローの起動トリガー）

- １つのイベントのみ指定する場合<br>
    ```yml
    on: push
    ```

- 複数のイベントを指定する場合<br>
    ```yml
    on: [push, pull_request]
    ```

- push する branch も指定する場合<br>
    ```yml
    on:                     # ワークフローをトリガーするイベント
      push:                 # master ブランチに新しいコードが push された時にトリガー
        branches:
          - master
    ```

- 特定のファイルのみの push をトリガーとする場合 
	```yml
  	on:
      push:
        paths:
          - '*.py'  # python ファイルの push のみをトリガー
	```

### ◎ ジョブ

- ジョブの設定例
    ```yml
    build:                          # ジョブIDを定義 
      name: Build         
      runs-on: macos-latest         # ジョブを実行するマシン
      steps:
      - uses:                         # use タグで実行する Actions を指定
        actions/checkout@v2             # actions/v2 という GitHub リポジトリにあるアクションの v2 ブランチのコードを使用
      - name: Setup python 3.6        # python 環境の構築
        uses: actions/setup-python@v2
        with:
        python-version: '3.6.9'
        architecture: x64
      - name: Install dependencies    # 依存ライブラリのインストール
        run:                            # run タグで実行するシェルコマンドを指定 / 
          python -m pip install --upgrade pip
          pip install tqdm
          pip install Pillow
          pip install opencv-python
      - name: Run test scripts        # 独自のテストスクリプトの自動実行
        run:
          python src/test.py --debug
    ```

- `jobs.${JOB_ID}` : ジョブを一意に特定するためのID。上記例では `JOB_ID=build`
- `jobs.${JOB_ID}.runs-on` : ジョブを実行するマシンを定義
    - `ubuntu-latest` : Ubuntu
    - `macos-latest` : MacOS
- `jobs.${JOB_ID}.steps` : ステップを定義
- `jobs.${JOB_ID}.steps.run` : 実行するシェルコマンド
- `jobs.${JOB_ID}.steps.uses` : 実行する Action を定義


## ■ 参考サイト
- https://docs.github.com/ja/actions/quickstart
- https://qiita.com/kozukata1993/items/fbbdec14645c3f6f2fb2
- https://knowledge.sakura.ad.jp/23478/
- https://murabitoleg.com/githubactions-python/
