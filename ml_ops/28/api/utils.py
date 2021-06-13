# coding=utf-8
import os
import io
from PIL import Image
import base64
import cv2
import numpy as np

import torch
import torch.nn as nn
from torchvision.utils import save_image

#====================================================
# 画像変換関連
#====================================================
def conv_base64_to_pillow( img_base64 ):
    decoded = base64.b64decode(img_base64)
    img_io = io.BytesIO(decoded)
    img_pillow = Image.open(img_io).convert('RGB')
    return img_pillow

def conv_pillow_to_base64( img_pillow ):
    buff = io.BytesIO()
    img_pillow.save(buff, format="PNG")
    img_binary = buff.getvalue()
    img_base64 = base64.b64encode(img_binary).decode('utf-8')
    return img_base64

def conv_tensor_to_pillow( img_tsr ):
    """
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5) 正規化した Tensor を Pillow に変換する。
    """
    img_tsr = (img_tsr.clone()+1)*0.5 * 255
    img_tsr = img_tsr.cpu().clamp(0,255)

    img_np = img_tsr.detach().numpy().astype('uint8')
    if img_np.shape[0] == 1:
        img_np = img_np.squeeze(0)
        img_np = img_np.swapaxes(0, 1).swapaxes(1, 2)
    elif img_np.shape[0] == 3:
        img_np = img_np.swapaxes(0, 1).swapaxes(1, 2)

    #Image.fromarray(img_np).save(save_img_paths)
    return Image.fromarray(img_np)

#====================================================
# モデルの保存＆読み込み関連
#====================================================
def save_checkpoint(model, device, save_path):
    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))

    torch.save(model.cpu().state_dict(), save_path)
    model.to(device)
    return

def save_checkpoint_w_step(model, device, save_path, step):
    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))

    torch.save(
        {
            'step': step,
            'model_state_dict': model.cpu().state_dict(),
        }, save_path
    )
    model.to(device)
    return

def load_checkpoint(model, device, checkpoint_path):
    if not os.path.exists(checkpoint_path):
        return
        
    model.load_state_dict(torch.load(checkpoint_path))
    model.to(device)
    return

def load_checkpoint_w_step(model, device, checkpoint_path):
    if not os.path.exists(checkpoint_path):
        return
        
    checkpoint = torch.load(checkpoint_path)
    model.load_state_dict(checkpoint["model_state_dict"])
    step = checkpoint['step']
    model.to(device)
    return step