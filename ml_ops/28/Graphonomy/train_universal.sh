#source activate pytorch11_py36
#cd ./exp/universal

python ./exp/universal/pascal_atr_cihp_uni.py \
    --image_size 64 --hidden_layers 32 --batch 4 --gpus 1 \
    --pretrainedModel './data/pretrained_model/deeplab_v3plus_v3.pth' \
    --lr 0.007
