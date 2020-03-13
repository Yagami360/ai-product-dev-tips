# 【Docker】 ホスト環境とコンテナ環境で同期したファイルの所有権を指定する。
`docker run` の `-v` オプションなどを使用すれば、ホスト環境のディレクトリとコンテナ環境のディレクトリを同期（＝ボリュームのマウント）できるが、コンテナ内で mkdir などでファイルアクセスしようとしたり、逆にホスト環境側から同期したファイルにアクセスしようとすると、所有権やアクセス権の関係で、permission denied エラーが出て実行できないケースがある。

※ この問題が発生するのは、Ubuntu 環境で docker を実行した場合で、docker for mac などではこのような問題は起こらない。

<!--dockerfile 内で一般ユーザーを作成し、作業ディレクトリをそのユーザーディレクトリ以下（例えば、`/home/ubuntu/`）にした場合、
-->

この問題を解決するための方法としては、以下のような方法がある。

- sudo 権限で命令を実行する<br>
    - 最も簡単な応急処置的な方法は、ホスト環境、又はコンテナ環境で sudo コマンドで命令を実行する方法
        ```sh
        # 例：ディレクトリを作成
        $ sudo mkdir temp
        ```
    - 但しこの方法だと毎回 sudo 指定する必要があり、またプログラムの中でファイルを読み込んだり書き込んだりする場合にも、いちいち `sudo python` 等で実行しなくてはならず、あまり実用的でない。

- `/etc/passwd` と `/etc/group` をコンテナにマウントする<br>
    この問題が発生する理由は、ホスト環境側とコンテナ環境側で異なるユーザーとなってしまうことが原因である（詳細は、下の「うまくいかない方法」を参照）ので、Ubuntu 環境においてユーザー情報を記載したファイルをホスト環境側とコンテナ環境側で readOnly で同期することで、ホスト環境側とコンテナ環境側のユーザーを同じにする。
    - `docker run` の `-v` オプションに追加する場合
        ```sh
        $ docker run -it --name ${CONTAINER_NAME} -v ${HOST_DIR}:${CONTAINER_DIR} \
            -v /etc/group:/etc/group:ro -v /etc/passwd:/etc/passwd:ro -u $(id -u $USER):$(id -g $USER) \
            ${IMAGE_NAME} bash
        ```

    - docker-compose を用いる場合は、`volumes` タグに追加
        ```yml
        volumes:
            - /etc/group:/etc/group:ro
            - /etc/passwd:/etc/passwd:ro
        ```
    - `/etc/group` : Ubuntu 環境において、
    - `/etc/passwd` : Ubuntu 環境において、システムに登録されているユーザリスト（ユーザーのアカウント情報）を記載したファイル
    ```sh
    # ホスト環境側の UID, GID は uid=1000(ubuntu) gid=1000(ubuntu)
    $ id
    uid=1000(ubuntu) gid=1000(ubuntu) groups=1000(ubuntu),4(adm),20(dialout),24(cdrom),25(floppy),27(sudo),29(audio),30(dip),44(video),46(plugdev),109(netdev),110(lxd),999(docker)

    # コンテナ起動
    $ docker run -it --rm --name python_container -v ${PWD}:/workspace -v /etc/group:/etc/group:ro -v /etc/passwd:/etc/passwd:ro -u $(id -u $USER):$(id -g $USER) python_image /bin/bash

    # コンテナ内のユーザーが root ではなく、ホスト環境側と同じ ubuntu(1000) ユーザーになっている
    ubuntu@64e190d002b8:/workspace$ id
    uid=1000(ubuntu) gid=1000(ubuntu) groups=1000(ubuntu)

    # 同期したディレクトリ workspace 以外は、root ユーザー
    ubuntu@64e190d002b8:/workspace$ cd ..
    ubuntu@64e190d002b8:/$ ls -l
    drwxr-xr-x   1 root   root   4096 Mar  4 07:00 bin
    drwxr-xr-x   2 root   root   4096 Apr 12  2016 boot
    drwxr-xr-x   5 root   root    360 Mar 13 07:33 dev
    drwxr-xr-x   1 root   root   4096 Mar 13 07:33 etc
    drwxr-xr-x   2 root   root   4096 Apr 12  2016 home
    drwxr-xr-x   1 root   root   4096 Sep 13  2015 lib
    drwxr-xr-x   2 root   root   4096 Nov  8 21:44 lib64
    drwxr-xr-x   2 root   root   4096 Nov  8 21:44 media
    drwxr-xr-x   2 root   root   4096 Nov  8 21:44 mnt
    drwxr-xr-x   2 root   root   4096 Nov  8 21:44 opt
    dr-xr-xr-x 163 root   root      0 Mar 13 07:33 proc
    drwx------   1 root   root   4096 Mar 13 07:05 root
    drwxr-xr-x   1 root   root   4096 Nov  8 21:44 run
    drwxr-xr-x   1 root   root   4096 Nov 27 00:22 sbin
    drwxr-xr-x   2 root   root   4096 Nov  8 21:44 srv
    dr-xr-xr-x  13 root   root      0 Mar 13 07:07 sys
    drwxrwxrwt   1 root   root   4096 Mar 13 07:05 tmp
    drwxr-xr-x   1 root   root   4096 Nov  8 21:44 usr
    drwxr-xr-x   1 root   root   4096 Nov  8 21:44 var
    drwxrwxr-x   2 ubuntu ubuntu 4096 Mar 13 07:37 workspace

    # コンテナ内で作成したファイル test.txt のユーザーもホストとおなじなので、ホスト環境側からでもアクセスできる
    ubuntu@64e190d002b8:/workspace$ touch test.txt
    ubuntu@64e190d002b8:/workspace$ ls -l
    -rw-rw-r-- 1 ubuntu ubuntu 1466 Mar 13 07:03 Dockerfile
    -rw-rw-r-- 1 ubuntu ubuntu 9019 Mar 13 07:45 README.md
    -rw-r--r-- 1 ubuntu ubuntu    0 Mar 13 07:46 test.txt
    ```

