"""
SensorLLM（Stage1: Sensor-Language Alignment）の単一サンプル推論リファレンス。

公式実装 https://github.com/cruiseresearchgroup/SensorLLM の eval.py の
モデルロード・生成フローに忠実に、1 チャネル分のセンサー時系列（例: 加速度）を
Chronos エンコーダで埋め込み、LLaMA 側に align された Stage1 モデルで
「そのセンサー信号のトレンドを自然言語で説明させる」推論を 1 件だけ実行する。

■ 前提（重要）
  - 公式リポジトリ cruiseresearchgroup/SensorLLM を clone し、その中の `sensorllm`
    パッケージを import できる状態で実行すること（本スクリプトは同リポジトリを
    PYTHONPATH に通して使う。run_predict.sh 参照）。
  - 著者は学習済みチェックポイントを配布していないため、既定では第三者による
    非公式チェックポイント `1EE1/SensorLLM-Stage1-Backup`（MHealth で学習された
    Stage1 重み・TinyLlama-1.1B 系ベース）をロードする。非公式のため出力の
    信頼性は担保されない。自分で 2 段学習した重みがあれば --model-path で差し替える。
  - 時系列エンコーダは Chronos（--chronos-path）。既定 ckpt(1EE1)は chronos-t5-base(768)で
    学習されているため既定は amazon/chronos-t5-base。使う ckpt の学習時サイズに合わせること。
  - GPU: 学習は Ampere 以降必須（flash-attn 2 + bf16）だが、本推論スクリプトは
    flash-attn を import しないため、--dtype float16 にすれば T4 / V100 でも動作可能
    （本 ckpt は約 2GB + Chronos 約 1.5GB で 16GB に収まる）。A100 等では bf16 でよい。

■ 注意
  本スクリプトは GPU の無い作成環境では実行検証できていない（[In-progress]）。
  A100 等の実 GPU で挙動を確認し、必要に応じてトークン方式・チャネル・系列長を調整すること。
"""

import argparse

import numpy as np
import torch
from transformers import AutoConfig, AutoTokenizer

# --- 公式リポジトリ(cruiseresearchgroup/SensorLLM)の内部モジュールを利用 ---
from sensorllm.model import SensorLLMStage1LlamaForCausalLM
from sensorllm.model.chronos_model import ChronosConfig
from sensorllm.data.utils import generate_chat_template, get_token_dict
from sensorllm.utils import disable_torch_init

# eval.py と同じシステムプロンプト
SYS_INST = (
    "A chat between a curious human and an AI assistant. The assistant is given a "
    "sequence of N features that represent information extracted from sensor "
    "(time-series) readings. The original readings consisted of N data points "
    "collected at a sample rate of 100Hz. The assistant's task is to analyze the "
    "trends and patterns in the sensor readings by leveraging the encoded "
    "information within the features to answer the following specific questions "
    "provided by the human."
)

DTYPE_MAP = {"float32": torch.float32, "float16": torch.float16, "bfloat16": torch.bfloat16}


