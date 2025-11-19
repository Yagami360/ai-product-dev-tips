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
        loss_kd = F.kl_div(
            F.log_softmax(outputs_student.logits / self.temperature, dim=-1),
            F.softmax(outputs_teacher.logits / self.temperature, dim=-1),
            reduction="batchmean",
        ) * (self.temperature**2)

        # Total loss: Cross Entropy loss と KL Divergence loss の線形結合
        loss = self.alpha * loss_ce + (1 - self.alpha) * loss_kd
        return (loss, outputs_student) if return_outputs else loss
