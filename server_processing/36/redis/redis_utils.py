import os
import io
import base64
from PIL import Image
import redis

def set_image_pillow_redis( redis_client, key_name, img_pillow ):
    """
    Pillow での画像データを Redis に追加
    """
    # Pillow データを base64 形式に変換
    bytes_io = io.BytesIO()
    img_pillow.save(bytes_io, format=img_pillow.format)
    img_base64 = base64.b64encode(bytes_io.getvalue())

    # base64 形式での画像データを追加
    redis_client.set(key_name, img_base64)
    return

def get_image_pillow_redis( redis_client, key_name ):
    """
    Redis の 画像データを Pillow 形式で取得
    """
    img_base64 = redis_client.get(key_name)
    img_base64 = base64.b64decode(img_base64)
    io_bytes = io.BytesIO(img_base64)
    img_pillow = Image.open(io_bytes)
    return img_pillow
    