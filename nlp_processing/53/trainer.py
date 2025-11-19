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
        outputs_student = model(**inputs)
        with torch.no_grad():
            outputs_teacher = self.teacher(**inputs)

        # Cross Entropy loss
        loss_ce = outputs_student.loss

        # ロジットのサイズを取得
        student_logits = outputs_student.logits
        teacher_logits = outputs_teacher.logits

        # 語彙サイズを揃える（モデル間で異なる場合）
        student_vocab_size = student_logits.size(-1)
        teacher_vocab_size = teacher_logits.size(-1)
        vocab_size = min(student_vocab_size, teacher_vocab_size)

        # 語彙サイズが異なる場合、小さい方に合わせる
        if student_vocab_size > vocab_size:
            student_logits_aligned = student_logits[..., :vocab_size]
        else:
            student_logits_aligned = student_logits

        if teacher_vocab_size > vocab_size:
            teacher_logits_aligned = teacher_logits[..., :vocab_size]
        else:
            teacher_logits_aligned = teacher_logits

        # シーケンス長を揃える（モデル間で異なる場合）
        student_seq_len = student_logits_aligned.size(1)
        teacher_seq_len = teacher_logits_aligned.size(1)
        seq_len = min(student_seq_len, teacher_seq_len)

        # シーケンス長が異なる場合、小さい方に合わせる
        if student_seq_len > seq_len:
            student_logits_aligned = student_logits_aligned[:, :seq_len, :]
        if teacher_seq_len > seq_len:
            teacher_logits_aligned = teacher_logits_aligned[:, :seq_len, :]

        # KL Divergence loss
        loss_kd = F.kl_div(
            F.log_softmax(student_logits_aligned / self.temperature, dim=-1),
            F.softmax(teacher_logits_aligned / self.temperature, dim=-1),
            reduction="batchmean",
        ) * (self.temperature**2)

        # Total loss: Cross Entropy loss と KL Divergence loss の線形結合
        loss = self.alpha * loss_ce + (1 - self.alpha) * loss_kd
        return (loss, outputs_student) if return_outputs else loss
