#!/bin/bash
#conda activate pytorch11_py36
set -eu
mkdir -p _logs

#GPU_IDS="0"
#GPU_IDS="1"
GPU_IDS="0,1,2,3"

GPU_IDS_=(${GPU_IDS//,/})
N_GPUS="${#GPU_IDS_}"

#----------------------
# model
#----------------------
N_EPOCHES=100
BATCH_SIZE=4
IMAGE_HIGHT=128
IMAGE_WIDTH=128

EXPER_NAME=debug_ddp
rm -rf tensorboard/${EXPER_NAME}
rm -rf tensorboard/${EXPER_NAME}_valid
if [ ${EXPER_NAME} = "debug_ddp" ] ; then
    N_DISPLAY_STEP=10
    N_DISPLAY_VALID_STEP=50
else
    N_DISPLAY_STEP=100
    N_DISPLAY_VALID_STEP=500
fi

python train_ddp.py \
    --exper_name ${EXPER_NAME} \
    --n_epoches ${N_EPOCHES} \
    --image_height ${IMAGE_HIGHT} --image_width ${IMAGE_WIDTH} --batch_size ${BATCH_SIZE} \
    --n_diaplay_step ${N_DISPLAY_STEP} --n_display_valid_step ${N_DISPLAY_VALID_STEP} \
    --data_augument_types "resize,crop,hflip,vflip,perspect,affine,color,erase,tps" \
    --gpu_ids ${GPU_IDS} \
    --use_ddp \
    --debug

if [ $1 = "poweroff" ] ; then
    sudo poweroff
    sudo shutdown -h now
fi
