# 【Docker】 ホスト環境とコンテナ環境で同期したファイルの所有権を指定する。
`docker run` の `-v` オプションなどを使用すれば、ホスト環境のディレクトリとコンテナ環境のディレクトリを同期（＝ボリュームのマウント）できるが、dockerfile 内で一般ユーザーを作成し、作業ディレクトリをそのユーザーディレクトリ以下（例えば、`/home/ubuntu/`）にした場合、コンテナ内で mkdir などでファイルアクセスしようとすると、所有権やアクセス権の関係で、permission denied エラーが出て実行できないケースがある。

この問題を解決するための方法としては、以下のような方法がある。

- sudo 権限で命令を実行する<br>
    - 最も簡単な応急処置的な方法は、sudo コマンドで命令を実行する方法
        ```sh
        # コンテナ内
        $ sudo mkdir temp
        ```
    - 但しこの方法だと毎回 sudo 指定する必要があり、またプログラムの中でファイルを読み込んだり書き込んだりする場合にも、いちいち `sudo python` 等で実行しなくてはならず、あまり実用的でない

- ユーザーの切り替えを行わず、作業ディレクトリを `/` 以下に配置する（例えば `/workspace`）
    - この場合、コンテナ内のユーザーは、root ユーザー（UID:0, GID=0）となる（＝ファイルやディレクトリの所有権が root）。そのため全てのファイルやディレクトリに sudo なしでアクセス可能となる。（同様にホスト環境側からもアクセス可能）
        ```sh
        $ docker run -it --rm --name python_container -v ${PWD}:/workspace python_image /bin/bash
        # コンテナ内
        # UID と GID は root ユーザーになっている
        root@baf17b677032:/workspace# id
        uid=0(root) gid=0(root) groups=0(root)
        root@baf17b677032:/workspace# cd ..
        root@baf17b677032:/# ls -l
        drwxr-xr-x   1 root root 4096 Mar  4 05:56 bin
        drwxr-xr-x   2 root root 4096 Apr 12  2016 boot
        drwxr-xr-x   5 root root  360 Mar 11 14:58 dev
        drwxr-xr-x   1 root root 4096 Mar 11 14:58 etc
        drwxr-xr-x   2 root root 4096 Apr 12  2016 home
        drwxr-xr-x   1 root root 4096 Sep 13  2015 lib
        drwxr-xr-x   2 root root 4096 Nov  8 21:44 lib64
        drwxr-xr-x   2 root root 4096 Nov  8 21:44 media
        drwxr-xr-x   2 root root 4096 Nov  8 21:44 mnt
        drwxr-xr-x   2 root root 4096 Nov  8 21:44 opt
        dr-xr-xr-x 200 root root    0 Mar 11 14:58 proc
        drwx------   1 root root 4096 Mar 11 14:49 root
        drwxr-xr-x   1 root root 4096 Nov  8 21:44 run
        drwxr-xr-x   1 root root 4096 Nov 27 00:22 sbin
        drwxr-xr-x   2 root root 4096 Nov  8 21:44 srv
        dr-xr-xr-x  13 root root    0 Mar 11 14:58 sys
        drwxrwxrwt   1 root root 4096 Mar 11 14:49 tmp
        drwxr-xr-x   1 root root 4096 Nov  8 21:44 usr
        drwxr-xr-x   1 root root 4096 Nov  8 21:44 var
        drwxr-xr-x   5 root root  160 Mar 11 15:00 workspace

        root@baf17b677032:/# cd workspace/
        # root ユーザーなので sudo なしでも mkdir 可能
        root@baf17b677032:/workspace# mkdir tmp

        # 同期したファイルやディレクトリ、コンテナ内で作成したファイルやディレクトリの所有権は root ユーザーになっている
        root@baf17b677032:/workspace# ls -l
        total 8
        -rw-r--r-- 1 root root 1317 Mar 11 14:55 Dockerfile
        -rw-r--r-- 1 root root 3552 Mar 11 15:03 README.md
        drwxr-xr-x 2 root root   64 Mar 11 15:00 tmp
        ```
    - 但し、一般的な Ubuntu システムのように、dockerfile で `/home` 以下にユーザーを作って（例えば、`/home/ubuntu/`）、そのユーザーで conda をインストールしている場合などは、作業ディレクトリを

