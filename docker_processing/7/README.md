# 【Docker】本番環境用の Docker イメージと開発環境用の Docker イメージの構成

- 開発環境用の dockerfile<br>
    開発環境用では、`docker run` の `-v` オプションなどでホスト環境と Docker 環境を同期することで、ホスト環境側で修正してソースコードが、即座にコンテナ環境でも反映されるようにする運用が望ましい。

- 本番環境（プロダクト環境）用の dockerfile<br>
    本番環境用では、`-v` オプションなどでのホスト環境と Docker 環境の同期は行わず、ソースコードや読み込みデータ等のプログラムの実行に必要なファイルを全て Docker イメージ内にコピーし、Docker イメージ単体で１つの実行可能ファイルにする運用が望ましい。<br>
    この場合、ホスト環境と Docker 環境を同期は行っていないので、ホスト環境でソースコードが修正されても、Docker イメージを再度作成しない限り、ソースコードの修正は反映されないことになる。

    尚、Docker イメージへのコピーは、`COPY` 又は `ADD` 命令で行える。
    この際に、docker ファイルの最初の方でコピーを行ってしまうと、キャッシュを利用できず毎回最初のほうの行からイメージを作成しなおしてしまうので、できるだけ最後の方で COPY or ADD するのが望ましい。

    ```dockerfile
    # ベースイメージの設定
    FROM nvidia/cuda:10.1-base-ubuntu16.04

    # ライブラリのインストール
    ENV DEBIAN_FRONTEND noninteractive
    RUN set -x && apt-get update && apt-get install -y --no-install-recommends \
        sudo \
        git \
        curl \
        wget \
        bzip2 \
        ca-certificates \
        libx11-6 \
        python3-pip \
        # imageのサイズを小さくするためにキャッシュ削除
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

    ...

    # コンテナ起動後の作業ディレクトリ
    WORKDIR /home/ubuntu/share

    # プログラムの実行に必要なソースコードの COPY
    # できるだけ最後の方で実行することで、イメージを作り直した場合でもキャッシュを利用できるようにする。
    COPY *.py /home/ubuntu/share/
    COPY *.sh /home/ubuntu/share/
    ```
