# coding=utf-8
import os
import io
from PIL import Image
import base64

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
    