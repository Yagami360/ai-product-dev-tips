# coding=utf-8
import os
import sys
import argparse
import json
from PIL import Image
import numpy as np

from datetime import datetime
import logging
import uuid

# fastAPI
from fastapi import FastAPI
from fastapi import HTTPException
import uvicorn
from pydantic import BaseModel
from typing import Any, Dict

# PyTorch
import torch
import torch.optim as optim
try:
    from apex import amp
except ImportError:
    amp = None

# Graphonomy
sys.path.append(os.path.join(os.getcwd(), '../Graphonomy'))
from networks import deeplab_xception_transfer

# 自作モジュール
from inference_all import inference
from utils.utils import conv_base64_to_pillow, conv_pillow_to_base64
from utils.logger import log_base_decorator,log_decorator

#--------------------------
# logger
#--------------------------
if( os.path.exists(__name__ + '.log') ):
    os.remove(__name__ + '.log')
logger = logging.getLogger(__name__)
logger.setLevel(10)
logger_fh = logging.FileHandler( __name__ + '.log')
logger.addHandler(logger_fh)
logger.info("{} {} start api server".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", __name__))

#--------------------------
# FastAPI
#--------------------------
app = FastAPI()

class ImageData(BaseModel):
    """
    画像データのリクエストボディ
    """
    pose_img_base64: Any

#--------------------------
# モデルの初期化処理
#--------------------------
parser = argparse.ArgumentParser()
parser.add_argument('--host', type=str, default="0.0.0.0", help="ホスト名（コンテナ名 or コンテナ ID）")
parser.add_argument('--port', type=str, default="5000", help="ポート番号")
parser.add_argument('--device', choices=['cpu', 'gpu'], default="gpu", help="使用デバイス (CPU or GPU)")
parser.add_argument('--load_checkpoints_path', default='../checkpoints/universal_trained.pth', type=str, help="学習済みモデルのチェックポイントへのパス")
parser.add_argument('--use_amp', action='store_true', help="AMP [Automatic Mixed Precision] の使用有効化")
parser.add_argument('--opt_level', choices=['O0','O1','O2','O3'], default='O1', help='mixed precision calculation mode')
parser.add_argument('--debug', action='store_true', help="デバッグモード有効化")
#args = parser.parse_args()
args, unknown = parser.parse_known_args()   # uWSGI or gnicorn で API を起動した場合に argparse を有効にするための処理
if( args.debug ):
    for key, value in vars(args).items():
        print('%s: %s' % (str(key), str(value)))

if not os.path.exists("_debug"):
    os.mkdir("_debug")
    
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

# モデルの定義
model = deeplab_xception_transfer.deeplab_xception_transfer_projection_savemem(
    n_classes=20,
    hidden_layers=128,
    source_classes=7, 
).to(device)

print( "load_checkpoints_path : ", args.load_checkpoints_path )
if not args.load_checkpoints_path == '':
    if( args.device == "gpu" ):
        model.load_state_dict( torch.load(args.load_checkpoints_path), strict=False )
    else:
        model.load_state_dict( torch.load(args.load_checkpoints_path, map_location="cpu"), strict=False )
else:
    print('no model load !!!!!!!!')
    raise RuntimeError('No model!!!!')

# AMP の適用（使用メモリ削減効果）
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

#======================================
# GET method
#======================================
@app.get("/")
def root():
    return 'Hello Fast-API Server!\n'

@log_base_decorator(logger=logger)
def _health():
    return {"health": "ok"}

@app.get("/health")
def health():
    return _health()

@log_base_decorator(logger=logger)
def _metadata():
    return

@app.get("/metadata")
def metadata():
    return _metadata()

#======================================
# POST method
#======================================
from pydantic import BaseModel
# `pydantic.BaseModel` 継承クラスでリクエストボディを定義
class UserData(BaseModel):
    id: int
    name: str
    age: str

@log_decorator(logger=logger)
def _predict(
    job_id: str,            # ロギングでリクエスト処理を識別するための job_id
    img_data: ImageData,
):
    #------------------------------------------
    # 送信された画像データの変換
    #------------------------------------------
    pose_img_pillow = conv_base64_to_pillow( img_data.pose_img_base64 )
    if( args.debug ):
        pose_img_pillow.save( os.path.join( "_debug", "pose_img.png" ) )

    #------------------------------------------
    # 入力データのチェック
    #------------------------------------------
    img_w, img_h =pose_img_pillow.size
    if( img_h >= 1024 or img_w >= 1024 ):
        logger.info("{} {} {} job_id={} img_w={} img_h={} 入力画像サイズが大きすぎます".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, job_id, img_h, img_w))
        raise HTTPException(status_code=404, detail="Invalid input data")
        """
        return {
            "status": "ng",
            "pose_parse_img_base64" : None,
            "pose_parse_img_RGB_base64" : None,
        }
        """

    #------------------------------------------
    # Graphonomy の実行
    #------------------------------------------
    pose_parse_img_np, pose_parse_img_RGB_pillow = inference( net=model, img=pose_img_pillow, device=device )
    pose_parse_img_pillow = Image.fromarray( np.uint8(pose_parse_img_np.transpose(0,1)) , 'L')
    if( args.debug ):
        pose_parse_img_pillow.save( os.path.join( "_debug", "pose_parse_img.png" ) )
        pose_parse_img_RGB_pillow.save( os.path.join( "_debug", "pose_parse_img_vis.png" ) )

    #------------------------------------------
    # 送信する画像データの変換
    #------------------------------------------
    pose_parse_img_base64 = conv_pillow_to_base64( pose_parse_img_pillow )
    pose_parse_img_RGB_base64 = conv_pillow_to_base64( pose_parse_img_RGB_pillow )

    #------------------------------------------
    # レスポンスメッセージの設定
    #------------------------------------------
    return {
        "status": "ok",
        "pose_parse_img_base64" : pose_parse_img_base64,
        "pose_parse_img_RGB_base64" : pose_parse_img_RGB_base64,
    }

@app.post("/predict/")
def predict(
    img_data: ImageData,        # リクエストボディ  
):
    job_id = str(uuid.uuid4())[:6]
    return _predict(job_id=job_id, img_data=img_data)


if __name__ == "__main__":
    #--------------------------
    # FastAPI の起動
    #--------------------------
    uvicorn.run(app, host=args.host, port=args.port)