#source activate pytorch11_py36
cd ./exp/transfer

python train_cihp_from_pascal.py \
    --image_size 64 --hidden_layers 32 --batch 4 --gpus 1 \
    --lr 0.007 --classes 20

<<COMMENTOUT
python ./exp/transfer/train_cihp_from_pascal.py \
    --batch 24 --gpus 8 --pretrainedModel './data/pretrained_model/pascal_base_trained.pth' \
    --lr 0.007 --classes 20
COMMENTOUT
