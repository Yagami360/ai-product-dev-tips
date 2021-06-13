import os
import sys
import argparse
from collections import OrderedDict
from datetime import datetime
import random

import numpy as np
from PIL import Image
import cv2
#import socket
import timeit
from tqdm import tqdm
try:
    from apex import amp
except ImportError:
    amp = None

# PyTorch includes
import torch
import torch.optim as optim
from torch.autograd import Variable
from torchvision import transforms
import torch.nn.functional as F

# Graphonomy
sys.path.append(os.path.join(os.getcwd(), '../Graphonomy'))
from networks import deeplab_xception_transfer, graph
from dataloaders import custom_transforms as tr

# グローバル変数
label_colours = [(0,0,0)
                , (128,0,0), (255,0,0), (0,85,0), (170,0,51), (255,85,0), (0,0,85), (0,119,221), (85,85,0), (0,85,85), (85,51,0), (52,86,128), (0,128,0)
                , (0,0,255), (51,170,221), (0,255,255), (85,255,170), (170,255,85), (255,255,0), (255,170,0)]


def flip(x, dim):
    indices = [slice(None)] * x.dim()
    indices[dim] = torch.arange(x.size(dim) - 1, -1, -1,
                                dtype=torch.long, device=x.device)
    return x[tuple(indices)]

def flip_cihp(tail_list):
    '''

    :param tail_list: tail_list size is 1 x n_class x h x w
    :return:
    '''
    # tail_list = tail_list[0]
    tail_list_rev = [None] * 20
    for xx in range(14):
        tail_list_rev[xx] = tail_list[xx].unsqueeze(0)
    tail_list_rev[14] = tail_list[15].unsqueeze(0)
    tail_list_rev[15] = tail_list[14].unsqueeze(0)
    tail_list_rev[16] = tail_list[17].unsqueeze(0)
    tail_list_rev[17] = tail_list[16].unsqueeze(0)
    tail_list_rev[18] = tail_list[19].unsqueeze(0)
    tail_list_rev[19] = tail_list[18].unsqueeze(0)
    return torch.cat(tail_list_rev,dim=0)


def decode_labels(mask, num_images=1, num_classes=20):
    """Decode batch of segmentation masks.

    Args:
      mask: result of inference after taking argmax.
      num_images: number of images to decode from the batch.
      num_classes: number of classes to predict (including background).

    Returns:
      A batch with num_images RGB images of the same size as the input.
    """
    n, h, w = mask.shape
    assert (n >= num_images), 'Batch size %d should be greater or equal than number of images to save %d.' % (
    n, num_images)
    outputs = np.zeros((num_images, h, w, 3), dtype=np.uint8)
    for i in range(num_images):
        img = Image.new('RGB', (len(mask[i, 0]), len(mask[i])))
        pixels = img.load()
        for j_, j in enumerate(mask[i, :, :]):
            for k_, k in enumerate(j):
                if k < num_classes:
                    pixels[k_, j_] = label_colours[k]
        outputs[i] = np.array(img)
    return outputs

def read_img(img_path):
    _img = Image.open(img_path).convert('RGB')  # return is RGB pic
    return _img

def img_transform(img, transform=None):
    sample = {'image': img, 'label': 0}

    sample = transform(sample)
    return sample

def inference(net, img, device ):
    # adj
    adj2_ = torch.from_numpy(graph.cihp2pascal_nlp_adj).float()
    adj2_test = adj2_.unsqueeze(0).unsqueeze(0).expand(1, 1, 7, 20).to(device).transpose(2, 3)

    adj1_ = Variable(torch.from_numpy(graph.preprocess_adj(graph.pascal_graph)).float())
    adj3_test = adj1_.unsqueeze(0).unsqueeze(0).expand(1, 1, 7, 7).to(device)

    cihp_adj = graph.preprocess_adj(graph.cihp_graph)
    adj3_ = Variable(torch.from_numpy(cihp_adj).float())
    adj1_test = adj3_.unsqueeze(0).unsqueeze(0).expand(1, 1, 20, 20).to(device)

    # multi-scale
    scale_list = [1, 0.5, 0.75, 1.25, 1.5, 1.75]
    #img = read_img(img_path)
    testloader_list = []
    testloader_flip_list = []
    for pv in scale_list:
        composed_transforms_ts = transforms.Compose([
            tr.Scale_only_img(pv),
            tr.Normalize_xception_tf_only_img(),
            tr.ToTensor_only_img()])

        composed_transforms_ts_flip = transforms.Compose([
            tr.Scale_only_img(pv),
            tr.HorizontalFlip_only_img(),
            tr.Normalize_xception_tf_only_img(),
            tr.ToTensor_only_img()])

        testloader_list.append(img_transform(img, composed_transforms_ts))
        # print(img_transform(img, composed_transforms_ts))
        testloader_flip_list.append(img_transform(img, composed_transforms_ts_flip))

    # print(testloader_list)
    start_time = timeit.default_timer()

    # One testing epoch
    net.eval()

    # 1 0.5 0.75 1.25 1.5 1.75 ; flip:
    for iii, sample_batched in enumerate(zip(testloader_list, testloader_flip_list)):
        inputs, labels = sample_batched[0]['image'], sample_batched[0]['label']
        inputs_f, _ = sample_batched[1]['image'], sample_batched[1]['label']
        inputs = inputs.unsqueeze(0)
        inputs_f = inputs_f.unsqueeze(0)
        inputs = torch.cat((inputs, inputs_f), dim=0)
        if iii == 0:
            _, _, h, w = inputs.size()
        # assert inputs.size() == inputs_f.size()

        # Forward pass of the mini-batch
        inputs = Variable(inputs, requires_grad=False)

        with torch.no_grad():
            inputs = inputs.to(device)
            # outputs = net.forward(inputs)
            outputs = net.forward(inputs, adj1_test.to(device), adj3_test.to(device), adj2_test.to(device))
            outputs = (outputs[0] + flip(flip_cihp(outputs[1]), dim=-1)) / 2
            outputs = outputs.unsqueeze(0)

            if iii > 0:
                outputs = F.upsample(outputs, size=(h, w), mode='bilinear', align_corners=True)
                outputs_final = outputs_final + outputs
            else:
                outputs_final = outputs.clone()

    ################ plot pic
    predictions = torch.max(outputs_final, 1)[1]
    results = predictions.cpu().numpy()
    vis_res = decode_labels(results)

    parsing_im = Image.fromarray(vis_res[0])
    #parsing_im.save(output_path+'/{}.png'.format(output_name))
    #cv2.imwrite(output_path+'/{}_gray.png'.format(output_name), results[0, :, :])

    end_time = timeit.default_timer()
    print('time used for the multi-scale image inference' + ' is :' + str(end_time - start_time))
    return results[0, :, :], parsing_im

