# Docker の基本事項・基本コマンド

## ■ Docker イメージ関連

### ◎ Docker イメージのダウンロード
`$ docker pull ${IMAGE_NAME}`

```sh
# example
$ docker pull pytorch/pytorch
```

### ◎ Docker イメージの検索
`$ docker search ${SARCH_WORDS}`

```sh
# example
$ docker search pytorch

NAME                            DESCRIPTION                                     STARS               OFFICIAL            AUTOMATED
pytorch/pytorch                 PyTorch is a deep learning framework that pu…   149                                     
floydhub/pytorch                pytorch                                         41                                      [OK]
anibali/pytorch                 Docker images for the PyTorch deep learning …   11                                      [OK]
...
```

### ◎ 作成したDocker イメージの確認
`$ docker images`

```sh
# example
$ docker docker images

REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
pytorch/pytorch     latest              ba2da111b833        6 weeks ago         4.32GB
```


## ■ コンテナ関連

### ◎ コンテナを起動

`$ docker run ${IMAGE_NAME}`
- `-i` オプション : ホストマシンとコンテナの双方向に接続できるようにする
- `-t` オプション : コンテナ内に擬似的なターミナルを割り当て
- `--rm` オプション : コンテナから抜けるとコンテナを自動で削除する
- `--name` オプション : コンテナの名前を指定する
- `-v ${ホストマシンの同期するディレクトリ}:${Dockerコンテナ内の同期するディレクトリ}` オプション : ホストマシンとコンテナの同期して、ホストマシンで編集した内容が、即時コンテナにも反映されるようにする。

`-v` オプションを指定しない `docker run` では、コンテナを終了する度に、コンテナ環境で作成したファイルが消えてしまう。

```sh
# example1
$ docker run -it --rm --name pytorch_container pytorch/pytorch /bin/bash

root@1f46a99c39b0:/workspace#
root@1f46a99c39b0:/workspace#exit
```
- `/bin/bash` : 
- `exit` コマンドでコンテナから抜ける

一般的には、`-v` オプションを指定した `docker run -v ${ホストマシンの同期するディレクトリ}:${Dockerコンテナ内の同期するディレクトリ}` で、 ホストマシンとコンテナのディレクトリを同期することで、 コンテナを終了しても（同期した）ディレクトリの内容が保存されるようにする。

```sh
# example2
$ docker run -it --rm -v ${PWD}/host_dir:/container_dir --name pytorch_container pytorch/pytorch /bin/bash

```

### ◎ 起動中のコンテナ確認

`$ docker ps`

```sh
# example
$ docker ps

CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS               NAMES
62415f8a2996        pytorch/pytorch     "/bin/bash"         9 seconds ago       Up 8 seconds                            pytorch_container
```

## ■ Docker-Compose

### ◎ サーバーの開始

`$ docker-compose up -d`

### コンテナの駆動状況の確認

`$ docker-compose ps`

### コンテナでのプログラム実行

`$ docker-compose run ${PROGRAM}`
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