## うまくいかない方法

- ユーザーの切り替えを行わず、作業ディレクトリを `/` 以下に配置する（例えば `/workspace`）
    - この場合、コンテナ内のユーザーは、root ユーザー（UID:0, GID=0）となる（＝ファイルやディレクトリの所有権が root）。そのため全てのファイルやディレクトリに sudo なしでアクセス可能となる。
    - 一方、同期したディレクトリやファイルの所有権は、ホスト環境側の一般ユーザーと同じものとなる。（例えば、ubuntu(1000) ユーザー）。
    - コンテナ環境では root ユーザー、ホスト環境では一般ユーザーとなるので、同期するディレクトリ内でコンテナ環境で作成したディレクトリやファイルをホスト環境側からアクセスできなくなり、ホスト環境側からファイルを操作しようとすると、permission denied エラーが出て実行できなくなってしまう。
        ```sh
        # ホスト環境側の UID, GID は uid=1000(ubuntu) gid=1000(ubuntu)
        $ id
        uid=1000(ubuntu) gid=1000(ubuntu) groups=1000(ubuntu),4(adm),20(dialout),24(cdrom),25(floppy),27(sudo),29(audio),30(dip),44(video),46(plugdev),109(netdev),110(lxd),999(docker)

        # コンテナ起動
        $ docker run -it --rm --name python_container -v ${PWD}:/workspace python_image /bin/bash

        # コンテナ内
        # UID と GID は root ユーザーになっている
        root@baf17b677032:/workspace# id
        uid=0(root) gid=0(root) groups=0(root)
        root@baf17b677032:/workspace# cd ..

        # 同期した作業ディレクトリ workspace のユーザーがホスト環境側の 1000(ubuntu)
        root@baf17b677032:/# ls -l
        drwxr-xr-x   1 root root 4096 Mar  4 07:00 bin
        drwxr-xr-x   2 root root 4096 Apr 12  2016 boot
        drwxr-xr-x   5 root root  360 Mar 13 07:07 dev
        drwxr-xr-x   1 root root 4096 Mar 13 07:07 etc
        drwxr-xr-x   2 root root 4096 Apr 12  2016 home
        drwxr-xr-x   1 root root 4096 Sep 13  2015 lib
        drwxr-xr-x   2 root root 4096 Nov  8 21:44 lib64
        drwxr-xr-x   2 root root 4096 Nov  8 21:44 media
        drwxr-xr-x   2 root root 4096 Nov  8 21:44 mnt
        drwxr-xr-x   2 root root 4096 Nov  8 21:44 opt
        dr-xr-xr-x 165 root root    0 Mar 13 07:07 proc
        drwx------   1 root root 4096 Mar 13 07:05 root
        drwxr-xr-x   1 root root 4096 Nov  8 21:44 run
        drwxr-xr-x   1 root root 4096 Nov 27 00:22 sbin
        drwxr-xr-x   2 root root 4096 Nov  8 21:44 srv
        dr-xr-xr-x  13 root root    0 Mar 13 07:07 sys
        drwxrwxrwt   1 root root 4096 Mar 13 07:05 tmp
        drwxr-xr-x   1 root root 4096 Nov  8 21:44 usr
        drwxr-xr-x   1 root root 4096 Nov  8 21:44 var
        drwxrwxr-x   2 1000 1000 4096 Mar 13 07:03 workspace

        root@baf17b677032:/# cd workspace/

        # コンテナ内は root ユーザーなので sudo なしでもファイルの作成が可能
        root@baf17b677032:/workspace# touch test.txt

        # 同期したファイルやディレクトリは、ホスト環境側のユーザー（ubuntu(1000)）
        # コンテナ内で作成したファイルやディレクトリの所有権は root ユーザーになっている
        # コンテナ内で作成したファイル test.txt は root ユーザーなので、ホスト環境側から操作できない
        root@baf17b677032:/workspace# ls -l
        total 8
        -rw-rw-r-- 1 1000 1000 1466 Mar 13 07:03 Dockerfile
        -rw-rw-r-- 1 1000 1000 6283 Mar 13 07:30 README.md
        -rw-r--r-- 1 root root    0 Mar 13 07:30 test.txt
        ```

- dockerfile 内でホスト環境側と同じユーザーを追加
    この方法はイメージをビルドしたマシンと実行するマシンが同じならば問題がない。
    しかし、イメージをビルドする段階でuidを決定しなければならないので、別のマシンでビルドしたイメージは使えず実用的ではない。


## 参考サイト

- [dockerでvolumeをマウントしたときのファイルのowner問題](https://qiita.com/yohm/items/047b2e68d008ebb0f001)

## Dockerfile

- ユーザーの切り替えを行わない
    ```Dockerfile
    ```

- sudo 権限をもつユーザーを追加
    ```Dockerfile
    ```

