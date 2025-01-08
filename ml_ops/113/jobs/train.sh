#!/bin/sh
#SBATCH --job-name=train-job-resnet18
#SBATCH --nodes=1
#SBATCH --ntasks=1
set -eu

N_EPOCHES=1
BATCH_SIZE=8
BATCH_SIZE_TEST=8
N_DISPLAY_STEP=10
N_DISPLAY_TEST_STEP=100
N_SAVE_STEP=1000

# mkdir -p .logs
EXEP_NAME=train-jobs-resnet18-epoch${N_EPOCHES}-$(date +%Y%m%d%H%M%S)
TENSOR_BOARD_DIR=.tensorboard
# if [ -d "${TENSOR_BOARD_DIR}/${EXEP_NAME}" ] ; then
#     rm -r ${TENSOR_BOARD_DIR}/${EXEP_NAME}
# fi
# if [ -d "${TENSOR_BOARD_DIR}/${EXEP_NAME}_test" ] ; then
#     rm -r ${TENSOR_BOARD_DIR}/${EXEP_NAME}_test
# fi

RESULTS_DIR=results
# if [ -d "${RESULTS_DIR}/${EXEP_NAME}" ] ; then
#     rm -r ${RESULTS_DIR}/${EXEP_NAME}
# fi

# -------------------
# Run train job
# -------------------
python3 train.py \
    --device cpu \
    --exper_name ${EXEP_NAME} \
    --dataset_dir ../dataset \
    --results_dir ${RESULTS_DIR} \
    --tensorboard_dir ${TENSOR_BOARD_DIR} \
    --save_checkpoints_dir checkpoints --n_save_step ${N_SAVE_STEP} \
    --dataset mnist --image_size 224 \
    --n_train 200 \
    --n_test 100 \
    --n_epoches ${N_EPOCHES} --batch_size ${BATCH_SIZE} --batch_size_test ${BATCH_SIZE_TEST} \
    --n_display_step ${N_DISPLAY_STEP} --n_display_test_step ${N_DISPLAY_TEST_STEP} \
    --debug

exit 0