- dockerfile 内で sudo ユーザーを追加し、そのユーザーに切り替える


- `/etc/passwd` と `/etc/group` をコンテナにマウントする<br>
    `docker run` の `-v` オプションに追加する場合
    ```sh
    $ docker run -it -v /etc/group:/etc/group:ro -v /etc/passwd:/etc/passwd:ro -u $(id -u $USER):$(id -g $USER) ${CONTAINER_NAME} bash
    ```

    docker-compose を用いる場合は、`volumes` タグに追加
    ```yml
    volumes:
        - /etc/group:/etc/group:ro
        - /etc/passwd:/etc/passwd:ro
    ```

    - `/etc/group` : Ubuntu 環境において、
    - `/etc/passwd` : Ubuntu 環境において、システムに登録されているユーザリスト（ユーザーのアカウント情報）を記載したファイル

## メモ

- dockerfile でユーザーを追加せず /workspace 以下を作業ディレクトリとした場合
    - コンテナ内では root ユーザー（UID:0, GID=0）でファイルやフォルダのアクセス可能なので、permission denied エラー発生しない。
    ```sh
    $ docker run -it --rm --name python_container -v ${PWD}:/workspace python_image /bin/bash
    root@baf17b677032:/workspace# id
    uid=0(root) gid=0(root) groups=0(root)
    root@baf17b677032:/workspace# cd ..
    root@baf17b677032:/# ls -l
    drwxr-xr-x   1 root root 4096 Mar  4 05:56 bin
    drwxr-xr-x   2 root root 4096 Apr 12  2016 boot
    drwxr-xr-x   5 root root  360 Mar 11 14:58 dev
    drwxr-xr-x   1 root root 4096 Mar 11 14:58 etc
    drwxr-xr-x   2 root root 4096 Apr 12  2016 home
    drwxr-xr-x   1 root root 4096 Sep 13  2015 lib
    drwxr-xr-x   2 root root 4096 Nov  8 21:44 lib64
    drwxr-xr-x   2 root root 4096 Nov  8 21:44 media
    drwxr-xr-x   2 root root 4096 Nov  8 21:44 mnt
    drwxr-xr-x   2 root root 4096 Nov  8 21:44 opt
    dr-xr-xr-x 200 root root    0 Mar 11 14:58 proc
    drwx------   1 root root 4096 Mar 11 14:49 root
    drwxr-xr-x   1 root root 4096 Nov  8 21:44 run
    drwxr-xr-x   1 root root 4096 Nov 27 00:22 sbin
    drwxr-xr-x   2 root root 4096 Nov  8 21:44 srv
    dr-xr-xr-x  13 root root    0 Mar 11 14:58 sys
    drwxrwxrwt   1 root root 4096 Mar 11 14:49 tmp
    drwxr-xr-x   1 root root 4096 Nov  8 21:44 usr
    drwxr-xr-x   1 root root 4096 Nov  8 21:44 var
    drwxr-xr-x   5 root root  160 Mar 11 15:00 workspace

    root@baf17b677032:/# cd workspace/
    root@baf17b677032:/workspace# mkdir tmp
    root@baf17b677032:/workspace# ls -l
    total 8
    -rw-r--r-- 1 root root 1317 Mar 11 14:55 Dockerfile
    -rw-r--r-- 1 root root 3552 Mar 11 15:03 README.md
    drwxr-xr-x 2 root root   64 Mar 11 15:00 tmp
    ```

## 参考サイト

- [dockerでvolumeをマウントしたときのファイルのowner問題](https://qiita.com/yohm/items/047b2e68d008ebb0f001)

## Dockerfile

- ユーザーの切り替えを行わない
    ```Dockerfile
    ```

- sudo 権限をもつユーザーを追加
    ```Dockerfile
    ```

