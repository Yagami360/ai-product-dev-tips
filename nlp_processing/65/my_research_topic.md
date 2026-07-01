# Title: Revisiting Simple Regularization for Small-Data Image Classification

## Keywords
regularization, small data, image classification, label smoothing, mixup

## TL;DR
On small labeled datasets, do modern regularizers (mixup, label smoothing) still help a small CNN, or do simpler choices win? Run controlled, low-cost experiments to find out.

## Abstract
Modern deep learning regularization techniques such as mixup and label smoothing are widely adopted, but most evidence comes from large-scale benchmarks. In many practical, resource-constrained settings only a few thousand labeled images are available, and it is unclear whether these regularizers still provide a reliable benefit or whether their effect shrinks (or reverses) in the small-data regime. This project studies, in a deliberately small and cheap experimental setting, how a compact convolutional network's generalization is affected by (1) label smoothing, (2) mixup, and (3) their combination, compared to a plain baseline with only standard data augmentation. We control for training budget and random seeds, report mean and variance across seeds, and analyze not only final accuracy but also calibration (expected calibration error) and robustness to a small amount of label noise. The goal is a clear, reproducible answer to a narrow question—"which simple regularizer should I reach for first on small image datasets?"—that can be produced end-to-end at low compute cost, making it a good target for an autonomous research agent running on local models. We expect the findings to surface non-obvious trade-offs (e.g. accuracy vs. calibration) that are easy to overlook when only headline accuracy on large benchmarks is reported.
