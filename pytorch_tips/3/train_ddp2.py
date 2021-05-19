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

import torch.distributed as dist

try:
    import apex
    from apex import amp
except ImportError:
    apex = None
    amp = None

# 自作モジュール
from data.dataset import TempleteDataset, TempleteDataLoader
from models.networks import TempleteNetworks, Pix2PixHDGenerator
from utils.utils import save_checkpoint, load_checkpoint
from utils.utils import board_add_image, board_add_images, save_image_w_norm


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--exper_name", default="debug", help="実験名")
    parser.add_argument("--dataset_dir", type=str, default="dataset/templete_dataset")
    parser.add_argument("--results_dir", type=str, default="results")
    parser.add_argument('--save_checkpoints_dir', type=str, default="checkpoints", help="モデルの保存ディレクトリ")
    parser.add_argument('--load_checkpoints_path', type=str, default="", help="モデルの読み込みファイルのパス")
    parser.add_argument('--tensorboard_dir', type=str, default="tensorboard", help="TensorBoard のディレクトリ")
    parser.add_argument("--n_epoches", type=int, default=100, help="エポック数")    
    parser.add_argument('--batch_size', type=int, default=4, help="バッチサイズ")
    parser.add_argument('--batch_size_valid', type=int, default=1, help="バッチサイズ")
    parser.add_argument('--image_height', type=int, default=128, help="入力画像の高さ（pixel単位）")
    parser.add_argument('--image_width', type=int, default=128, help="入力画像の幅（pixel単位）")
    parser.add_argument('--lr', type=float, default=0.0002, help="学習率")
    parser.add_argument('--beta1', type=float, default=0.5, help="学習率の減衰率")
    parser.add_argument('--beta2', type=float, default=0.999, help="学習率の減衰率")
    parser.add_argument("--n_diaplay_step", type=int, default=100,)
    parser.add_argument('--n_display_valid_step', type=int, default=500, help="valid データの tensorboard への表示間隔")
    parser.add_argument("--n_save_epoches", type=int, default=10,)
    parser.add_argument("--val_rate", type=float, default=0.01)
    parser.add_argument('--n_display_valid', type=int, default=8, help="valid データの tensorboard への表示数")
    parser.add_argument('--data_augument_types', type=str, default="resize,crop")
    parser.add_argument("--seed", type=int, default=71)
    parser.add_argument("--gpu_ids", default="0", help="使用GPU番号")
    parser.add_argument('--n_workers', type=int, default=4, help="CPUの並列化数（0 で並列化なし）")
    parser.add_argument('--use_cuda_benchmark', action='store_true', help="torch.backends.cudnn.benchmark の使用有効化")
    parser.add_argument('--use_cuda_deterministic', action='store_true', help="再現性確保のために cuDNN に決定論的振る舞い有効化")
    parser.add_argument('--detect_nan', action='store_true')
    parser.add_argument('--use_ddp', action='store_true', help="DDP [DistributedDataParallel] の使用有効化")
    parser.add_argument("--local_rank", type=int, help="DDP [DistributedDataParallel] の使用時のマルチプロセス番号。python -m torch.distributed.launch で自動的に設定される")
    parser.add_argument('--use_amp', action='store_true', help="AMP [Automatic Mixed Precision] の使用有効化")
    parser.add_argument('--opt_level', choices=['O0','O1','O2','O3'], default='O1', help='mixed precision calculation mode')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    # args 引数の分解
    args.data_augument_types = args.data_augument_types.split(',')

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

    # rank0（0番目のプロセス）マシンのアドレスとポート番号
    if(args.use_ddp):
        os.environ['MASTER_ADDR'] = 'localhost'
        os.environ['MASTER_PORT'] = '1234'

    # すべてのプロセスが同じIPアドレスとポートを使用することで、マスターを介して調整できるようにする
    if(args.use_ddp):
        if( torch.cuda.is_available() ):
            dist.init_process_group("nccl", rank=args.local_rank, world_size=len(args.gpu_ids))
        else:
            dist.init_process_group("gloo", rank=args.local_rank, world_size=len(args.gpu_ids))

    # 出力フォルダの作成
    if not os.path.isdir(args.results_dir):
        os.mkdir(args.results_dir)
    if not os.path.isdir( os.path.join(args.results_dir, args.exper_name) ):
        os.mkdir(os.path.join(args.results_dir, args.exper_name))
    if not( os.path.exists(args.save_checkpoints_dir) ):
        os.mkdir(args.save_checkpoints_dir)
    if not( os.path.exists(os.path.join(args.save_checkpoints_dir, args.exper_name)) ):
        os.mkdir( os.path.join(args.save_checkpoints_dir, args.exper_name) )

    # 実行 Device の設定
    if( torch.cuda.is_available() ):
        if( args.use_ddp ):
            torch.cuda.set_device(args.local_rank)
            device = torch.device(f'cuda:{args.local_rank}')
        else:
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
    if( args.local_rank == 0 ):
        board_train = SummaryWriter( log_dir = os.path.join(args.tensorboard_dir, args.exper_name) )
        board_valid = SummaryWriter( log_dir = os.path.join(args.tensorboard_dir, args.exper_name + "_valid") )

    #================================
    # データセットの読み込み
    #================================    
    # 学習用データセットとテスト用データセットの設定
    ds_train = TempleteDataset( args, args.dataset_dir, datamode = "train", image_height = args.image_height, image_width = args.image_width, batch_size = args.batch_size, data_augument_types = args.data_augument_types, use_ddp = args.use_ddp, n_gpus = len(args.gpu_ids), debug = args.debug )
    ds_valid = TempleteDataset( args, args.dataset_dir, datamode = "valid", image_height = args.image_height, image_width = args.image_width, batch_size = args.batch_size_valid, data_augument_types = args.data_augument_types, use_ddp = args.use_ddp, n_gpus = len(args.gpu_ids), debug = args.debug )
    if(args.use_ddp):
        #sampler_train = torch.utils.data.distributed.DistributedSampler(ds_train, num_replicas=len(args.gpu_ids), rank=args.local_rank, shuffle=True)
        #sampler_valid = torch.utils.data.distributed.DistributedSampler(ds_valid, num_replicas=len(args.gpu_ids), rank=args.local_rank, shuffle=False)
        sampler_train = torch.utils.data.distributed.DistributedSampler(ds_train, num_replicas=len(args.gpu_ids), rank=args.local_rank)
        sampler_valid = torch.utils.data.distributed.DistributedSampler(ds_valid, num_replicas=len(args.gpu_ids), rank=args.local_rank)
        dloader_train = torch.utils.data.DataLoader(sampler_train, batch_size=args.batch_size, sampler=sampler_train, shuffle=False, num_workers = args.n_workers//len(args.gpu_ids), pin_memory = True )
        dloader_valid = torch.utils.data.DataLoader(sampler_valid, batch_size=args.batch_size_valid, sampler=sampler_valid, shuffle=False, num_workers = 1, pin_memory = True )
    else:
        dloader_train = torch.utils.data.DataLoader(ds_train, batch_size=args.batch_size, shuffle=True, num_workers = args.n_workers, pin_memory = True )
        dloader_valid = torch.utils.data.DataLoader(ds_valid, batch_size=args.batch_size_valid, shuffle=False, num_workers = 1, pin_memory = True )

    #================================
    # モデルの構造を定義する。
    #================================
    #model_G = TempleteNetworks().to(device)
    model_G = Pix2PixHDGenerator().to(device)
    if( args.debug ):
        if( args.local_rank == 0 ):
            print( "model_G\n", model_G )

    # モデルを読み込む
    if not args.load_checkpoints_path == '' and os.path.exists(args.load_checkpoints_path):
        load_checkpoint(model_G, device, args.load_checkpoints_path )
        
    #================================
    # optimizer_G の設定
    #================================
    optimizer_G = optim.Adam( params = model_G.parameters(), lr = args.lr, betas = (args.beta1,args.beta2) )

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
    if( args.use_ddp ):
        if( args.use_amp ):
            model_G = apex.parallel.DistributedDataParallel(model_G)
        else:
            model_G = torch.nn.parallel.DistributedDataParallel(model_G, device_ids=[args.local_rank])
    else:
        if( len(args.gpu_ids) >= 2 ):
            model_G = torch.nn.DataParallel(model_G)

    #================================
    # loss 関数の設定
    #================================
    loss_fn = nn.L1Loss()

    #================================
    # モデルの学習
    #================================    
    print("Starting Training Loop...")
    n_print = 1
    step = 0
    for epoch in tqdm( range(args.n_epoches), desc = "epoches" ):
        for iter, inputs in enumerate( tqdm( dloader_train, desc = "epoch={}".format(epoch) ) ):
            model_G.train()

            # 一番最後のミニバッチループで、バッチサイズに満たない場合は無視する（後の計算で、shape の不一致をおこすため）
            if inputs["image"].shape[0] != args.batch_size:
                break

            # ミニバッチデータを GPU へ転送
            image = inputs["image"].to(device)
            target = inputs["target"].to(device)

            if( args.debug and n_print > 0):
                print( "[image] shape={}, dtype={}, device={}, min={}, max={}".format(image.shape, image.dtype, image.device, torch.min(image), torch.max(image)) )
                print( "[target] shape={}, dtype={}, device={}, min={}, max={}".format(target.shape, target.dtype, target.device, torch.min(target), torch.max(target)) )

            #----------------------------------------------------
            # 生成器 の forword 処理
            #----------------------------------------------------
            output = model_G( image )
            if( args.debug and n_print > 0 ):
                print( "output.shape : ", output.shape )

            #----------------------------------------------------
            # 生成器の更新処理
            #----------------------------------------------------
            # 損失関数を計算する
            loss_G = loss_fn( output, target )

            # ネットワークの更新処理
            optimizer_G.zero_grad()
            if( args.use_amp ):
                with amp.scale_loss(loss_G, optimizer_G, loss_id=0) as loss_G_scaled:
                    loss_G_scaled.backward()
            else:
                loss_G.backward()

            optimizer_G.step()
            
            #====================================================
            # 学習過程の表示
            #====================================================
            if( step == 0 or ( step % args.n_diaplay_step == 0 ) ):
                # 最初のプロセスのみで表示処理を行うようにする
                if( args.local_rank == 0 ):
                    # lr
                    for param_group in optimizer_G.param_groups:
                        lr = param_group['lr']

                    board_train.add_scalar('lr/learning rate', lr, step )

                    # loss
                    board_train.add_scalar('G/loss_G', loss_G.item(), step)
                    print( "step={}, loss_G={:.5f}".format(step, loss_G.item()) )

                    # visual images
                    visuals = [
                        [ image.detach(), target.detach(), output.detach() ],
                    ]
                    board_add_images(board_train, 'train', visuals, step+1)

            #====================================================
            # valid データでの処理
            #====================================================
            if( step == 0 or ( step % args.n_display_valid_step == 0 ) ):
                loss_G_total = 0
                n_valid_loop = 0
                for iter, inputs in enumerate( tqdm(dloader_valid, desc = "valid") ):
                    model_G.eval()            

                    # 一番最後のミニバッチループで、バッチサイズに満たない場合は無視する（後の計算で、shape の不一致をおこすため）
                    if inputs["image"].shape[0] != args.batch_size_valid:
                        break

                    # ミニバッチデータを GPU へ転送
                    image = inputs["image"].to(device)
                    target = inputs["target"].to(device)

                    # 推論処理
                    with torch.no_grad():
                        output = model_G( image )

                    # 損失関数を計算する
                    loss_G = loss_fn( output, target )
                    loss_G_total += loss_G

                    # 生成画像表示
                    if( iter <= args.n_display_valid ):
                        if( args.local_rank == 0 ):
                            # visual images
                            visuals = [
                                [ image.detach(), target.detach(), output.detach() ],
                            ]
                            board_add_images(board_valid, 'valid/{}'.format(iter), visuals, step+1)

                    n_valid_loop += 1

                # loss 値表示
                if( args.local_rank == 0 ):
                    board_valid.add_scalar('G/loss_G', loss_G_total.item()/n_valid_loop, step)

            step += 1
            n_print -= 1

        #====================================================
        # モデルの保存
        #====================================================
        if( epoch % args.n_save_epoches == 0 ):
            if( args.local_rank == 0 ):
                save_checkpoint( model_G, device, os.path.join(args.save_checkpoints_dir, args.exper_name, 'model_G_ep%03d.pth' % (epoch)) )
                save_checkpoint( model_G, device, os.path.join(args.save_checkpoints_dir, args.exper_name, 'model_G_final.pth') )
                print( "saved checkpoints" )

    print("Finished Training Loop.")
    if( args.local_rank == 0 ):
        save_checkpoint( model_G, device, os.path.join(args.save_checkpoints_dir, args.exper_name, 'model_G_final.pth') )

