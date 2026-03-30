"""
Whisper Medium 转录脚本
用法: py -3.11 scripts/whisper_transcribe.py --audio "audio.wav" --output "subtitle.srt"
"""
import whisper
import argparse
import os

def fmt_timestamp(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int((t % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def transcribe(audio_path, output_path, language="zh"):
    print(f"Loading Whisper medium model...")
    model = whisper.load_model("medium")
    print(f"Transcribing: {audio_path}")

    result = model.transcribe(audio_path, language=language, task="transcribe")
    segments = result.get("segments", [])
    print(f"Transcription complete. {len(segments)} segments.")

    with open(output_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            f.write(f"{i}\n")
            f.write(f"{fmt_timestamp(seg['start'])} --> {fmt_timestamp(seg['end'])}\n")
            f.write(f"{seg['text'].strip()}\n\n")

    print(f"Saved to: {output_path}")
    return len(segments)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Whisper Medium 转录工具")
    parser.add_argument("--audio", required=True, help="音频文件路径")
    parser.add_argument("--output", required=True, help="输出 SRT 路径")
    parser.add_argument("--lang", default="zh", help="语言代码，默认中文")
    args = parser.parse_args()

    if not os.path.exists(args.audio):
        print(f"Error: Audio file not found: {args.audio}")
        exit(1)

    transcribe(args.audio, args.output, args.lang)
