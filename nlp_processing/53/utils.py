"""
Utility functions for monitoring memory usage
"""

from typing import Optional

import torch


def get_model_memory_usage(model: torch.nn.Module) -> dict:
    """
    モデルのメモリ使用量を計算

    Args:
        model: PyTorchモデル

    Returns:
        dict: メモリ使用量情報
            - params_mb: パラメータのメモリ使用量（MB）
            - buffers_mb: バッファのメモリ使用量（MB）
            - total_mb: 合計メモリ使用量（MB）
            - num_params: パラメータ数
    """
    param_size = 0
    buffer_size = 0
    num_params = 0

    # パラメータのサイズを計算
    for param in model.parameters():
        num_params += param.numel()
        param_size += param.numel() * param.element_size()

    # バッファのサイズを計算
    for buffer in model.buffers():
        buffer_size += buffer.numel() * buffer.element_size()

    # MBに変換
    param_mb = param_size / 1024 / 1024
    buffer_mb = buffer_size / 1024 / 1024
    total_mb = param_mb + buffer_mb

    return {
        "params_mb": param_mb,
        "buffers_mb": buffer_mb,
        "total_mb": total_mb,
        "num_params": num_params,
    }


def print_model_memory(model: torch.nn.Module, model_name: str = "Model", detailed: bool = True):
    """
    モデルのメモリ使用量を表示

    Args:
        model: PyTorchモデル
        model_name: モデル名（表示用）
        detailed: 詳細情報を表示するか
    """
    info = get_model_memory_usage(model)

    print(f"\n{'='*60}")
    print(f"📊 {model_name} - Memory Usage")
    print(f"{'='*60}")
    print(f"Parameters:     {info['num_params']:,} ({info['num_params']/1e6:.2f}M)")
    print(f"Memory (Params): {info['params_mb']:.2f} MB ({info['params_mb']/1024:.2f} GB)")

    if detailed:
        print(f"Memory (Buffers): {info['buffers_mb']:.2f} MB")
        print(f"Total Memory:    {info['total_mb']:.2f} MB ({info['total_mb']/1024:.2f} GB)")

    print(f"{'='*60}")


def get_gpu_memory_usage() -> Optional[dict]:
    """
    GPU メモリ使用量を取得

    Returns:
        dict or None: GPU メモリ情報（GPUが利用できない場合はNone）
            - allocated_mb: 割り当て済みメモリ（MB）
            - reserved_mb: 予約済みメモリ（MB）
            - total_mb: 総メモリ（MB）
    """
    if not torch.cuda.is_available():
        return None

    allocated = torch.cuda.memory_allocated() / 1024 / 1024
    reserved = torch.cuda.memory_reserved() / 1024 / 1024
    total = torch.cuda.get_device_properties(0).total_memory / 1024 / 1024

    return {
        "allocated_mb": allocated,
        "reserved_mb": reserved,
        "total_mb": total,
    }


def print_gpu_memory(detailed: bool = True):
    """
    GPU メモリ使用量を表示

    Args:
        detailed: 詳細情報を表示するか
    """
    info = get_gpu_memory_usage()

    if info is None:
        print("\n⚠️  GPU is not available")
        return

    print(f"\n{'='*60}")
    print(f"🎮 GPU Memory Usage")
    print(f"{'='*60}")
    print(f"Allocated: {info['allocated_mb']:.2f} MB ({info['allocated_mb']/1024:.2f} GB)")
    print(f"Reserved:  {info['reserved_mb']:.2f} MB ({info['reserved_mb']/1024:.2f} GB)")

    if detailed:
        print(f"Total:     {info['total_mb']:.2f} MB ({info['total_mb']/1024:.2f} GB)")
        usage_percent = (info["allocated_mb"] / info["total_mb"]) * 100
        print(f"Usage:     {usage_percent:.1f}%")

    print(f"{'='*60}")


def print_memory_summary(teacher_model: Optional[torch.nn.Module] = None, student_model: Optional[torch.nn.Module] = None, show_gpu: bool = True):
    """
    教師モデル、生徒モデル、GPUのメモリ使用量をまとめて表示

    Args:
        teacher_model: 教師モデル（オプション）
        student_model: 生徒モデル（オプション）
        show_gpu: GPUメモリも表示するか
    """
    print("\n" + "=" * 60)
    print("💾 Memory Summary")
    print("=" * 60)

    if teacher_model is not None:
        teacher_info = get_model_memory_usage(teacher_model)
        print(f"\n👨‍🏫 Teacher Model:")
        print(f"  Parameters: {teacher_info['num_params']:,} ({teacher_info['num_params']/1e6:.2f}M)")
        print(f"  Memory:     {teacher_info['total_mb']:.2f} MB ({teacher_info['total_mb']/1024:.2f} GB)")

    if student_model is not None:
        student_info = get_model_memory_usage(student_model)
        print(f"\n👨‍🎓 Student Model:")
        print(f"  Parameters: {student_info['num_params']:,} ({student_info['num_params']/1e6:.2f}M)")
        print(f"  Memory:     {student_info['total_mb']:.2f} MB ({student_info['total_mb']/1024:.2f} GB)")

    if teacher_model is not None and student_model is not None:
        ratio = teacher_info["num_params"] / student_info["num_params"]
        memory_ratio = teacher_info["total_mb"] / student_info["total_mb"]
        print(f"\n📊 Compression Ratio:")
        print(f"  Parameters: {ratio:.2f}x")
        print(f"  Memory:     {memory_ratio:.2f}x")

    if show_gpu:
        gpu_info = get_gpu_memory_usage()
        if gpu_info is not None:
            print(f"\n🎮 GPU Memory:")
            print(f"  Allocated: {gpu_info['allocated_mb']:.2f} MB ({gpu_info['allocated_mb']/1024:.2f} GB)")
            print(f"  Reserved:  {gpu_info['reserved_mb']:.2f} MB ({gpu_info['reserved_mb']/1024:.2f} GB)")
            print(f"  Total:     {gpu_info['total_mb']:.2f} MB ({gpu_info['total_mb']/1024:.2f} GB)")
            usage_percent = (gpu_info["allocated_mb"] / gpu_info["total_mb"]) * 100
            print(f"  Usage:     {usage_percent:.1f}%")

    print("=" * 60 + "\n")
