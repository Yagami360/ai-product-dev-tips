# -*- coding:utf-8 -*-
import os

import torch
import torch.nn as nn


# ====================================
# ResNet
# ====================================
class BasicBlock(nn.Module):
    """ """

    def __init__(
        self,
        n_in_channels=3,
        n_out_channels=3,
        stride=1,
    ):
        """
        [Args]
            n_in_channels : <int> 入力画像のチャンネル数
            n_out_channels : <int> 出力画像のチャンネル数
            stride : <int>
        """
        super(BasicBlock, self).__init__()
        self.layer1 = nn.Sequential(
            nn.Conv2d(
                n_in_channels, n_out_channels, kernel_size=3, stride=stride, padding=1
            ),
            nn.BatchNorm2d(n_out_channels),
            nn.LeakyReLU(0.2, inplace=True),
        )

        self.layer2 = nn.Sequential(
            nn.Conv2d(
                n_out_channels, n_out_channels, kernel_size=3, stride=1, padding=1
            ),
            nn.BatchNorm2d(n_out_channels),
        )

        # shortcut connection は、恒等写像
        self.shortcut_connections = nn.Sequential()

        # 入出力次元が異なる場合は、ゼロパディングで、次元の不一致箇所を０で埋める。
        if n_in_channels != n_out_channels:
            self.shortcut_connections = nn.Sequential(
                nn.Conv2d(
                    n_in_channels,
                    n_out_channels,
                    kernel_size=1,
                    stride=stride,
                    padding=0,
                    bias=False,
                ),
                nn.BatchNorm2d(n_out_channels),
            )

        return

    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)

        # shortcut connection からの経路を加算
        out += self.shortcut_connections(x)
        return out


class ResNet18(nn.Module):
    def __init__(self, n_in_channels=3, n_fmaps=64, n_classes=10):
        super(ResNet18, self).__init__()
        self.layer0 = nn.Sequential(
            nn.Conv2d(n_in_channels, n_fmaps, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm2d(n_fmaps),
            nn.LeakyReLU(0.2, inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1),
        )

        self.layer1 = nn.Sequential(
            BasicBlock(n_in_channels=n_fmaps, n_out_channels=n_fmaps, stride=1),
            BasicBlock(n_in_channels=n_fmaps, n_out_channels=n_fmaps, stride=1),
        )

        self.layer2 = nn.Sequential(
            BasicBlock(n_in_channels=n_fmaps, n_out_channels=n_fmaps * 2, stride=2),
            BasicBlock(n_in_channels=n_fmaps * 2, n_out_channels=n_fmaps * 2, stride=1),
        )

        self.layer3 = nn.Sequential(
            BasicBlock(n_in_channels=n_fmaps * 2, n_out_channels=n_fmaps * 4, stride=2),
            BasicBlock(n_in_channels=n_fmaps * 4, n_out_channels=n_fmaps * 4, stride=1),
        )

        self.layer4 = nn.Sequential(
            BasicBlock(n_in_channels=n_fmaps * 4, n_out_channels=n_fmaps * 8, stride=2),
            BasicBlock(n_in_channels=n_fmaps * 8, n_out_channels=n_fmaps * 8, stride=1),
        )

        self.avgpool = nn.AvgPool2d(7, stride=1)
        self.fc_layer = nn.Linear(n_fmaps * 8, n_classes)
        return

    def forward(self, x):
        out = self.layer0(x)  # 224x224
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)  # 7x7
        # out = torch.squeeze(out)

        out = self.avgpool(out)  # 1x1
        out = out.view(out.size(0), -1)
        out = self.fc_layer(out)
        return out
