import os
import argparse
import numpy as np
import pandas as pd
import random
from tqdm import tqdm
from PIL import Image
import cv2

# sklearn
from sklearn.model_selection import train_test_split

# PyTorch
import torch
from torch.utils.data import DataLoader, Dataset, Subset
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional as F
import torchvision
from torchvision.utils import save_image
from tensorboardX import SummaryWriter

try:
    from apex import amp
except ImportError:
    amp = None

# 自作モジュール
from data.dataset import TempleteDataset, TempleteDataLoader
from models.generators import Pix2PixHDGenerator
from utils.utils import save_checkpoint, load_checkpoint
from utils.utils import board_add_image, board_add_images, save_image_w_norm

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--exper_name", default="debug", help="実験名")
    parser.add_argument("--dataset_dir", type=str, default="dataset/templete_dataset")
    parser.add_argument("--results_dir", type=str, default="results")
    parser.add_argument('--load_checkpoints_path', type=str, default="", help="モデルの読み込みファイルのパス")
    parser.add_argument('--tensorboard_dir', type=str, default="tensorboard", help="TensorBoard のディレクトリ")
    parser.add_argument('--n_samplings', type=int, default=100000, help="サンプリング最大数")
    parser.add_argument('--batch_size_test', type=int, default=1, help="バッチサイズ")
    parser.add_argument('--image_height', type=int, default=128, help="入力画像の高さ（pixel単位）")
    parser.add_argument('--image_width', type=int, default=128, help="入力画像の幅（pixel単位）")
    parser.add_argument("--seed", type=int, default=71)
    parser.add_argument("--gpu_ids", default="0", help="使用GPU番号")
    parser.add_argument('--n_workers', type=int, default=4, help="CPUの並列化数（0 で並列化なし）")
    parser.add_argument('--use_cuda_benchmark', action='store_true', help="torch.backends.cudnn.benchmark の使用有効化")
    parser.add_argument('--use_cuda_deterministic', action='store_true', help="再現性確保のために cuDNN に決定論的振る舞い有効化")
    parser.add_argument('--detect_nan', action='store_true')
    parser.add_argument('--use_amp', action='store_true', help="AMP [Automatic Mixed Precision] の使用有効化")
    parser.add_argument('--opt_level', choices=['O0','O1','O2','O3'], default='O1', help='mixed precision calculation mode')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    #os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu_ids
    str_gpu_ids = args.gpu_ids.split(',')
    args.gpu_ids = []
    for str_gpu_id in str_gpu_ids:
        gpu_id = int(str_gpu_id)
        if gpu_id >= 0:
            args.gpu_ids.append(gpu_id)  

    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

    # 出力フォルダの作成
    if not os.path.isdir(args.results_dir):
        os.mkdir(args.results_dir)
    if not os.path.isdir( os.path.join(args.results_dir, args.exper_name) ):
        os.mkdir(os.path.join(args.results_dir, args.exper_name))
    if not os.path.isdir( os.path.join(args.results_dir, args.exper_name, "output" ) ):
        os.mkdir(os.path.join(args.results_dir, args.exper_name, "output"))

    # 実行 Device の設定
    if( torch.cuda.is_available() ):
        device = torch.device(f'cuda:{args.gpu_ids[0]}')
        print( "実行デバイス :", device)
        print( "GPU名 :", torch.cuda.get_device_name(device))
        print("torch.cuda.current_device() =", torch.cuda.current_device())
    else:
        device = torch.device("cpu")
        print( "実行デバイス :", device)

    # seed 値の固定
    if( args.use_cuda_deterministic ):
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    np.random.seed(args.seed)
    random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)

    # NAN 値の検出
    if( args.detect_nan ):
        torch.autograd.set_detect_anomaly(True)

    # tensorboard 出力
    board_test = SummaryWriter( log_dir = os.path.join(args.tensorboard_dir, args.exper_name) )

    #================================
    # データセットの読み込み
    #================================    
    # 学習用データセットとテスト用データセットの設定
    ds_test = TempleteDataset( args, args.dataset_dir, datamode = "test", image_height = args.image_height, image_width = args.image_width, data_augument_types = "resize,crop", debug = args.debug )
    dloader_test = torch.utils.data.DataLoader(ds_test, batch_size=args.batch_size_test, shuffle = False, num_workers = args.n_workers, pin_memory = True )

    #================================
    # モデルの構造を定義する。
    #================================
    model_G = Pix2PixHDGenerator().to(device)
    if( args.debug ):
        print( "model_G\n", model_G )

    # モデルを読み込む
    if not args.load_checkpoints_path == '' and os.path.exists(args.load_checkpoints_path):
        load_checkpoint(model_G, device, args.load_checkpoints_path )
        
    #================================
    # optimizer_G の設定（ダミー）
    #================================
    if( args.use_amp ):
        optimizer_G = optim.Adam( params = model_G.parameters(), lr = 0.0001, betas = (0.999,0.5) )

    #================================
    # apex initialize
    #================================
    if( args.use_amp ):
        model_G, optimizer_G = amp.initialize(
            model_G, 
            optimizer_G, 
            opt_level = args.opt_level,
            num_losses = 1
        )

    #================================
    # マルチ GPU
    #================================
    if len(args.gpu_ids) >= 2:
        model_G = torch.nn.DataParallel(model_G)

    #================================
    # モデルの推論
    #================================    
    print("Starting Testing Loop...")
    n_print = 1
    model_G.eval()
    for step, inputs in enumerate( tqdm( dloader_test, desc = "Samplings" ) ):
        if inputs["image_s"].shape[0] != args.batch_size_test:
            break

        # ミニバッチデータを GPU へ転送
        image_s_name = inputs["image_s_name"]
        image_s = inputs["image_s"].to(device)
        if( args.debug and n_print > 0):
            print( "image_s.shape : ", image_s.shape )

        #----------------------------------------------------
        # 生成器の推論処理
        #----------------------------------------------------
        with torch.no_grad():
            output = model_G( image_s )
            if( args.debug and n_print > 0 ):
                print( "output.shape : ", output.shape )

        #====================================================
        # 推論結果の保存
        #====================================================
        save_image_w_norm( output, os.path.join( args.results_dir, args.exper_name, "output", image_s_name[0] ) )

        # tensorboard
        visuals = [
            [ image_s, output ],
        ]
        board_add_images(board_test, 'test', visuals, step+1)

        n_print -= 1
        if( step >= args.n_samplings ):
            break
