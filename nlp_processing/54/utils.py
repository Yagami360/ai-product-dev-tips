"""
ユーティリティ関数
メモリ使用量の監視など
"""

import torch


def get_model_memory_usage(model):
    """モデルのメモリ使用量を計算"""
    param_memory = 0
    buffer_memory = 0

    # パラメータのメモリ使用量
    for param in model.parameters():
        param_memory += param.numel() * param.element_size()

    # バッファのメモリ使用量
    for buffer in model.buffers():
        buffer_memory += buffer.numel() * buffer.element_size()

    return param_memory, buffer_memory


def print_model_memory(model, model_name, detailed=False):
    """モデルのメモリ使用量を表示"""
    param_memory, buffer_memory = get_model_memory_usage(model)
    total_memory = param_memory + buffer_memory

    # パラメータ数をカウント
    total_params = sum(p.numel() for p in model.parameters())

    print("=" * 60)
    print(f"📊 {model_name} - Memory Usage")
    print("=" * 60)
    print(f"Parameters:     {total_params:,} ({total_params/1e6:.2f}M)")
    print(
        f"Memory (Params): {param_memory / 1024**2:.2f} MB ({param_memory / 1024**3:.2f} GB)"
    )
    print(f"Memory (Buffers): {buffer_memory / 1024**2:.2f} MB")
    print(
        f"Total Memory:    {total_memory / 1024**2:.2f} MB ({total_memory / 1024**3:.2f} GB)"
    )
    print("=" * 60)

    if detailed:
        print("\nDetailed breakdown:")
        for name, param in model.named_parameters():
            size_mb = param.numel() * param.element_size() / 1024**2
            print(f"  {name}: {param.shape} -> {size_mb:.2f} MB")


def get_gpu_memory_usage():
    """GPU メモリ使用量を取得"""
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / 1024**2  # MB
        reserved = torch.cuda.memory_reserved() / 1024**2  # MB
        total = torch.cuda.get_device_properties(0).total_memory / 1024**2  # MB
        return allocated, reserved, total
    return 0, 0, 0


def print_gpu_memory(detailed=False):
    """GPU メモリ使用量を表示"""
    if not torch.cuda.is_available():
        print("GPU is not available")
        return

    allocated, reserved, total = get_gpu_memory_usage()

    print("\n🎮 GPU Memory Usage:")
    print(f"  Allocated: {allocated:.2f} MB ({allocated/1024:.2f} GB)")
    print(f"  Reserved:  {reserved:.2f} MB ({reserved/1024:.2f} GB)")
    print(f"  Total:     {total:.2f} MB ({total/1024:.2f} GB)")
    print(f"  Usage:     {reserved/total*100:.1f}%")

    if detailed:
        print("\n  Detailed GPU info:")
        print(f"    Device: {torch.cuda.get_device_name()}")
        print(f"    Capability: {torch.cuda.get_device_capability()}")


def print_memory_summary(teacher_model=None, student_model=None, show_gpu=True):
    """メモリ使用量のサマリーを表示"""
    print("\n" + "=" * 60)
    print("💾 Memory Summary")
    print("=" * 60)

    if teacher_model:
        teacher_params = sum(p.numel() for p in teacher_model.parameters())
        teacher_memory, _ = get_model_memory_usage(teacher_model)
        print(f"\n👨‍🏫 Teacher Model:")
        print(f"  Parameters: {teacher_params:,} ({teacher_params/1e6:.2f}M)")
        print(
            f"  Memory:     {teacher_memory / 1024**2:.2f} MB ({teacher_memory / 1024**3:.2f} GB)"
        )

    if student_model:
        student_params = sum(p.numel() for p in student_model.parameters())
        student_memory, _ = get_model_memory_usage(student_model)
        print(f"\n👨‍🎓 Student Model:")
        print(f"  Parameters: {student_params:,} ({student_params/1e6:.2f}M)")
        print(
            f"  Memory:     {student_memory / 1024**2:.2f} MB ({student_memory / 1024**3:.2f} GB)"
        )

    if teacher_model and student_model:
        print(f"\n📊 Compression Ratio:")
        print(f"  Parameters: {teacher_params / student_params:.2f}x")
        print(f"  Memory:     {teacher_memory / student_memory:.2f}x")

    if show_gpu:
        allocated, reserved, total = get_gpu_memory_usage()
        if total > 0:
            print(f"\n🎮 GPU Memory:")
            print(f"  Allocated: {allocated:.2f} MB ({allocated/1024:.2f} GB)")
            print(f"  Reserved:  {reserved:.2f} MB ({reserved/1024:.2f} GB)")
            print(f"  Total:     {total:.2f} MB ({total/1024:.2f} GB)")
            print(f"  Usage:     {reserved/total*100:.1f}%")

    print("=" * 60)