def parse_args():
    parser = argparse.ArgumentParser(description="SensorLLM Stage1 単一サンプル推論")
    parser.add_argument("--model-path", type=str, default="1EE1/SensorLLM-Stage1-Backup",
                        help="Stage1 チェックポイント(既定は非公式の MHealth 学習済み重み)")
    parser.add_argument("--chronos-path", type=str, default="amazon/chronos-t5-base",
                        help="時系列エンコーダ(Chronos)のチェックポイント。"
                             "既定 ckpt(1EE1)は chronos-t5-base(d_model=768)で学習されている。"
                             "この場合 sensorllm/model/ts_backbone.yaml の encoder_output_dim を 768 に、"
                             "name を chronos-t5-base に合わせること(不一致だと ts_proj で size mismatch)")
    parser.add_argument("--dataset", type=str, default="mhealth",
                        help="ts_backbone.yaml のデータセット名(既定 ckpt は mhealth で学習)")
    parser.add_argument("--channel", type=str, default=None,
                        help="センサーチャネル名(未指定なら当該データセットの先頭チャネル)")
    parser.add_argument("--tokenize-method", type=str, default="StanNormalizeUniformBins",
                        help="Chronos のトークン化方式(学習時と揃える)")
    parser.add_argument("--dtype", type=str, default="bfloat16", choices=list(DTYPE_MAP),
                        help="T4/V100 では float16 を指定する")
    parser.add_argument("--device", type=str, default="cuda", choices=["cuda", "cpu"])
    parser.add_argument("--input", type=str, default=None,
                        help="1 次元センサー系列の .npy パス(未指定なら合成波形を生成)")
    parser.add_argument("--length", type=int, default=200, help="合成波形の系列長")
    parser.add_argument("--question", type=str,
                        default="What is the overall trend of this sensor reading?",
                        help="モデルへの質問")
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--temperature", type=float, default=0.6)
    parser.add_argument("--seed", type=int, default=0, help="合成波形の乱数シード(再現性)")
    parser.add_argument("--plot", type=str, default=None, help="入力センサー信号を保存する PNG パス")
    return parser.parse_args()


def load_model(args, dtype):
    """eval.py の init_model() と同じ手順でモデル・トークナイザ・Chronos を用意する。"""
    disable_torch_init()
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, padding_side="left")
    model = SensorLLMStage1LlamaForCausalLM.from_pretrained(
        args.model_path, low_cpu_mem_usage=False, use_cache=False, torch_dtype=dtype
    ).to(args.device)

    # 時系列エンコーダ(Chronos)のバックボーンをロード
    model.get_model().load_pt_encoder_backbone_checkpoint(
        args.chronos_path, tc=args.tokenize_method, torch_dtype=dtype
    )
    pt_backbone_config = AutoConfig.from_pretrained(args.chronos_path)
    assert hasattr(pt_backbone_config, "chronos_config"), "Chronos の config ではありません"
    chronos_config = ChronosConfig(**pt_backbone_config.chronos_config)
    chronos_config.tokenizer_class = args.tokenize_method
    chronos_tokenizer = chronos_config.create_tokenizer()

    # 特殊トークン・センサーチャネル設定をデータセットに合わせて初期化
    model.initialize_tokenizer_ts_backbone_config_wo_embedding(tokenizer, dataset=args.dataset)
    model.get_model().load_start_end_tokens(dataset=args.dataset)
    return model, tokenizer, chronos_tokenizer


def build_sensor_series(args):
    """1 チャネル分のセンサー系列を用意する(--input が無ければ合成波形)。"""
    if args.input:
        arr = np.squeeze(np.load(args.input).astype(np.float32))
        if arr.ndim != 1:
            raise ValueError(
                f"--input は 1 チャネル（1 次元）のセンサー系列を指定してください。"
                f"多チャネル（shape={arr.shape}）は Stage1 の単一チャネル推論では扱えません。"
            )
        series = arr
    else:
        # 周期成分 + トレンド + ノイズの合成加速度っぽい波形（--seed で再現性を固定）
        np.random.seed(args.seed)
        t = np.linspace(0, 4 * np.pi, args.length)
        series = (np.sin(t) + 0.3 * np.sin(3 * t) + 0.02 * t
                  + 0.05 * np.random.randn(args.length)).astype(np.float32)
    return torch.tensor(series, dtype=torch.float32)


