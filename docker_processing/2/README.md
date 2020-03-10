# 【Docker】 docker コンテナ内で機械学習モデルの処理を実行中に tensorboard で実行結果を確認する。

- Docker のみを使用して環境構築されている環境において、docker コンテナ内で機械学習モデルの処理を実行中に tensorboard で実行結果を確認するには、機械学習モデルの処理を行っているコンテナとは別に、Tensorflow イメージでの別コンテナを立ち上げ、そのコンテナ内から tensorborad を実行すれば良い。
この際に、tensorboard が使用するのポート番号（6006など）を、`-p` オプションで設定する必要があることに注意

    ```sh
    # 機械学習モデルの実行コンテナ
    docker run -it --rm -v ${PWD}/GAN_WGAN-GP_PyTorch:/workspace/GAN_WGAN-GP_PyTorch --name ml_pytorch_container ml_exercises_pytorch_image /bin/bash

    # 機械学習モデルの学習処理実行中
    root@4bad523338de:/workspace# cd GAN_WGAN-GP_PyTorch/
    root@4bad523338de:/workspace/GAN_WGAN-GP_PyTorch# sh train.sh
    minbatch iters:   6%|████▊                                                                                  | 13/235 [17:21<4:47:33, 77.72s/it]
    ...
    ```

    ```sh
    # Tensorflow イメージのダウンロード
    $ docker pull tensorflow/tensorflow

    # 別コンテナの立ち上げ
    $ docker run -it --rm -v ${PWD}/GAN_WGAN-GP_PyTorch:/workspace/GAN_WGAN-GP_PyTorch -p 6006:6006 --name tensorflow_container tensorflow/tensorflow /bin/bash

    root@b5c355ab900e:/workspace# cd GAN_WGAN-GP_PyTorch/
    root@b5c355ab900e:/workspace/GAN_WGAN-GP_PyTorch# tensorboard --logdir tensorboard
    Serving TensorBoard on localhost; to expose to the network, use a proxy or pass --bind_all
    TensorBoard 2.0.0 at http://localhost:6006/ (Press CTRL+C to quit)
    ```

- 又は、機械学習モデルを実行しているコンテナのイメージの作成時に、TensorFlow をインストールしてイメージを作成した上で、コンテナ内で tensorboard 起動を nohup で実行すればよい（こっちのほうが一般的なやり方）。この際に、機械学習モデルと tensorboard を実行するコンテナの起動時に、tensorboard が使用するのポート番号（6006など）を、`-p` オプションで設定する必要があることに注意
