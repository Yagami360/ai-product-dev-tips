# 【Docker】 Docker の基本事項・基本コマンド

## ■ Docker イメージ関連

### ◎ Docker イメージのダウンロード

- `$ docker pull ${IMAGE_NAME}`

    ```sh
    # example
    $ docker pull pytorch/pytorch
    ```

### ◎ Docker イメージの検索

- `$ docker search ${SARCH_WORDS}`

    ```sh
    # example
    $ docker search pytorch

    NAME                            DESCRIPTION                                     STARS               OFFICIAL            AUTOMATED
    pytorch/pytorch                 PyTorch is a deep learning framework that pu…   149                                     
    floydhub/pytorch                pytorch                                         41                                      [OK]
    anibali/pytorch                 Docker images for the PyTorch deep learning …   11                                      [OK]
    ...
    ```

### ◎ Docker イメージの作成

- `$ docker build ./ -t ${IMAGE_NAME}`
    - 作成するイメージの構成を定義した Dockerfile が存在するディレクトリで、上のコマンドを実行
    ```sh
    $ docker build ./ -t ml_exercises_pytorch_image

    Sending build context to Docker daemon  607.1MB
    Step 1/7 : FROM pytorch/pytorch
     ---> ba2da111b833
    Step 2/7 : ARG ROOT_DIR=/workspace
     ---> Running in 190f0a9adf81
    ...
    ```

### ◎ 作成した Docker イメージの確認

- `$ docker images`

    ```sh
    # example
    $ docker images

    REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
    pytorch/pytorch     latest              ba2da111b833        6 weeks ago         4.32GB
    ```

### ◎ Docker イメージの削除

