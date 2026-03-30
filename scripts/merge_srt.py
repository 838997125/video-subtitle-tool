"""
SRT 合并/修正工具
用法: py -3.11 scripts/merge_srt.py --part1 "base.srt" --part2 "medium.srt" --offset 530 --output "merged.srt"
用于合并两个 SRT 文件（如前半段 base 模型+后半段 medium 模型）
offset 为 part2 的时间偏移秒数
"""
import argparse
import os

def fmt_timestamp(total_seconds):
    h = int(total_seconds // 3600)
    m = int((total_seconds % 3600) // 60)
    s = int(total_seconds % 60)
    ms = int((total_seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def parse_timestamp(ts_str):
    """Parse 'HH:MM:SS,mmm' or 'HH:MM:SS.mmm' -> total seconds"""
    ts_str = ts_str.strip().replace(',', '.')
    h, m, s = ts_str.split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)

def read_srt(path):
    """Read SRT file, return list of (index, ts_line, text)"""
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.split('\n')
    entries = []
    i = 0
    while i < len(lines):
        if lines[i].strip().isdigit():
            idx = lines[i].strip()
            i += 1
            if i < len(lines) and '-->' in lines[i]:
                ts_line = lines[i].strip()
                i += 1
                text_lines = []
                while i < len(lines) and lines[i].strip() != '':
                    text_lines.append(lines[i].rstrip())
                    i += 1
                entries.append((idx, ts_line, '\n'.join(text_lines)))
        i += 1
    return entries

def merge_srt(part1_path, part2_path, offset_seconds, output_path, cutoff_ts=None):
    """
    Merge two SRT files: part1 first, then part2 with offset applied.
    If cutoff_ts is set, entries at or after this timestamp in part1 are replaced by part2.
    """
    part1_entries = read_srt(part1_path)
    part2_entries = read_srt(part2_path)

    # Build output from part1, cutting at cutoff_ts
    output = []
    cutoff_idx = None
    if cutoff_ts:
        for i, (idx, ts_line, text) in enumerate(part1_entries):
            ts_start = parse_timestamp(ts_line.split('-->')[0])
            if ts_start >= cutoff_ts:
                cutoff_idx = i
                break

    if cutoff_idx is not None:
        output = []
        for i in range(cutoff_idx):
            idx, ts_line, text = part1_entries[i]
            output.append(idx)
            output.append(ts_line)
            output.append(text)
            output.append('')
    else:
        for idx, ts_line, text in part1_entries:
            output.append(idx)
            output.append(ts_line)
            output.append(text)
            output.append('')

    # Append part2 with offset
    for orig_idx, ts_line, text in part2_entries:
        ts_parts = ts_line.split('-->')
        start = parse_timestamp(ts_parts[0]) + offset_seconds
        end = parse_timestamp(ts_parts[1]) + offset_seconds
        new_ts = f"{fmt_timestamp(start)} --> {fmt_timestamp(end)}"
        output.append(orig_idx)
        output.append(new_ts)
        output.append(text)
        output.append('')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    print(f"Merged: {len(part1_entries)} + {len(part2_entries)} entries -> {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SRT 合并工具")
    parser.add_argument("--part1", required=True, help="前半段 SRT 文件")
    parser.add_argument("--part2", required=True, help="后半段 SRT 文件")
    parser.add_argument("--offset", type=float, required=True, help="后半段时间偏移秒数")
    parser.add_argument("--output", required=True, help="输出 SRT 路径")
    parser.add_argument("--cutoff", type=float, default=None, help="截断时间点（秒），part1 在此之后的条目被替换")
    args = parser.parse_args()

    merge_srt(args.part1, args.part2, args.offset, args.output, args.cutoff)
