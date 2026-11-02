---
name: voice-clone
description: |
  音色克隆助手。从参考音频样本中克隆音色，返回 voice_id
  供后续通过 audios_generation 进行 TTS 生成。
  内置法律合规确认（强制）、音频时长预处理（自动循环/裁切）、
  降噪与音量归一化、语言检测与试听生成、克隆后元数据收集。
  触发短语：voice clone、clone voice、音色克隆、声音克隆、复刻音色、复刻声音。
trigger-words: [voice clone, clone voice, 音色克隆, 声音克隆, 克隆音色, 克隆声音, 复刻音色, 复刻声音]
allowed-tools: [hub_audio_meta, read, hub_audios_generation, hub_ffmpeg]
allowed-tools-speech: hub_voice_prepare
guide-prompt: 请提供一段参考音频文件(mp3/m4a/wav, 建议10秒-5分钟纯人声)
guide-prompt-en: 请提供一段参考音频文件（mp3/m4a/wav，建议 10 秒-5 分钟纯人声）
---

# 音色克隆

从参考音频中克隆音色，返回 `voice_id` 供 `audios_generation` 使用。

**语言规则**：始终使用用户使用的语言与其交互。如果用户说中文，用中文回复。如果用户说英文，用英文回复。

## 步骤 1：法律合规确认

在任何音频处理之前，你**必须**要求用户确认法律免责声明。如果未确认则终止流程。

根据用户语言使用以下确切文本。**不要转述或概括。**

**中文（用户说中文时）：**
```
question: "音色克隆需要您确认以下声明，请确认后继续:"
options:
  - label: "确认并继续"
    description: "我确认并保证: 1）我拥有该音频的合法使用权并已获得音频中说话人的授权，从而有权继续进行音色克隆操作；2）克隆生成的结果仅用于合法用途"
  - label: "取消"
    description: "我不确定是否有授权，取消操作"
```

**英文（用户说英文时）：**
```
question: "Voice cloning requires you to confirm the following statement before proceeding:"
options:
  - label: "Confirm and continue"
    description: "I confirm and guarantee: 1) I have the legal right to use this audio and have obtained authorization from the speaker, thereby having the right to proceed with voice cloning; 2) The cloned results will only be used for lawful purposes"
  - label: "Cancel"
    description: "I am not sure if I have authorization, cancel the operation"
```

用户选择「取消」或回复表示不确认 --> 立即终止并解释原因。

**不可跳过**，即使用户催促加快速度。

## 步骤 2：音频元数据检查

调用 `audio_meta` 获取参考音频的时长和格式。

检查项：
- 格式：必须是 mp3/m4a/wav；其他格式需先用 ffmpeg 转换
- 大小：不得超过 20MB
- 时长：判断是否需要预处理（步骤 3）

## 步骤 3：音频时长预处理

| 条件 | 操作 |
|------|------|
| < 10s | 用 ffmpeg 循环音频直到 >= 10s。如 4s 音频循环 3 次 = 12s。命令：`ffmpeg -stream_loop 2 -i input.wav -c copy output.wav` |
| 10s - 5min | 无需处理，直接使用 |
| > 5min | 用 ffmpeg `silencedetect` 找到 5 分钟前的最后一个静音点，在该静音起始处裁切。如果 5 分钟内未检测到静音，在 4 分 55 秒处硬切并添加淡出 |

**> 5min 裁切流程：**

```bash
# 1. 检测静音（阈值 -30dB，最小时长 0.5s）
ffmpeg -i input.wav -af silencedetect=noise=-30dB:d=0.5 -f null - 2>&1 | grep silence_start

# 2. 找到 300s（5分钟）之前的最后一个 silence_start
# 3. 在该点裁切
ffmpeg -i input.wav -t <silence_start> -c copy output.wav
```

如果 5 分钟内未检测到静音：
```bash
# 在 295s 处开始淡出，持续 5s，总时长 300s
ffmpeg -i input.wav -t 300 -af "afade=t=out:st=295:d=5" output.wav
```

## 步骤 4：降噪与音量归一化

分别询问用户是否需要降噪和音量归一化：

```
question: "参考音频需要降噪处理吗？"
options:
  - label: "不需要降噪"
    description: "音频是干净的人声，没有背景噪音"
  - label: "需要降噪"
    description: "音频有噪音、背景音乐或其他干扰"
```

```
question: "需要音量归一化吗？"
options:
  - label: "不需要"
    description: "音频音量正常"
  - label: "需要归一化"
    description: "音频太大声或太小声，自动调整到合适水平"
```

根据用户选择设置参数：
```
need_noise_reduction: <根据用户选择>
need_volume_normalization: <根据用户选择>
```

## 步骤 5：语言检测与试听文本

### 5a. 语言检测

调用 `read` 分析参考音频的语言：

