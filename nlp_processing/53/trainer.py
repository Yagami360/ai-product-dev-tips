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

        # KL Divergence loss
        loss_kd = F.kl_div(
            F.log_softmax(outputs_student.logits / self.temperature, dim=-1),
            F.softmax(outputs_teacher.logits / self.temperature, dim=-1),
            reduction="batchmean",
        ) * (self.temperature**2)

        # Total loss: Cross Entropy loss と KL Divergence loss の線形結合
        loss = self.alpha * loss_ce + (1 - self.alpha) * loss_kd
        return (loss, outputs_student) if return_outputs else loss
