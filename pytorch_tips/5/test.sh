#!/bin/sh
#conda activate pytorch11_py36
set -eu
mkdir -p _logs

GPU_IDS="0"
#GPU_IDS="1"
#GPU_IDS="0,1,2,3"

#----------------------
# model
#----------------------
IMAGE_HIGHT=128
IMAGE_WIDTH=128

EXPER_NAME=debug
LOAD_CHECKPOINTS_PATH=checkpoints/${EXPER_NAME}/model_G_final.pth
rm -rf results/${EXPER_NAME}
rm -rf tensorboard/${EXPER_NAME}_test
if [ ${EXPER_NAME} = "debug" ] ; then
    N_SAMPLING=5
else
    N_SAMPLING=100000
fi

python test.py \
    --exper_name ${EXPER_NAME} \
    --load_checkpoints_path ${LOAD_CHECKPOINTS_PATH} \
    --n_samplings ${N_SAMPLING} \
    --image_height ${IMAGE_HIGHT} --image_width ${IMAGE_WIDTH} --batch_size_test 1 \
    --gpu_ids ${GPU_IDS} \
    --debug

if [ $1 = "poweroff" ] ; then
    sudo poweroff
    sudo shutdown -h now
fi
