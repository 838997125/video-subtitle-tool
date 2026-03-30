# 🎬 本地模型视频字幕工具

使用本地 AI 模型为视频自动生成并烧录字幕——无需上传、无需 API、全程离线。

## 核心能力

**上传任意视频 → 输出带字幕的视频**

```
原视频.mp4  ──[本地 Whisper]──  字幕.srt  ──[ffmpeg]──  带字幕视频.mp4
                    ↑
              完全本地运行，不依赖云服务
```

- 🎯 **高精度**：Whisper Medium 模型，比传统 ASR 准确率更高
- 🔒 **隐私安全**：所有处理在本地完成，视频不上传
- 🤖 **AI 纠错**：自动修正识别错字
- ⚡ **全自动化**：一条命令完成提取 → 转录 → 纠错 → 烧录

## 效果示例

| 场景 | 原版 | 加字幕后 |
|------|------|----------|
| 课程视频 | 无字幕 | 实时字幕 |
| 产品 Demo | 无字幕 | 方便传播 |
| 演讲/分享 | 无字幕 | 便于回顾 |
| IPD 手册 | 无字幕 | 专业呈现 |

## 环境要求

| 工具 | 要求 |
|------|------|
| Python | **3.11**（必须，不支持 3.13）|
| ffmpeg | 已安装并加入 PATH |
| Whisper 模型 | medium（约 1.4GB，首次自动下载）|

## 快速开始

### 安装依赖

```bash
# Python 3.11
# https://www.python.org/downloads/

# 安装 Whisper（使用清华镜像）
pip install openai-whisper torch -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 一键生成字幕视频

```bash
# Step 1: 提取音频
ffmpeg -i your_video.mp4 -vn -acodec pcm_s16le audio.wav

# Step 2: 转录为 SRT
py -3.11 -c "
import whisper
model = whisper.load_model('medium')
result = model.transcribe('audio.wav', language='zh', task='transcribe')

def fmt(t):
    h,m,s = int(t//3600), int(t%3600//60), int(t%60)
    ms = int((t%1)*1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'

with open('subtitle.srt','w',encoding='utf-8') as f:
    for i,seg in enumerate(result['segments'],1):
        f.write(f'{i}\n{fmt(seg[\"start\"])} --> {fmt(seg[\"end\"])}\n{seg[\"text\"].strip()}\n\n')
"

# Step 3: AI 纠错（复制 subtitle.srt 内容给 AI 模型修正错字）

# Step 4: 烧录字幕进视频
ffmpeg -i your_video.mp4 -vf "subtitles=subtitle.srt:charenc='utf-8':force_style='FontSize=24,PrimaryColour=&HFFFFFF,Outline=2'" -c:a copy output.mp4
```

## 项目结构

```
video-subtitle-tool/
├── README.md                   # 本文件
├── SKILL.md                    # OpenClaw Agent Skill（完整工作流定义）
├── scripts/
│   ├── whisper_transcribe.py   # Whisper Medium 转录脚本
│   └── merge_srt.py           # SRT 合并工具（处理长视频分段转录）
└── requirements.txt            # Python 依赖
```

## 工作流程详解

```
1. 提取音频
   ffmpeg -i video.mp4 audio.wav

2. 本地转录（Whisper Medium）
   py -3.11 scripts/whisper_transcribe.py --audio audio.wav --output subtitle.srt

3. AI 纠错
   将 subtitle.srt 丢给 AI 模型，输出修正版

4. 烧录字幕
   ffmpeg -i video.mp4 -vf "subtitles=subtitle_fixed.srt:..." output_subtitled.mp4
```

## 常见问题

**Q: 报错 `No module named 'whisper'`**
A: 确保使用 Python 3.11 运行：`py -3.11`，不是系统默认的 Python 3.13

**Q: medium 模型加载崩溃**
A: Python 3.13 与 PyTorch 不兼容，本项目必须使用 Python 3.11

**Q: ffmpeg 处理中文路径报错**
A: 视频路径避免中文，或复制到英文路径下处理

**Q: 视频时长较长（如 1 小时以上）**
A: Whisper 转录速度约为视频原速的 1/9（CPU），长视频建议分段处理；可用 `scripts/merge_srt.py` 合并多段字幕

## License

MIT