def build_prompt(args, model, tokenizer, chronos_tokenizer, series):
    """dataset_stage1 の preprocess_time_series2 と同じ規則でプロンプトと ts トークンを作る。"""
    ts_backbone_config = model.get_model().ts_backbone_config
    data_args = dict(ts_backbone_config[args.dataset])
    data_args["default_ts_token"] = ts_backbone_config["default_ts_token"]           # "<ts>"
    last_token = ts_backbone_config["chronos_model"]["last_token"]                    # True

    start_tokens, end_tokens = get_token_dict(args.dataset, data_args)
    channel = args.channel or list(start_tokens.keys())[0]
    assert channel in start_tokens, f"利用可能なチャネル: {list(start_tokens.keys())}"
    print(f"[INFO] 利用可能なチャネル: {list(start_tokens.keys())}")
    print(f"[INFO] 使用チャネル: {channel}")

    # Chronos で系列を離散トークン化(eval の dataset と同じ context_input_transform)
    context = series.unsqueeze(0)  # (1, L)
    ts_token_ids, ts_attention_mask, _ = chronos_tokenizer.context_input_transform(context)

    # <ts> プレースホルダ数は Chronos の実出力トークン長に一致させる。
    # context_input_transform の出力長は EOS を含む min(系列長, context_length)+1 なので、
    # last_token=True なら EOS 込みのトークン長そのもの、False なら EOS を除いた長さを使う。
    # 生系列長ではなく tokenized 長を使うことで、context_length(既定 512)による切り詰めが
    # 起きても、Chronos エンコーダが出力する埋め込み数とプレースホルダ数が一致する。
    ts_token = data_args["default_ts_token"]
    n_ts = ts_token_ids.shape[-1] - (0 if last_token else 1)
    modified_q = start_tokens[channel] + ts_token * n_ts + end_tokens[channel] + args.question

    prompt = generate_chat_template(
        [{"role": "system", "content": SYS_INST}, {"role": "user", "content": modified_q}],
        bos_token=tokenizer.bos_token, eos_token=tokenizer.eos_token, add_generation_prompt=True,
    )
    inputs = tokenizer([prompt], padding=True, return_tensors="pt").to(model.device)
    return inputs, ts_token_ids.to(model.device), ts_attention_mask.to(model.device)


@torch.inference_mode()
def generate(model, tokenizer, inputs, ts_token_ids, ts_attention_mask, args):
    model.eval()
    model.get_model().pt_encoder_backbone.eval()
    # Llama-3 系なら <|eot_id|> も終端に加える(存在しない ckpt では eos のみ)
    terminators = [tokenizer.eos_token_id]
    eot = tokenizer.convert_tokens_to_ids("<|eot_id|>")
    if eot is not None and eot != tokenizer.unk_token_id:
        terminators.append(eot)

    outputs = model.generate(
        **inputs,
        ts_token_ids=[ts_token_ids],           # eval.py と同じくサンプルごとの list
        ts_attention_mask=[ts_attention_mask],
        do_sample=True,
        use_cache=False,
        temperature=args.temperature,
        top_k=50,
        top_p=0.9,
        max_new_tokens=args.max_new_tokens,
        eos_token_id=terminators,
        pad_token_id=tokenizer.pad_token_id,
    )
    input_len = inputs.input_ids.shape[1]
    text = tokenizer.batch_decode(outputs[:, input_len:], skip_special_tokens=True)[0]
    return text.strip()


def save_plot(series, path, title):
    """入力センサー信号(1 チャネル)を折れ線で PNG 保存する。"""
    import os
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    plt.figure(figsize=(9, 3))
    plt.plot(series.numpy(), color="#1f77b4", linewidth=1.2)
    plt.title(title)
    plt.xlabel("time step")
    plt.ylabel("sensor value")
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()
    print(f"[INFO] 入力センサー信号を保存: {path}")


if __name__ == "__main__":
    args = parse_args()
    dtype = DTYPE_MAP[args.dtype]

    model, tokenizer, chronos_tokenizer = load_model(args, dtype)
    series = build_sensor_series(args)
    if args.plot:
        save_plot(series, args.plot, f"input sensor signal (channel={args.channel or 'auto'})")
    inputs, ts_token_ids, ts_attention_mask = build_prompt(
        args, model, tokenizer, chronos_tokenizer, series
    )

    print("\n===== 質問 (Question) =====")
    print(args.question)
    print("\n===== SensorLLM の出力(センサー信号のトレンド説明) =====")
    print(generate(model, tokenizer, inputs, ts_token_ids, ts_attention_mask, args))
