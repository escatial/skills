#!/bin/bash
# Thesis current-state section: Markdown → Word
# 用法：./gen_docx.sh <input.md> [output.docx]
#
# 依赖：pandoc（系统已自带）
# 输出：A4、1.5 倍行距、首行缩进 2 字符、宋体 + Times New Roman

set -e

INPUT="$1"
OUTPUT="${2:-${INPUT%.md}.docx}"

if [ -z "$INPUT" ]; then
    echo "用法: $0 <input.md> [output.docx]"
    exit 1
fi

if [ ! -f "$INPUT" ]; then
    echo "文件不存在: $INPUT"
    exit 1
fi

# 生成带样式的 docx
# --reference-doc 可选：传入自定义 reference.docx 用学校/期刊模板
pandoc "$INPUT" \
    -o "$OUTPUT" \
    --from markdown+raw_attribute \
    --to docx \
    --toc \
    --toc-depth=3 \
    --reference-doc="${REFERENCE_DOC:-}"

echo "OK: $OUTPUT"