if __name__ == '__main__':
    '''argparse begin'''
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', choices=['cpu', 'gpu'], default="gpu", help="使用デバイス (CPU or GPU)")
    parser.add_argument('--in_image_dir', type=str, default="images", help="入力画像のディレクトリ" )
    parser.add_argument('--results_dir', type=str, default="results", help="生成画像の出力ディレクトリ")
    parser.add_argument('--load_checkpoints_path', default='checkpoints/universal_trained.pth', type=str, help="学習済みモデルのチェックポイントへのパス")
    parser.add_argument('--save_vis', action='store_true', help="視覚用のRGB画像の人物パース画像も保存するか否か")
    parser.add_argument("--seed", type=int, default=8, help="乱数シード値")
    parser.add_argument('--use_amp', action='store_true', help="AMP [Automatic Mixed Precision] の使用有効化")
    parser.add_argument('--opt_level', choices=['O0','O1','O2','O3'], default='O1', help='mixed precision calculation mode')
    parser.add_argument('--debug', action='store_true', help="デバッグモード有効化")
    args = parser.parse_args()
    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

    # 各種出力ディレクトリ
    if not( os.path.exists(args.results_dir) ):
        os.mkdir(args.results_dir)

    # 実行 Device の設定
    if( args.device == "gpu" ):
        use_cuda = torch.cuda.is_available()
        if( use_cuda == True ):
            device = torch.device( "cuda" )
            print( "実行デバイス :", device)
            print( "GPU名 :", torch.cuda.get_device_name(device))
            print("torch.cuda.current_device() =", torch.cuda.current_device())
        else:
            print( "can't using gpu." )
            device = torch.device( "cpu" )
            print( "実行デバイス :", device)
    else:
        device = torch.device( "cpu" )
        print( "実行デバイス :", device)

    # seed 値の固定
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed(args.seed)

    #-------------------------------
    # モデルの定義
    #-------------------------------
    model = deeplab_xception_transfer.deeplab_xception_transfer_projection_savemem(
        n_classes=20,
        hidden_layers=128,
        source_classes=7, 
    ).to(device)
    if( args.debug ):
        print( model )

    if not args.load_checkpoints_path == '':
        if( args.device == "gpu" ):
            #x = torch.load(args.load_checkpoints_path)
            #model.load_source_model(x)
            model.load_state_dict( torch.load(args.load_checkpoints_path), strict=False )
        else:
            model.load_state_dict( torch.load(args.load_checkpoints_path, map_location="cpu"), strict=False )
    else:
        print('no model load !!!!!!!!')
        raise RuntimeError('No model!!!!')

    #-------------------------------
    # AMP の適用（使用メモリ削減効果）
    #-------------------------------
    if( args.use_amp ):
        # dummy の optimizer
        optimizer = optim.Adam( params = model.parameters(), lr = 0.0001, betas = (0.5,0.999) )

        # amp initialize
        model, optimizer = amp.initialize(
            model, 
            optimizer, 
            opt_level = args.opt_level,
            num_losses = 1
        )

    #-------------------------------
    # フォルダ内の全画像に対して推論処理
    #-------------------------------
    image_names = sorted( [f for f in os.listdir(args.in_image_dir) if f.endswith(('.jpg','.jpeg','.png','.bmp'))] )
    for image_name in tqdm(image_names):
        in_img_path = os.path.join( args.in_image_dir, image_name )
        img = Image.open( os.path.join(args.in_image_dir, image_name ) )
        parse_img, parse_img_RGB = inference( net=model, img_path=in_img_path, device=device )

        cv2.imwrite( os.path.join( args.results_dir, image_name.split(".")[0] + ".png" ), parse_img )
        if( args.save_vis ):
            parse_img_RGB.save( os.path.join( args.results_dir, image_name.split(".")[0] + "_vis.png" ) )
