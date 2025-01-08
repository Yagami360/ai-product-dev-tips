import os

import imageio
import torch
import torch.nn as nn
from PIL import Image
from tensorboardX import SummaryWriter
from torchvision.utils import save_image


# ====================================================
# モデルの保存＆読み込み関連
# ====================================================
def save_checkpoint(model, device, save_path, step):
    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))

    torch.save(
        {
            "step": step,
            "model_state_dict": model.cpu().state_dict(),
        },
        save_path,
    )
    model.to(device)
    return


def save_checkpoint_wo_step(model, device, save_path):
    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))

    torch.save(model.cpu().state_dict(), save_path)
    model.to(device)
    return


def load_checkpoint(model, device, checkpoint_path):
    if not os.path.exists(checkpoint_path):
        return

    checkpoint = torch.load(checkpoint_path)
    model.load_state_dict(checkpoint["model_state_dict"])
    step = checkpoint["step"]
    model.to(device)
    return step


def load_checkpoint_wo_step(model, device, checkpoint_path):
    if not os.path.exists(checkpoint_path):
        return

    model.load_state_dict(torch.load(checkpoint_path))
    model.to(device)
    return


# ====================================================
# 画像の保存関連
# ====================================================
def save_image_historys_gif(images_historys, file_name="images_historys.gif"):
    """
    画像履歴を gif ファイルで保存
    """
    imageio.mimsave(file_name, images_historys)
    return


# ====================================================
# TensorBoard への出力関連
# ====================================================
def tensor_for_board(img_tensor):
    # map into [0,1]
    tensor = (img_tensor.clone() + 1) * 0.5
    tensor.cpu().clamp(0, 1)

    if tensor.size(1) == 1:
        tensor = tensor.repeat(1, 3, 1, 1)

    return tensor


def tensor_list_for_board(img_tensors_list):
    grid_h = len(img_tensors_list)
    grid_w = max(len(img_tensors) for img_tensors in img_tensors_list)

    batch_size, channel, height, width = tensor_for_board(img_tensors_list[0][0]).size()
    canvas_h = grid_h * height
    canvas_w = grid_w * width
    canvas = torch.FloatTensor(batch_size, channel, canvas_h, canvas_w).fill_(0.5)
    for i, img_tensors in enumerate(img_tensors_list):
        for j, img_tensor in enumerate(img_tensors):
            offset_h = i * height
            offset_w = j * width
            tensor = tensor_for_board(img_tensor)
            canvas[
                :, :, offset_h : offset_h + height, offset_w : offset_w + width
            ].copy_(tensor)

    return canvas


def board_add_image(board, tag_name, img_tensor, step_count, n_max_images=32):
    tensor = tensor_for_board(img_tensor)
    tensor = tensor[0 : min(tensor.shape[0], n_max_images)]
    for i, img in enumerate(tensor):
        board.add_image("%s/%03d" % (tag_name, i), img, step_count)


def board_add_images(board, tag_name, img_tensors_list, step_count, n_max_images=32):
    tensor = tensor_list_for_board(img_tensors_list)
    tensor = tensor[0 : min(tensor.shape[0], n_max_images)]
    for i, img in enumerate(tensor):
        board.add_image("%s/%03d" % (tag_name, i), img, step_count)


def save_images(img_tensors, img_names, save_dir):
    for img_tensor, img_name in zip(img_tensors, img_names):
        tensor = (img_tensor.clone() + 1) * 0.5 * 255
        tensor = tensor.cpu().clamp(0, 255)

        array = tensor.numpy().astype("uint8")
        if array.shape[0] == 1:
            array = array.squeeze(0)
        elif array.shape[0] == 3:
            array = array.swapaxes(0, 1).swapaxes(1, 2)

        Image.fromarray(array).save(os.path.join(save_dir, img_name))
