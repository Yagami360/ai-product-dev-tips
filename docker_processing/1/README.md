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
    - 作成したイメージの構成を定義した Dockerfile が存在するディレクトリで、上のコマンドを実行
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
    $ docker docker images

    REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
    pytorch/pytorch     latest              ba2da111b833        6 weeks ago         4.32GB
    ```


## ■ コンテナ関連

### ◎ コンテナを起動

- `$ docker run ${CONTAINER_NAME} ${IMAGE_NAME} /bin/bash`
    - `${CONTAINER_NAME}` : コンテナ名
    - `${IMAGE_NAME}` : docker イメージ名
    - `-i` オプション : ホストマシンとコンテナの双方向に接続できるようにする
    - `-t` オプション : コンテナ内に擬似的なターミナルを割り当て
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
    $ HOST_DIR=GAN_WGAN-GP_PyTorch
    $ CONTAINER_DIR=GAN_WGAN-GP_PyTorch
    $ docker run -it --rm -v ${PWD}/${HOST_DIR}:/workspace/${CONTAINER_DIR} --name pytorch_container pytorch/pytorch /bin/bash

    # 接続されるコンテナのディレクトリは、デフォルトで workspace ディレクトリ
    root@31121a30cb2b:/workspace# ls
    GAN_WGAN-GP_PyTorch
    root@31121a30cb2b:/workspace# cd GAN_WGAN-GP_PyTorch/
    root@31121a30cb2b:/workspace/GAN_WGAN-GP_PyTorch# exit
    ```

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



## ■ Docker-Compose
複数コンテナを一元管理するコンポーネント。それと同時に docker イメージの作成からコンテナの起動までを一括して行える機能もある。

### ◎ サーバーの開始

- `$ docker-compose up -d`

### コンテナの駆動状況の確認

- `$ docker-compose ps`

### コンテナでのプログラム実行

- `$ docker-compose run ${PROGRAM}`
    - `--rm` オプション：コンテナ終了時にコンテナを自動的に削除
    - `-v` オプション : ホストの任意のパスをコンテナの任意のパスにマウントさせる（＝認識させる）


## ■ nvidia-docker
nvidia-dockerは大まかにいうと、実行したいコンテナ内からGPUにアクセスできるようにDocker Engine APIに色々なパラメータを指定してあげてコンテナを起動している。GPU関連の情報を取得できるようにnvidia-docker-pluginっていうGPU関連の情報をHTTPのサーバが立っている。

### nvidia-docker 1.0

`nvidia-docker` という docker ラッパーコマンドを使用する。

### nvidia-docker 2.0

`docker run --runtime=nvidia` という xxx

### nvidia-docker 3.0
xxx