```
file_path: <audio_path>
question: "Identify the language spoken in this audio. Choose the best match from: Chinese, Cantonese, English, Arabic, Russian, Spanish, French, Portuguese, German, Turkish, Dutch, Ukrainian, Vietnamese, Indonesian, Japanese, Italian, Korean, Thai, Polish, Romanian, Greek, Czech, Finnish, Hindi, Bulgarian, Danish, Hebrew, Malay, Persian, Slovak, Swedish, Croatian, Filipino, Hungarian, Norwegian, Slovenian, Catalan, Nynorsk, Tamil, Afrikaans. Reply with the language name only."
```

与用户确认检测到的语言：

```
question: "检测到的语言：<detected_language>。请确认："
options:
  - label: "<detected_language>"
    description: "语言检测正确"
  - label: "不正确"
    description: "检测有误——请在下方文本框中输入正确的语言"
```

### 5b. 试听文本

从 `references/demo-texts.json` 中查找确认语言对应的默认试听文本（key = 语言名称）。

与用户确认试听文本：

```
question: "克隆完成后将生成一段试听音频。请选择试听文本："
options:
  - label: "使用默认试听文本"
    description: "<显示该语言在 demo-texts.json 中条目的前 20 个字符>..."
  - label: "自定义试听文本"
    description: "在下方文本框中输入你自己的文本（最多 200 字符）"
```

如果试听文本语言与参考音频语言不同，警告用户可能影响试听质量。

## 步骤 6：执行克隆

调用 `voice_clone`：

```
audio_path: <processed_audio_path>
need_noise_reduction: <步骤 4>
need_volume_normalization: <步骤 4>
demo_text: <步骤 5 确认的试听文本>
demo_model: "speech-2.8-hd"
```

### 敏感内容检查

如果 `input_sensitive_type` 非零：
- 通知用户参考音频被标记为风险内容（类型含义：1=严重违规，2=涉黄，3=广告，4=违禁，5=辱骂，6=恐怖主义，7=其他）
- 询问用户是否继续使用克隆的音色

## 步骤 7：克隆后元数据收集

克隆成功后，收集音色元数据：

```
question: "克隆成功！请为这个音色命名："
options:
  - label: "使用默认名称"
    description: "自动命名为'克隆音色 <日期>'"
  - label: "自定义名称"
    description: "在下方文本框中输入你的音色名称"
```

名称确认后，收集可选信息：

```
question: "是否添加音色元数据？（可选，随时可以跳过）"
options:
  - label: "跳过，完成克隆"
    description: "不需要额外信息"
  - label: "添加元数据"
    description: "添加性别、语言、音色描述标签"
```

用户选择「添加元数据」--> 收集：
- 性别：男 / 女 / 其他
- 语言：使用步骤 5 检测到的语言作为默认值
- 音色描述：自由文本，如「温暖低沉的男声」

## 步骤 8：返回结果

向用户呈现完整的克隆结果：

```
## 音色克隆完成

- **音色名称**：<voice_name>
- **Voice ID**：`<voice_id>`
- **语言**：<language>
<如有性别> - **性别**：<gender>
<如有描述> - **描述**：<description>

### 试听
<如有试听音频> ![试听](<demo_audio_url>)

### 使用方法
- 将 `voice_id` 传递给 `audios_generation` 的 `voice_id` 参数即可使用此音色
```

## 步骤 9：保存到记忆（可选）

呈现结果后，询问用户是否保存此音色以供未来使用：

```
question: "需要记录这个音色吗？记录后在任何项目中都可以通过名称直接调用。"
options:
  - label: "记录音色"
    description: "保存 voice_id，后续可通过音色名称直接使用"
  - label: "不用了"
    description: "仅本次使用，不记录"
```

用户选择「记录音色」-->

使用 `memory_write`，参数如下：
- **scope**：`user`
- **name**：`voice-<voice_name>`（kebab-case，如音色名称为「2」→ `voice-2`，音色名称为「Alice」→ `voice-alice`）
- **type**：`reference`
- **description**：克隆音色「<voice_name>」的 voice_id，来源文件 <source_audio_filename>
- **body**：
```markdown
# 音色：<voice_name>

- **Voice ID**：`<voice_id>`
- **来源音频**：`<source_audio_path>`
- **语言**：<language>
<如有性别> - **性别**：<gender>
<如有描述> - **描述**：<description>
- **克隆日期**：<date>

当用户提到「<voice_name>」时，使用此 voice_id 进行语音生成。
```

用户选择「不用了」--> 跳过，结束流程。

## 反面模式

- **不要跳过法律确认**——步骤 1 是强制的，即使用户说「快点」
- **不要将 > 5 分钟的音频直接传给 voice_clone**——API 会拒绝，必须先裁切
- **不要将 < 10 秒的音频直接传给 voice_clone**——API 会拒绝或产出低质量结果，必须先循环
- **不要在同一任务中重复克隆同一段音频**——voice_id 可在会话内复用
