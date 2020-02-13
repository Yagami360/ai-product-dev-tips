# 【Docker】 コンテナの起動とコンテナ内での python スクリプト実行を一括して行う。
`docker run` コマンドや `docker start` コマンドなどでコンテナを起動した後に、そのコンテナ内での python スクリプト実行したい場合が多々あるが、それぞれのコマンドを都度入力するのは手間である。

このようなケースでは、コンテナの起動とコンテナ内での python スクリプト実行を一括して行えれば便利であるが、これを行うには、`docker exec` コマンドの `-c` オプション指定後の "xxx" 内に python コマンドを入力すればよい。

```sh
# コンテナを起動
docker start ${CONTAINER_NAME}

# 実行中の docker 内に入る
docker exec -it ${CONTAINER_NAME} /bin/bash -c \
    "python train.py \
        --device gpu \
        --exper_name ${EXEP_NAME} \
        --dataset_dir ../dataset \
        --results_dir ${RESULTS_DIR} \
        --tensorboard_dir ${TENSOR_BOARD_DIR} \
        --save_checkpoints_dir checkpoints --n_save_step ${N_SAVE_STEP} \
        --dataset mnist --image_size 64 \
        --n_epoches ${N_EPOCHES} --batch_size ${BATCH_SIZE} --batch_size_test ${BATCH_SIZE_TEST} \
        --lr 0.0001 --beta1 0.5 --beta2 0.999 \
        --n_display_step ${N_DISPLAY_STEP} --n_display_test_step ${N_DISPLAY_TEST_STEP} \
        --debug"
```

コンテナを起動後に、複数コマンドを実行したい場合は `docker exec` の `-c` オプション指定後の "xxx" 内で && でコマンドを接続すればよい。

```sh
# コンテナを起動
docker start ${CONTAINER_NAME}

# 実行中の docker 内に入る
docker exec -it ${CONTAINER_NAME} /bin/bash -c "cd GAN_DCGAN_PyTorch && ls && \
    python train.py \
        --device gpu \
        --exper_name ${EXEP_NAME} \
        --dataset_dir ../dataset \
        --results_dir ${RESULTS_DIR} \
        --tensorboard_dir ${TENSOR_BOARD_DIR} \
        --save_checkpoints_dir checkpoints --n_save_step ${N_SAVE_STEP} \
        --dataset mnist --image_size 64 \
        --n_epoches ${N_EPOCHES} --batch_size ${BATCH_SIZE} --batch_size_test ${BATCH_SIZE_TEST} \
        --lr 0.0001 --beta1 0.5 --beta2 0.999 \
        --n_display_step ${N_DISPLAY_STEP} --n_display_test_step ${N_DISPLAY_TEST_STEP} \
        --debug"
```

