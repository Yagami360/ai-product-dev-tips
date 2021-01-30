# GitHub Actions を用いた CI/CD
他の一般的な CI/CD ツールと同様にして、リポジトリに対するプッシュやプルリクエストといった操作、もしくは指定した時刻になるといったイベントをトリガーとして、あらかじめ定義しておいた処理を実行することで CI/CD を実現できる。<br> 
GitHub だけで CI/CD 的な機能を実現できるのがメリット。利用料金も無料。CI/CD ツールとしては、現状 GitHub Actions を使うのがベストっぽい。

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
1. 作成した Workflow ファイルを git push する<br>
1. GitHub リポジトリの Actions タブから、実行されたワークフローのログを確認<br>

## ■ Workflow ファイル（yaml形式）の中身

- Workflow ファイルの設定例
    ```yml
    name: Build and Deploy  # ワークフローの名前
    on:                     # ワークフローをトリガーするイベントを定義
        push:                       # master ブランチに新しいコードが push された時にトリガー
            branches:
            - master
    jobs:                   # job（ワークフローの中で実行される処理のひとまとまり）を定義。
        build:                      # Build ジョブを定義 
            name: Build
            runs-on: ubuntu-latest      # ジョブを実行するマシン
            steps:                      # ジョブの step（ジョブの中で実行される一連のタスク）を定義
            - name: Checkout Repo
                uses: actions/checkout@master   # use タグで使用する Actions を指定 / actions/checkout という GitHub リポジトリにあるアクションの master ブランチのコードを使用
            - name: Install Dependencies
                run: npm install                # run タグで使用するシェルコマンドを指定 / 
            - name: Build
                run: npm run build
            - name: Archive Production Artifact
                uses: actions/upload-artifact@master
                with:
                name: public
                path: public    
        deploy:                     # Deploy ジョブを定義 
            name: Deploy
            needs: build
            runs-on: ubuntu-latest
            steps:
            - name: Checkout Repo
                uses: actions/checkout@master           # 使用する Action を定義。
            - name: Download Artifact
                uses: actions/download-artifact@master
                with:
                name: public
                path: public
            - name: Deploy to Firebase
                uses: w9jds/firebase-action@master
                with:
                args: deploy
                env:
                FIREBASE_TOKEN: ${{ secrets.FIREBASE_TOKEN }}
            - name: run_shell
                run:                                    # 使用するシェルコマンドを定義
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
        push:                   # master ブランチに新しいコードが push された時にトリガー
            branches:
            - master
    ```

### ◎ Build ジョブ
xxx

### ◎ Deploy ジョブ
xxx

## ■ 参考サイト
- https://docs.github.com/ja/actions/quickstart
- https://qiita.com/kozukata1993/items/fbbdec14645c3f6f2fb2
- https://knowledge.sakura.ad.jp/23478/

