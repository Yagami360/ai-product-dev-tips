import argparse
import json
import subprocess
import unicodedata
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


FLEURS_IDS = [1519, 1608, 1607, 1634, 1625]
TTS_TEXTS = [
    "設備の状態を確認してください。",
    "設備Bは点検中です。",
    "期限は明日の午後五時です。",
]
ASR_MODELS = {
    "ReazonSpeech NeMo v2": ("reazonspeech-v2:q4_k",),
    "Qwen3-ASR 0.6B": ("qwen3-asr-0.6b:q4_k", "--language", "ja"),
    "Qwen3-ASR 1.7B": ("qwen3-asr-1.7b:q4_k", "--language", "ja"),
}
TTS_MODELS = {
    "Qwen3-TTS 0.6B": "qwen3-tts-0.6b:q4_k",
    "Qwen3-TTS 1.7B": "qwen3-tts-1.7b:q4_k",
}
QWEN_Q8_ASR = {"Qwen3-ASR 1.7B（Q8_0）": ("qwen3-asr-1.7b:q8_0", "--language", "ja")}
QWEN_Q8_TTS = {"Qwen3-TTS 1.7B（Q8_0）": "qwen3-tts-1.7b:q8_0"}


def request_bytes(url, *, data=None):
    headers = {"Content-Type": "application/json"} if data is not None else {}
    with urlopen(Request(url, data=data, headers=headers), timeout=90) as response:
        return response.read()


def fleurs_samples(directory):
    params = urlencode({
        "dataset": "google/fleurs", "config": "ja_jp", "split": "validation",
        "offset": 0, "length": len(FLEURS_IDS),
    })
    rows = json.loads(request_bytes(f"https://datasets-server.huggingface.co/rows?{params}"))["rows"]
    if [item["row"]["id"] for item in rows] != FLEURS_IDS:
        raise SystemExit("FLEURS の行 ID が実測時と異なります。")

    for item in rows:
        row = item["row"]
        audio_path = directory / f"fleurs-{row['id']}.wav"
        audio_path.write_bytes(request_bytes(row["audio"][0]["src"]))
        yield row["id"], row["raw_transcription"], audio_path


def tts_samples(directory, speech, device_options, models, voicevox_url):
    for index, reference in enumerate(TTS_TEXTS, start=1):
        for name, model in models.items():
            qwen_path = directory / f"{model.split(':')[0]}-{index}.wav"
            subprocess.run(
                [speech, "tts", model, *device_options,
                 "--language", "ja", "--voice", "ono_anna", "--seed", "42",
                 "-o", str(qwen_path), reference],
                check=True,
            )
            yield name, index, reference, qwen_path

        if voicevox_url:
            voicevox_path = directory / f"voicevox-{index}.wav"
            params = urlencode({"speaker": 1, "text": reference})
            query = request_bytes(f"{voicevox_url}/audio_query?{params}", data=b"")
            voicevox_path.write_bytes(request_bytes(f"{voicevox_url}/synthesis?speaker=1", data=query))
            yield "VOICEVOX ENGINE", index, reference, voicevox_path


def normalize(text):
    return "".join(
        char for char in unicodedata.normalize("NFKC", text).casefold()
        if not char.isspace() and not unicodedata.category(char).startswith("P")
    )


def edit_distance(reference, hypothesis):
    previous = list(range(len(hypothesis) + 1))
    for index, expected in enumerate(reference, start=1):
        current = [index]
        for column, actual in enumerate(hypothesis, start=1):
            current.append(min(
                previous[column] + 1,
                current[column - 1] + 1,
                previous[column - 1] + (expected != actual),
            ))
        previous = current
    return previous[-1]


def compare(samples, speech, device_options, asr_models=ASR_MODELS):
    totals = {}
    for source, sample_id, reference, audio_path in samples:
        normalized_reference = normalize(reference)
        for asr, model_options in asr_models.items():
            hypothesis = subprocess.check_output(
                [speech, "asr", *model_options, *device_options, str(audio_path)], text=True
            ).strip()
            errors = edit_distance(normalized_reference, normalize(hypothesis))
            counts = totals.setdefault((source, asr), [0, 0, 0, 0])
            counts[0] += errors
            counts[1] += len(normalized_reference)
            counts[2] += errors == 0
            counts[3] += 1
            print(f"{source} / {sample_id} / {asr}: {errors}/{len(normalized_reference)}")
            print(f"  参照: {reference}\n  転写: {hypothesis}")

    for (source, asr), (errors, characters, matches, samples_count) in totals.items():
        print(f"{source} / {asr}: CER {errors / characters:.2%} "
              f"({errors}/{characters}), 完全一致 {matches}/{samples_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="日本語の CPU 音声モデルを比較する")
    parser.add_argument("task", choices=("asr", "tts"))
    parser.add_argument("--speech", default="./speech-cpp/speech")
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--voicevox-url", default="http://127.0.0.1:50021")
    parser.add_argument("--qwen-q8", action="store_true", help="Qwen3 1.7B の Q8_0 版を評価する")
    args = parser.parse_args()
    suffix = "-qwen-q8" if args.qwen_q8 else ""
    directory = Path("_tmp") / f"evaluate-{args.task}{suffix}"
    directory.mkdir(parents=True, exist_ok=True)
    device_options = ("--device", "cpu", "--threads", str(args.threads))

    if args.task == "asr":
        asr_models = QWEN_Q8_ASR if args.qwen_q8 else ASR_MODELS
        samples = (("FLEURS", *sample) for sample in fleurs_samples(directory))
    else:
        asr_models = ASR_MODELS
        models = QWEN_Q8_TTS if args.qwen_q8 else TTS_MODELS
        voicevox_url = None if args.qwen_q8 else args.voicevox_url.rstrip("/")
        samples = tts_samples(directory, args.speech, device_options, models, voicevox_url)
    compare(samples, args.speech, device_options, asr_models)
