# 🎬 Video Subtitle Tool

 Whisper 视频字幕工具 — 自动从视频提取语音、转录为字幕文件，并通过 AI 纠错提升准确率。

## 功能

- 📼 **音视频提取**：使用 ffmpeg 从任意格式视频提取音频
- 🎯 **Whisper Medium 转录**：高精度中文语音识别（比 base 模型准确率提升约 30%）
- 🤖 **AI 纠错**：自动修正 Whisper 识别错字
- 🎞️ **字幕烧录**：将字幕直接嵌入视频输出

## 环境要求

| 工具 | 版本 | 说明 |
|------|------|------|
| Python | **3.11** | 必须使用 3.11，不支持 3.13 |
| ffmpeg | 最新 | 音频/视频处理 |
| Whisper | medium | 中文字幕转录 |

## 快速开始

### 1. 安装依赖

```bash
# Python 3.11（必须）
# 从 https://www.python.org/downloads/ 安装 Python 3.11

# 安装 Whisper 及依赖（使用清华镜像源）
pip install openai-whisper torch numpy tqdm -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 转录视频

```bash
# Step 1: 提取音频
ffmpeg -i your_video.mp4 -vn -acodec pcm_s16le audio.wav

# Step 2: Whisper Medium 转录
py -3.11 -c "
import whisper
model = whisper.load_model('medium')
result = model.transcribe('audio.wav', language='zh', task='transcribe')

def fmt(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int((t % 1) * 1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'

with open('subtitle.srt', 'w', encoding='utf-8') as f:
    for i, seg in enumerate(result['segments'], 1):
        f.write(f'{i}\n{fmt(seg[\"start\"])} --> {fmt(seg[\"end\"])}\n{seg[\"text\"].strip()}\n\n')
"

# Step 3: AI 纠错（将 SRT 文件内容复制给 LLM 纠错）

# Step 4: 烧录字幕进视频
ffmpeg -i your_video.mp4 -vf "subtitles=subtitle.srt:charenc='utf-8':force_style='FontSize=24,PrimaryColour=&HFFFFFF,Outline=2'" -c:a copy output_with_subtitles.mp4
```

## 项目文件说明

```
video-subtitle-tool/
├── README.md              # 本文件
├── SKILL.md               # OpenClaw Agent Skill 定义（完整工作流）
├── scripts/
│   ├── whisper_transcribe.py   # Whisper Medium 转录脚本
│   └── merge_srt.py           # SRT 合并/修正脚本
└── requirements.txt        # Python 依赖
```

## 工作流程

```
视频文件.mp4
    ↓ [ffmpeg 提取音频]
音频.wav
    ↓ [Whisper Medium 转录]
字幕.srt（原始）
    ↓ [AI 纠错]
字幕_纠错.srt
    ↓ [ffmpeg 烧录]
带字幕视频.mp4
```

## 常见问题

**Q: 提示 `ModuleNotFoundError: No module named 'whisper'`**
A: 使用 Python 3.11 运行：`py -3.11`，不要用系统默认的 Python

**Q: medium 模型加载崩溃**
A: 确保使用 Python 3.11，Python 3.13 与 PyTorch 不兼容

**Q: ffmpeg 处理中文路径报错**
A: 视频路径避免中文，或复制到英文路径下处理

## License

MIT
