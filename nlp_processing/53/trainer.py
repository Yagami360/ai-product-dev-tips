import json
import os
from datetime import datetime
from typing import Any, Dict, Optional, Union

import torch
import torch.nn.functional as F
from transformers import Trainer


class LogitDistillationTrainer(Trainer):
    def __init__(self, teacher_model, temperature=2.0, alpha=0.5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.teacher = teacher_model
        self.teacher.eval()
        self.temperature = temperature
        self.alpha = alpha
        for param in self.teacher.parameters():
            param.requires_grad = False

    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        # [compute_loss] inputs: {
        #     'input_ids': tensor([[    48,     25,  32016,  ..., 151643, 151643, 151643],
        #         [    48,     25,  10978,  ..., 151643, 151643, 151643],
        #         [    48,     25,   2619,  ..., 151643, 151643, 151643],
        #         [    48,     25,  43924,  ..., 151643, 151643, 151643]],
        #        device='cuda:0'),
        #   'attention_mask': tensor([[1, 1, 1,  ..., 0, 0, 0],
        #         [1, 1, 1,  ..., 0, 0, 0],
        #         [1, 1, 1,  ..., 0, 0, 0],
        #         [1, 1, 1,  ..., 0, 0, 0]], device='cuda:0'),
        #   'labels': tensor([[   48,    25, 32016,  ...,  -100,  -100,  -100],
        #         [   48,    25, 10978,  ...,  -100,  -100,  -100],
        #         [   48,    25,  2619,  ...,  -100,  -100,  -100],
        #         [   48,    25, 43924,  ...,  -100,  -100,  -100]], device='cuda:0')}
        # print("[compute_loss] inputs:", inputs)

        # 教師モデルの推論結果（正解データ）
        with torch.no_grad():
            outputs_teacher = self.teacher(**inputs)

        # 生徒モデルの推論結果（予測データ）
        outputs_student = model(**inputs)

        # Cross Entropy loss　(hard target loss)
        # 学習用データセットの正解データと生徒モデルの予測データ間の loss。生徒モデルの出力が正解データに近づくようにする
        # Hugging Face の transformers の AutoModelForCausalLM では、モデルを呼び出す際 (model(**inputs)) に、入力データ (inputs) に labels (正解データ) が含まれている場合、モデルは内部でクロスエントロピー損失 (Cross Entropy Loss) を自動的に計算し、.loss 属性に格納
        loss_ce = outputs_student.loss

        # KL Divergence loss (soft target loss)
        # 教師モデルの確率分布と生徒モデルの確率分布間の距離を最小化し、生徒モデルの出力が教師モデルの出力に近づくようにする
        # loss_kd = F.kl_div(
        #     F.log_softmax(outputs_student.logits / self.temperature, dim=-1),
        #     F.softmax(outputs_teacher.logits / self.temperature, dim=-1),
        #     reduction="batchmean",
        # ) * (self.temperature**2)

        # KL Divergence を計算（reduction="none" で各要素ごとの loss を取得）
        student_logits = outputs_student.logits / self.temperature
        teacher_logits = outputs_teacher.logits / self.temperature
        loss_kd = F.kl_div(
            F.log_softmax(student_logits, dim=-1),
            F.softmax(teacher_logits, dim=-1),
            reduction="none",
        ).sum(dim=-1)

        # attention_mask を適用して有効なトークンのみの平均を取る（パディングトークンを計算対象から除外）
        attention_mask = inputs.get("attention_mask", None)
        if attention_mask is not None:
            loss_kd = (loss_kd * attention_mask).sum() / attention_mask.sum()
        else:
            loss_kd = loss_kd.mean()

        loss_kd = loss_kd * (self.temperature**2)

        # Total loss: Cross Entropy loss と KL Divergence loss の線形結合
        loss = self.alpha * loss_ce + (1 - self.alpha) * loss_kd
        return (loss, outputs_student) if return_outputs else loss
