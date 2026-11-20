import argparse
import asyncio
import base64
import os
import wave
from pathlib import Path

from dotenv import dotenv_values
from google import genai
from google.genai import types


def transcribe(client, audio_path):
    upload_config = {"mime_type": "audio/wav"} if audio_path.suffix.lower() == ".wav" else None
    audio_file = client.files.upload(file=audio_path, config=upload_config)
    try:
        result = client.interactions.create(
            model="gemini-3.5-transcribe",
            input=[{"type": "audio", "uri": audio_file.uri, "mime_type": audio_file.mime_type}],
        )
    finally:
        client.files.delete(name=audio_file.name)
    if not result.output_text:
        raise SystemExit("文字起こし結果が空です。")
    print(result.output_text)


def synthesize(client, text, output_path):
    result = client.interactions.create(
        model="gemini-3.8-flash-lite-tts",
        input=[{"type": "user_input", "content": [{"type": "text", "text": text}]}],
        response_format={"type": "audio"},
        generation_config={"speech_config": [{"voice": "Kore"}]},
    )
    audio = result.output_audio
    if not audio or not audio.data:
        raise SystemExit("合成音声が返りませんでした。")
    output_path.write_bytes(base64.b64decode(audio.data))


async def live_lookup(client, input_path):
    with wave.open(str(input_path), "rb") as recording:
        audio_format = (recording.getnchannels(), recording.getsampwidth(), recording.getframerate())
        if audio_format != (1, 2, 16000):
            raise SystemExit("16 kHz / 16-bit / mono の WAV を指定してください。")
        frame_count = recording.getnframes()
        if not 0 < frame_count <= 16_000 * 30:
            raise SystemExit("30 秒以内の空でない WAV を指定してください。")
        pcm = recording.readframes(frame_count)

    config = {
        "response_modalities": ["AUDIO"],
        "system_instruction": (
            "日本語で回答してください。設備の状態を聞かれたら "
            "lookup_equipment を呼び、結果を日本語の音声で伝えてください。"
        ),
        "realtime_input_config": {"automatic_activity_detection": {"disabled": True}},
        "tools": [{"function_declarations": [{
            "name": "lookup_equipment",
            "description": "模擬設備の状態を取得する",
            "parameters": {
                "type": "OBJECT",
                "properties": {"equipment_id": {"type": "STRING", "enum": ["A", "B"]}},
                "required": ["equipment_id"],
            },
        }]}],
    }
    statuses = {"A": "稼働中", "B": "点検中"}
    response_pcm = bytearray()
    async with client.live.connect(model="gemini-3.8-live", config=config) as session:
        await session.send_realtime_input(activity_start=types.ActivityStart())
        chunk_size = 3200  # 16 kHz、16-bit、mono の 100 ms 分
        for offset in range(0, len(pcm), chunk_size):
            await session.send_realtime_input(
                audio=types.Blob(
                    data=pcm[offset:offset + chunk_size], mime_type="audio/pcm;rate=16000"
                )
            )
        await session.send_realtime_input(activity_end=types.ActivityEnd())

        # ツール要求のターンと、結果を読み上げるターンが分かれることがある。
        waiting_for_tool_audio = True
        while waiting_for_tool_audio:
            waiting_for_tool_audio = False
            async for message in session.receive():
                if audio := message.data:
                    response_pcm.extend(audio)
                    waiting_for_tool_audio = False
                if message.tool_call:
                    responses = []
                    for call in message.tool_call.function_calls or []:
                        equipment_id = (call.args or {}).get("equipment_id")
                        if call.name == "lookup_equipment" and equipment_id in ("A", "B"):
                            result = {"equipment_id": equipment_id, "status": statuses[equipment_id]}
                        else:
                            result = {"error": "設備 A または B を指定してください。"}
                        print(f"{call.name} -> {result}")
                        responses.append(types.FunctionResponse(id=call.id, name=call.name, response=result))
                    if responses:
                        await session.send_tool_response(function_responses=responses)
                        waiting_for_tool_audio = True

    if not response_pcm:
        raise SystemExit("音声応答が返りませんでした。")
    return response_pcm


async def run_live(client, input_path, output_path):
    async with client.aio as async_client:
        try:
            pcm = await asyncio.wait_for(live_lookup(async_client, input_path), timeout=90)
        except asyncio.TimeoutError:
            raise SystemExit("90 秒以内に Live API の応答が完了しませんでした。") from None
    with wave.open(str(output_path), "wb") as recording:
        recording.setparams((1, 2, 24000, 0, "NONE", "not compressed"))
        recording.writeframes(pcm)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gemini の日本語音声 API を試す")
    subparsers = parser.add_subparsers(dest="command", required=True)

    asr_parser = subparsers.add_parser("asr", help="音声ファイルの ASR（文字起こし）")
    asr_parser.add_argument("audio", type=Path)

    tts_parser = subparsers.add_parser("tts", help="テキストの TTS（読み上げ）")
    tts_parser.add_argument("text")
    tts_parser.add_argument("--output", type=Path, default=Path("gemini-tts.wav"))

    live_parser = subparsers.add_parser("live", help="Live API で設備の状態を照会する")
    live_parser.add_argument("audio", type=Path)
    live_parser.add_argument("--output", type=Path, default=Path("gemini-live.wav"))

    args = parser.parse_args()
    settings = dotenv_values(Path(__file__).with_name(".env"))
    api_key = settings.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        parser.error(".env の GEMINI_API_KEY に API キーを設定してください。")

    with genai.Client(api_key=api_key, vertexai=False, http_options={"api_version": "v1beta"}) as client:
        if args.command == "asr":
            transcribe(client, args.audio)
        elif args.command == "tts":
            synthesize(client, args.text, args.output)
        else:
            asyncio.run(run_live(client, args.audio, args.output))