- `$ docker rmi [イメージID]`

    ```sh
    $ docker images
    REPOSITORY                   TAG                 IMAGE ID            CREATED             SIZE
    ml_exercises_pytorch_image   latest               52849ea557ed        7 weeks ago         4.54GB
    <none>                       <none>

    $ docker rmi 52849ea557ed
    ````

### ◎ Dockerfile 関連


## ■ コンテナ関連

### ◎ コンテナを起動

- `$ docker run ${CONTAINER_NAME} ${IMAGE_NAME} /bin/bash`
    - `${CONTAINER_NAME}` : コンテナ名
    - `${IMAGE_NAME}` : docker イメージ名
    - `-i` オプション : ホストマシンとコンテナの双方向に接続できるようにする
    - `-t` オプション : コンテナ内に擬似的なターミナルを割り当て（コンテナ内でターミナルを使用できるようにする？）
    - `--rm` オプション : コンテナから抜けるとコンテナを自動で削除する
    - `--name` オプション : コンテナの名前を指定する
    - `-v ${ホストマシンの同期するディレクトリ}:${Dockerコンテナ内の同期するディレクトリ}` オプション : ホストマシンとコンテナの同期して、ホストマシンで編集した内容が、即時コンテナにも反映されるようにする。
    - `-p ${ホストマシンのIPアドレス}:${Dockerコンテナ内の同期するディレクトリ}`
        - ホスト側のディレクトリも絶対パスで指定する必要あり。
    - `-d` オプション : バックグラウンドでコンテナを作成
    - `/bin/bash` : ターミナル（bash）を起動
    - `exit` コマンドでコンテナから抜ける

- コンテナを起動（非同期）：<br>
    `-v` オプションを指定しない `docker run` では、コンテナを終了する度に、コンテナ環境で作成したファイルが消えてしまう。また、ホストマシンでエディタなどで修正した変更が、リアルタイムでコンテナ環境に適用されない。
    ```sh
    # example1
    $ docker run -it --rm --name pytorch_container pytorch/pytorch /bin/bash

    # 接続されるコンテナのディレクトリは、デフォルトで workspace ディレクトリ
    root@1f46a99c39b0:/workspace#
    root@1f46a99c39b0:/workspace# cd ..
    root@023a52ee99a8:/# ls
    bin  boot  dev  etc  home  lib  lib64  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var  workspace
    root@023a52ee99a8:/# exit
    ```

- コンテナを起動（同期）：<br>
    一般的には、`-v` オプションを指定した `docker run -v ${ホストマシンの同期するディレクトリ}:${Dockerコンテナ内の同期するディレクトリ}` で、 ホストマシンとコンテナのディレクトリを同期することで、 コンテナを終了してもコンテナ側で作成＆修正した内容が保存されるようにする。更に、ホストマシンでエディタなどで修正した変更が、リアルタイムでコンテナ環境にも適用されるようになる。
    ```sh
    # example
    # 基本的にホストディレクトリ名とコンテナディレクトリ名は同じ方がわかりやすい
    $ HOST_DIR=${PWD}
    $ CONTAINER_DIR=workspace/GAN_DCGAN_PyTorch
    $ docker run -it --rm -v ${HOST_DIR}:${CONTAINER_DIR} --name pytorch_container pytorch/pytorch /bin/bash

    # 接続されるコンテナのディレクトリは、デフォルトで workspace ディレクトリ
    root@31121a30cb2b:/workspace# ls
    GAN_DCGAN_PyTorch
    root@31121a30cb2b:/workspace# cd GAN_DCGAN_PyTorch/
    root@31121a30cb2b:/workspace/GAN_DCGAN_PyTorch# exit
    ```

### ◎ 起動済みのコンテナ内に入る（バックグラウンドでコンテナ立ち上げ -d をした場合に使用）

- `$ docker exec -it ${CONTAINER_ID} /bin/sh`
    - `/bin/sh` :  : ターミナル（bash）を起動


### ◎ 起動中のコンテナ確認

- `$ docker ps`

    ```sh
    # example
    $ docker ps

    CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS               NAMES
    62415f8a2996        pytorch/pytorch     "/bin/bash"         9 seconds ago       Up 8 seconds                            pytorch_container
    ```

### ◎ コンテナを停止

- `$ docker stop ${CONTAINER_ID}`


## ■ Dockerfile 関連

- Dockerfile の一例

    ```Dockerfile
    #-----------------------------
    # Docker イメージのベースイメージ
    #-----------------------------
    # pytorch 環境をベースにする
    FROM pytorch/pytorch

    #-----------------------------
    # ARGで変数を定義
    # buildする時に変更可能
    #-----------------------------
    # コンテナ内のディレクトを決めておく
    ARG ROOT_DIR=/workspace

    #-----------------------------
    # RUN : コマンド命令
    # ここに記述したコマンドを実行してミドルウェアをインストールし、imageのレイヤーを重ねる
    #-----------------------------
    # apt-get update : インストール可能なパッケージの「一覧」を更新する。
    # apt-get install : インストールを実行する。
    # -y : 問い合わせがあった場合はすべて「y」と答える
    # python & python3-pipのインストール
    RUN apt-get update && apt-get install -y \
        python3 \
        python3-pip \
        # imageのサイズを小さくするためにキャッシュ削除
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/* \
        # pipのアップデート
        && pip install --upgrade pip

    #-----------------------------
    # 環境変数
    #-----------------------------
    # 日本語対応
    ENV PYTHONIOENCODING utf-8

    #-----------------------------
    # Dockerfileを実行したディレクトにあるファイルのコピー
    # COPY ${コピー元（ホスト側にあるファイル）} ${コピー先（）}
    #-----------------------------
    COPY requirements.txt ${ROOT_DIR}

    #-----------------------------
    # ライブラリのインストール
    #-----------------------------
    WORKDIR ${ROOT_DIR}
    RUN pip install -r requirements.txt

    #-----------------------------
    # ディレレクトリの移動
    #-----------------------------
    WORKDIR ${ROOT_DIR}/MachineLearning_Exercises_Python_PyTorch
    ```

- FROM コマンド : 
- ARG コマンド : 
- ENV コマンド : 
- CMD コマンド : コンテナが作成された後で実行するコマンドを指定する

## ■ Docker-Compose
複数コンテナを一元管理するコンポーネント。それと同時に docker イメージの作成からコンテナの起動までを一括して行える機能もある。

### ◎ Docker-Compose でのイメージ作成 ＆ コンテナ立ち上げ

- `$ docker-compose up -d`
    - 作成する docker-compose.yml の構成を定義した docker-compose ファイルが存在するディレクトリで、上のコマンドを実行
    - `-d` : バックグラウンドでコンテナ立ち上げ

### ◎ コンテナの駆動状況の確認

- `$ docker-compose ps`


### ◎ コンテナでのプログラム実行

- `$ docker-compose run ${PROGRAM}`
    - `--rm` オプション：コンテナ終了時にコンテナを自動的に削除
    - `-v` オプション : ホストの任意のパスをコンテナの任意のパスにマウントさせる（＝認識させる）

### ◎ docker-compose.yml

- docker-compose.yml の一例
    ```yml
    version: "3"
    services:
    app:
        container_name: "ml_exercises_container"
        build:
        context: .
        dockerfile: ./Dockerfile
        image: ml_exercises_pytorch_image
        volumes: 
            - ${PWD}:/workspace
        tty: true
        command: /bin/bash
    ```

docker-compose.yml は基本的に docker run のオプションと対応している。

- version : docker-compose のバージョン（古いバージョンだと、nvidia-docker は動かない）
- services: app : サービスの名称・ここ被ると他のdocker-composeで操作される・
- container_name : コンテナ名
- image : Docker イメージ名
- volumes ${HOST_DIR}:${CONTAINER_DIR} : ホストPCとコンテナディレクトリ間でデータをやり取りするディレクトリ。
- runtime: nvidia-docker を動かすときなどに必要（nvidia-docker 2.0）
- tty: true : false の場合 docker が起動即終了するので，立ち上げてすぐプログラムを走らせて終了，みたいな使い方じゃなければ，trueにして，あとからexecコマンドで動作させる．
- ports : ホストPCとコンテナ間でつなげたいポート
- command: docker-compose を起動した際に動作させるターミナル

## ■ nvidia-docker
nvidia-docker を使用すると、起動中のコンテナ内から直接 CUDA 経由で GPU にアクセスできるようなる。これにより例えば、起動中のコンテナ内から nvidia-smi 等の GPU コマンドが使用できるようになる。

### ◎ nvidia-docker 1.0

- `$ nvidia-docker` という docker ラッパーコマンドを使用する。

### ◎ nvidia-docker 2.0

- `$ nvidia-docker` は廃止
- `$ docker run --runtime=nvidia` というコマンドで実行可能になっている。（通常の `docker run` に `--runtime=nvidia` を指定）

### ◎ Docker 19.03 以降 + nvidia-container-toolkit

- `nvidia-docker` は廃止
- `--runtime=nvidia` も廃止
- GPU コンテナを実行するには Docker 19.03 でサポートされた`--gpus` オプションを使用。

```sh
# 例 : 全ての GPU を認識
$ docker run --gpus all nvidia/cuda:9.0-base nvidia-smi
```

### ◎ nvidia-docker をベースにした独自の Docker image の作成 （GPUコンテナの作成）

- ベースイメージ（FROM）
    - CUDA 10.0 の場合 : `FROM nvidia/cuda:10.0-cudnn7-devel-ubuntu16.04`

- 環境変数 : `ENV NVIDIA_VISIBLE_DEVICES`<br>
    コンテナ内から指定のGPU が確認できるように環境変数 NVIDIA_VISIBLE_DEVICES で指定する。
    ```Dockerfile
    # コンテナ内から全ての GPU を確認できるようにする。
    ENV NVIDIA_VISIBLE_DEVICES all
    ```

- 環境変数 : `ENV NVIDIA_DRIVER_CAPABILITIES`<br>
    ```Dockerfile
    # utility : nvidia-smi コマンドおよび NVML, 
    # compute : CUDA / OpenCL アプリケーション
    ENV NVIDIA_DRIVER_CAPABILITIES utility,compute
    ```

- Dockerfile の一例
    ```Dockerfile
    # 一例
    ```
