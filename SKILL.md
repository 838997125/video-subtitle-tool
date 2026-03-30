# 视频字幕自动化 - Whisper + Python 3.11 Medium 模型

通过 Whisper medium 模型将视频语音转文字（高精度），最后烧录字幕进视频。

## ⚠️ Python 版本要求

**必须使用 Python 3.11**，不能使用系统默认的 Python 3.13。

| Python | 用途 | 可用 |
|--------|------|------|
| Python 3.13（系统默认）| whisper CLI | ❌ medium 模型崩溃 |
| **Python 3.11** | Python API + whisper | ✅ 正常 |

**调用方式**：始终使用 `py -3.11` 前缀，不使用裸 `whisper` 命令。

---

## 工作流程

### Step 1：提取音频
```bash
ffmpeg -i "视频路径.mp4" -vn -acodec pcm_s16le "音频路径.wav"
```

**注意**：Windows 路径含中文时，输出路径用英文避免参数解析错误。

### Step 2：Whisper Medium 转录（SRT 格式）
```bash
py -3.11 -c "
import whisper

model = whisper.load_model('medium')
result = model.transcribe('音频路径.wav', language='zh', task='transcribe')

def fmt(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int((t % 1) * 1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'

with open('输出字幕.srt', 'w', encoding='utf-8') as f:
    for i, seg in enumerate(result['segments'], 1):
        f.write(f'{i}\n{fmt(seg[\"start\"])} --> {fmt(seg[\"end\"])}\n{seg[\"text\"].strip()}\n\n')
"
```

**参数说明**：
- `medium`：比 base 模型精度高约 30%，适合正式内容
- `language='zh'`：指定中文，否则默认自动检测
- 输出文件：`音频路径.srt`

**Medium 模型下载**（首次自动下载，约 1.42GB）

### Step 3：AI 纠错
用 LLM 对 SRT 文件进行错字修正。

**操作方式**：通过 subagent 读取 SRT 文件，输出纠错后的 SRT 文件。

**prompt**：
```
Read the file [SRT路径]，这是 Whisper medium 模型的语音识别字幕文件，可能存在少量识别错误。

请对每条字幕进行纠错：
- 修正识别错误的字词（如"混烂"→"混乱"，"耗产"→"产品"，"网细"→"往西"）
- 修正标点符号
- 保持原意不变，不添加或删除内容
- 保持相同的时间戳
- 保持 SRT 格式（序号 + 时间轴行 + 字幕文本 + 空行）
- 序号保持连续

输出完整的纠错后 SRT 文件到：[纠错后SRT路径]
```

**示例常见错误**：
| 纠错前 | 纠错后 |
|--------|--------|
| 耗产 | 产品 |
| 混烂 | 混乱 |
| 网细 | 往西 |
| 打胜账 | 打胜仗 |
| 交响月团 | 交响乐团 |
| 一脱再脱 | 一拖再拖 |
| 甩锅 | 甩锅 ✅（保留）|

### Step 4：烧录字幕进视频
```bash
ffmpeg -i "原视频.mp4" -vf "subtitles=filename='纠错后SRT路径':charenc='utf-8':force_style='FontSize=24,PrimaryColour=&HFFFFFF,Outline=2'" -c:a copy "输出视频.mp4"
```

**参数说明**：
- `-c:a copy`：保留原音频，不重新编码
- `force_style`：白色字体（PrimaryColour=&HFFFFFF），黑色描边（Outline=2），字号 24
- SRT 路径中反斜杠需双写

---

## Python 3.11 环境说明

### 安装位置
```
C:\Program Files\Python311\python.exe
```

### 已有依赖（pip install -i https://pypi.tuna.tsinghua.edu.cn/simple）
- torch 2.11.0+cpu（PyTorch CPU 版）
- openai-whisper 20250625
- numpy, tqdm, numba, tiktoken, regex, requests 等

### 如果依赖缺失
```bash
py -3.11 -m pip install openai-whisper tqdm numpy -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 常见错误
| 错误 | 原因 | 解决 |
|------|------|------|
| `ModuleNotFoundError: No module named 'whisper'` | 用了 Python 3.13 | 改用 `py -3.11` |
| medium 模型加载崩溃 | Python 3.13 不兼容 PyTorch | 必须用 `py -3.11` |
| ffmpeg 中文路径报错 | PowerShell 参数解析 | 输出路径用英文 |

---

## 快速执行脚本

已预置在项目 `scripts/` 目录下：

- `scripts/whisper_transcribe.py` — Whisper Medium 转录脚本
- `scripts/merge_srt.py` — SRT 合并工具

执行：
```bash
py -3.11 scripts/whisper_transcribe.py --audio "音频路径.wav" --output "输出字幕.srt"
```
