import argparse
import asyncio
import base64
import json
import os
import wave
from pathlib import Path

from dotenv import dotenv_values
from openai import AsyncOpenAI, AuthenticationError, OpenAI
from websockets.exceptions import ConnectionClosedError


REALTIME_MODEL = "gpt-realtime-2.1-mini"
PCM_RATE = 24000
EQUIPMENT_STATUS = {"A": "稼働中", "B": "点検中"}
LOOKUP_EQUIPMENT = {
    "type": "function",
    "name": "lookup_equipment",
    "description": "模擬設備の状態を取得する",
    "parameters": {
        "type": "object",
        "properties": {"equipment_id": {"type": "string", "enum": ["A", "B"]}},
        "required": ["equipment_id"],
        "additionalProperties": False,
    },
}


def transcribe(client, audio_path):
    with audio_path.open("rb") as recording:
        result = client.audio.transcriptions.create(model="gpt-transcribe", file=recording)
    if not result.text:
        raise SystemExit("文字起こし結果が空です。")
    print(result.text)


def read_pcm(audio_path):
    with wave.open(str(audio_path), "rb") as recording:
        if (recording.getnchannels(), recording.getsampwidth(), recording.getframerate()) != (1, 2, PCM_RATE):
            raise SystemExit("24 kHz / 16-bit / mono の WAV を指定してください。")
        frames = recording.getnframes()
        if not PCM_RATE // 10 <= frames <= PCM_RATE * 30:
            raise SystemExit("100 ms 以上、30 秒以内の WAV を指定してください。")
        return recording.readframes(frames)


async def realtime_audio(client, content):
    dialogue = content["type"] == "input_audio"
    audio_format = {"type": "audio/pcm", "rate": PCM_RATE}
    session = {"type": "realtime", "output_modalities": ["audio"], "audio": {
        "output": {"format": audio_format, "voice": "marin"},
    }}
    if dialogue:
        session["audio"]["input"] = {"format": audio_format, "turn_detection": None}
        session["instructions"] = "設備の状態を聞かれたら lookup_equipment を使い、日本語で結果を答えてください。"
        session["tools"] = [LOOKUP_EQUIPMENT]
    else:
        session["instructions"] = "ユーザーが入力した文章を、付け足さずに日本語でそのまま読み上げてください。"

    pcm = bytearray()
    async with client.realtime.connect(model=REALTIME_MODEL) as connection:
        await connection.session.update(session=session)
        await connection.conversation.item.create(item={
            "type": "message", "role": "user", "content": [content],
        })
        await connection.response.create()

        async for event in connection:
            if event.type == "error":
                raise SystemExit(f"Realtime API のエラー: {event.error.message}")
            if event.type == "response.output_audio.delta":
                pcm.extend(base64.b64decode(event.delta))
            if event.type != "response.done":
                continue
            if event.response.status != "completed":
                raise SystemExit(f"Realtime API の応答が完了しませんでした（{event.response.status}）。")
            tool_calls = [item for item in event.response.output or [] if item.type == "function_call"]
            if not tool_calls:
                break
            for call in tool_calls:
                try:
                    arguments = json.loads(call.arguments)
                except json.JSONDecodeError:
                    arguments = None
                equipment_id = arguments.get("equipment_id") if isinstance(arguments, dict) else None
                if call.name == "lookup_equipment" and equipment_id in ("A", "B"):
                    result = {"equipment_id": equipment_id, "status": EQUIPMENT_STATUS[equipment_id]}
                else:
                    result = {"error": "設備 A または B を指定してください。"}
                print(f"{call.name} -> {result}")
                await connection.conversation.item.create(item={
                    "type": "function_call_output", "call_id": call.call_id,
                    "output": json.dumps(result, ensure_ascii=False),
                })
            await connection.response.create()

    if not pcm:
        raise SystemExit("音声応答が返りませんでした。")
    return pcm


async def save_realtime_audio(api_key, content, output_path):
    async with AsyncOpenAI(api_key=api_key) as client:
        try:
            pcm = await asyncio.wait_for(realtime_audio(client, content), timeout=90)
        except asyncio.TimeoutError:
            raise SystemExit("90 秒以内に Realtime API の応答が完了しませんでした。") from None
    with wave.open(str(output_path), "wb") as recording:
        recording.setparams((1, 2, PCM_RATE, 0, "NONE", "not compressed"))
        recording.writeframes(pcm)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenAI の音声 API を試す")
    commands = parser.add_subparsers(dest="command", required=True)
    asr = commands.add_parser("asr", help="ASR（文字起こし）")
    asr.add_argument("audio", type=Path)
    tts = commands.add_parser("tts", help="TTS（読み上げ）")
    tts.add_argument("text")
    tts.add_argument("--output", type=Path, default=Path("openai-tts.wav"))
    dialogue = commands.add_parser("dialogue", help="録音で設備を照会する")
    dialogue.add_argument("audio", type=Path)
    dialogue.add_argument("--output", type=Path, default=Path("openai-dialogue.wav"))
    args = parser.parse_args()

    settings = dotenv_values(Path(__file__).with_name(".env"))
    api_key = settings.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        parser.error(".env の OPENAI_API_KEY に API キーを設定してください。")
    if api_key.startswith("sk-ant-"):
        parser.error("OPENAI_API_KEY に Anthropic 用のキーが設定されています。OpenAI Platform の API キーを設定してください。")

    try:
        if args.command == "asr":
            with OpenAI(api_key=api_key, timeout=90) as client:
                transcribe(client, args.audio)
        else:
            content = {"type": "input_text", "text": args.text} if args.command == "tts" else {
                "type": "input_audio", "audio": base64.b64encode(read_pcm(args.audio)).decode("ascii"),
            }
            asyncio.run(save_realtime_audio(api_key, content, args.output))
    except AuthenticationError:
        raise SystemExit("OpenAI API の認証に失敗しました。OPENAI_API_KEY を確認してください。") from None
    except ConnectionClosedError as error:
        if error.rcvd and "invalid_api_key" in error.rcvd.reason:
            raise SystemExit("OpenAI Realtime API の認証に失敗しました。OPENAI_API_KEY を確認してください。") from None
        raise
