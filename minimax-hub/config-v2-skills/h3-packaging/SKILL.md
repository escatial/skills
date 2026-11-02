---
name: h3-packaging
description: |
  用于生成复古潮流拼贴、炫酷 MV、特效 MV、说唱 rap、fashion 动作相关的 15 秒音乐短片完整提示词，并通过 Hub video agent 逐字派单；用户要做这类高能视觉音乐片、拼贴感 MV 或说唱视觉 prompt 时使用。默认 16:9、15 秒、中文执行说明和 English-only 屏幕动态文字；只补问缺失的人物来源与音乐内容。内置 fashion 人物动作库，要求 5–7 个动作族、空间借力、服装动作、静动冲突和至少 4 个连贯空间区段，避免反复扭身、冲近或摸镜头。原创歌曲未指定曲风时默认采用 K-pop hip-hop / K-hip-hop / trap-rap performance。完整提示词保持 5200–6800 字符、8–10 个逐镜 Shot 及 Layer A/B/C 动态字体；video agent 只能传输同一字符串，禁止摘要、缩写、翻译或二次改写。
allowed-tools: [question, task, hub_audio_analyze_music, hub_audio_meta, hub_canvas_get_node, hub_get_asset_relations]
---

# Retro Street Collage Audiovisual

只执行“复古潮流拼贴”路线：地下音乐录像带、独立时尚杂志、zine/复印印刷、海报墙、大字报排版与高时装真人摄影。默认使用 **MiniMax-H3 / Hailuo H3、16:9、15 秒**。最终提示词以中文为主，只有画面中真实可见的字体文案使用英文。

最终只建立一个视频生成任务。音乐、歌曲、人声、歌词、音效和画面默认由 H3 在同一视频中同步生成；除非用户明确要求独立音频文件，否则禁止另派音乐 Agent。

## 最高优先级：Hub 适配与逐字派单协议

本节是不可删除、不可概括的执行协议。任何安装转换、Hub 适配或 Skill 重写都必须完整保留本节；不得把它改写成“向 video agent 提交一个创意摘要”。

1. **编排 Agent 负责完整提示词工程**：先在当前上下文中生成唯一变量 `final_h3_prompt`，目标 5700–6500 字符，硬范围 5200–6800 字符。它必须包含七个中文结构段、Music Prompt、原创歌曲的 5–7 行实际歌词或 BGM 声明、Shot 1 至 Shot 8–10、逐镜 Typography/Layer A/B/C、Rhythm/Cut 和全局负面约束。
2. **先展示，再派单**：把 `final_h3_prompt` 完整显示给用户；显示代码块内部的每个字符就是最终送给 H3 的字符串。不得另做“派单版”“精简版”或英文翻译版。
3. **只走 Hub 原生 video agent**：本 Skill 已经是 Hub 原生 Skill，不调用编排层的直接视频生成工具，避免安装时被再次自动适配或重写。编排器必须通过 `task` 把完整 `final_h3_prompt` 交给 video agent；video agent 只是传输和执行者，不是第二位创意作者。

```text
Task type: generation
model: MiniMax-H3
Aspect ratio: 16:9
Duration: 15s
Prompt handling: VERBATIM COPY ONLY. Do not summarize, shorten, translate, rewrite, reorder, polish, or add text.
Copy only the characters between the two markers into hub_generate_video.prompt. Do not include the markers.

VERBATIM_H3_PROMPT_START
<完整 final_h3_prompt，5200–6800 字符>
VERBATIM_H3_PROMPT_END
```

4. **禁止摘要派单**：只给 video agent 角色、风格、歌词和一串动作的短摘要属于失败；少于 5200 字符、没有七个结构段、没有至少 8 个 `Shot`、没有逐镜 Layer A/B/C 的文本不得派单。
5. **字符串锁定**：外层 task metadata、marker 和 `Original request` 不属于 H3 prompt。H3 实际 prompt 只能是代码块中已展示、marker 之间完全相同的 `final_h3_prompt`。

Hub 安装器不得再次把本 Skill 识别成第三方直接生成流程；如果运行环境仍需改变 `task` 的外层调用名称，只允许改变调用名称，不得改变完整提示词的作者、内容、结构、长度和逐字复制要求。

开始工作前，按需读取：

- 音乐与声线：`references/music.md`
- 印刷拼贴方法：`references/methods.md`
- 字体骨架和层叠：`references/typography.md`
- 视觉坐标与参考边界：`references/style-guide.md`
- 人物动作与空间调度：`references/performance-and-space.md`（每个有人物的项目必须完整读取）
- 最终格式与压缩预算：`references/prompt-blueprint.md`

## 0. 两道前置门

每个新项目先读用户消息、真实附件和已有选择，只判断 `character_gate` 与 `music_gate`。两道门没有通过前，不得写完整提示词，不得调用 `hub_generate_video`。

### Character gate

以下任一条件成立即通过：

- 用户已上传含明确主角的人物参考图；
- 用户已明确选择 AI 原创人物；
- 用户已给出足够完整的人物文字设定；
- 项目明确不需要人物。

若未通过，只问一题：

**人物来源**

- `上传人物参考（推荐）`：等待用户上传真实图片；
- `AI 原创人物`：按本风格自动写先锋时尚人物、服装与气质。

不得自动替用户选择 AI 原创人物。图片中若人物一目了然，直接作为人物参考，不重复询问；只有多张人物图导致主角身份确实无法判断时，才只问“哪张是主角”。没有场景图或字体图不构成阻塞，由 Skill 自行设计。

### Music gate

以下任一条件成立即通过：

- 用户已上传音乐/音频；
- 用户已提供歌词并明确要歌曲；
- 用户已明确选择原创歌曲、纯器乐 BGM 或无音乐；
- 用户已在描述中明确曲风与人声/器乐形态。

若未通过，只问一题：

**音乐内容**

- `原创歌曲（推荐）`：H3 随视频同步生成编曲、人声和完整 15 秒微型歌曲；未指定曲风时默认 K-pop hip-hop / trap-rap performance；
- `纯器乐 BGM`：H3 随视频生成配乐，无人声、无歌词；
- `上传参考音乐`：等待用户上传音频，再按真实节拍设计。

卡片中不要使用含混的“原创 Hook”作为选项名。用户选择“原创歌曲”或直接说“原创音乐”后，自动完成短歌词、声线、编曲和节拍映射，不再确认 Hook、歌词或屏幕词。用户选择上传时必须等待真实文件，不能虚构音频信息。

### 卡片合并规则

人物与音乐都缺失时，在同一张 `question` 卡片中放上述两题；只缺一项时只问一题。不得询问画幅、时长、风格、屏幕文字、英文词库或“大字白名单”。默认回显为：

`MiniMax-H3｜16:9｜15s｜复古潮流拼贴｜屏幕文字 English only`

## 1. 素材、歌词与声音

### 真实素材绑定

- 人物参考：只锁定身份、脸、发型、年龄感、服装轮廓、比例、肤质与气质。
- 场景参考：只借空间、构图、光线、环境层次、色彩与材质。
- 字体参考：只借字形骨架、尺度对比、字距、材质、排版和运动机制。
- 音频参考：先用 `hub_audio_meta` / `hub_audio_analyze_music` 读取真实 BPM、重拍、段落和人声，不再生成第二条音乐。

只有真实附件存在时才写文件路径。不要虚构 `@图片1`、`image.png` 或节点 id。参考图中的品牌、Logo、标题和可识别文字都不得复刻。

### 原创歌曲

每次原创歌曲都必须完整读取并执行 `references/music.md`。用户未指定曲风时，默认采用 **K-pop hip-hop / K-hip-hop / trap-rap performance track**，不要再自动写成偏氛围的 dark-pop。用户明确指定其他曲风时服从用户，但仍要有连续 vocal、段落对比、记忆性 Hook 和完整结尾。

默认按 128 BPM、4/4、8 小节组织：Intro tag → 两小节 Rap A → Pre-hook lift → 两小节 melodic/chant Hook → Beat switch/response → Final Hook tag。Music Prompt 必须写清鼓组、3–4 音 808 走向、4–6 音问答 motif、声线、主音色、flow/cadence、押韵、vocal layering、0–15 秒结构和最终收束。

原创 rap/K-pop hip-hop 写 **5–7 行实际歌词**：至少两条语义连续的 rap lyric、一个 pre-hook、两句 Hook、可选 response/ad-lib 和 final tag。Rap A1/A2 各约 8–12 个可听音节，至少一组内押、一组尾押，并从 straight-sixteenth 切到 syncopated 或 triplet cadence；Hook 每句约 3–6 个音节，使用主句/回应句和明确落音。歌词多于屏幕词，画面仍只提取 3–6 个英文关键词，不把完整歌词做字幕。

声线跟随人物参考：明显男性主角用 male / masculine timbre，明显女性主角用 female / feminine timbre，多人按角色分配，无法判断时才用 neutral timbre。Rap 主轨靠前且干，押韵词可 double；Hook 才增加低八度、和声或短 ad-lib。禁止孤立口号式假 rap、单音旋律、全程同一鼓型、持续单根音 808、无关风格突变、性别错配和没有结尾的循环。

### 纯器乐 BGM

明确写：`instrumental only, no vocals, no lyrics`。仍需写 BPM、拍号、低频根音、一个可辨认的 4–6 音问答旋律动机、鼓组层次、段落能量、一次中段变化和最终落点，不得只写“氛围音乐”。BGM 也要遵循“建立 → 展开 → 抽空 → 回归 → 收束”，不能从头到尾同一层循环。

### English-only 屏幕词

- 有歌词：从歌词、片名和情节中自动提取或忠实翻译 3–6 个英文短词/短句。
- 无歌词：根据人物、地点、动作冲突与结尾自动创作 3–6 个英文词；不得复用案例固定词。
- 只把实际英文文案写进各镜头 `Typography`，不要在最终提示词中出现 `TEXT WHITELIST`、`approved words`、白名单元数据或向用户确认词库。
- 不生成随机小字、伪品牌、乱码或与剧情无关的口号。

## 2. 固定视觉语法

### 影像与剪辑

- 视觉母体：地下录像带 + 独立时尚杂志 + 复印 zine + 街头海报；真人皮肤和服装真实，不做廉价霓虹赛博风。
- 色盘：油墨黑、纸白、警示红为默认，可随参考替换一个专色；全片控制在 2–4 色。
- 材质：粗颗粒、gate weave、胶片闪烁、复印灰尘、半色调、印刷毛边、套印错位、扫描偏移、撕纸、跳帧残影、单帧过曝；效果必须有恢复点。
- 15 秒使用 **8–10 个主镜头**，按音乐的 8 小节结构组织；每镜内部可含 1–2 次节拍级动作或图层变化。每个镜头要有独立的空间、景别、人物动作或版式任务，不靠重复形容词拉长提示词。只用硬切、跳切、鼓点切、遮挡切、闪白硬切、文字压屏切和字腔穿越。
- 镜头节奏按“建立 → 第一次冲击 → 变化/抽空 → 回归 → 终止”分组，不把 15 秒写成从头到尾同一种高潮。至少一个镜头负责音乐开场，至少一个镜头负责中段转折，至少一个镜头负责最终收束。
- 至少 4 个连贯但视觉可辨的空间区段，至少 3 次明显景别变化，至少 2 个设计主导镜头。相邻镜头不得同时保持相同景别、空间和文字深度。

### 人物张力与静动冲突

每个有人物的项目必须完整读取并执行 `references/performance-and-space.md`。先根据角色身份、服装、音乐和环境设计一条可完成的 15 秒表演弧线，再写逐镜 Prompt；不得从案例里机械抄动作。

8–10 镜选择 5–7 个不同动作族，至少包含 3 个大幅度动作、2 个空间借力动作、1 个服装动作和 2 个承上启下的静点。每镜按“进入路径 → 起势/重心 → 发力 → 空间或服装接触 → 惯性/落点 → 镜头反馈”写成动作链。相邻镜头必须改变动作族，并在身体轴线、运动方向、空间支点、镜头关系中再改变至少两项。手掌伸向或触摸镜头全片最多一次，不能把“扭身、冲近、伸手”换词后反复使用。

空间不是背景贴图：15 秒至少选择 4 个属于同一视觉世界、但有纵深/横向/高低/遮挡差异的空间区段，让人物进入、穿越、借力、换位或离开。动作强弱按“启动 → 爆发 → 冻结/呼吸 → 再爆发 → 明确落点”组织，不能只靠字体和故障效果制造节奏。

### TYPE LAYER STACK

每个文字镜头只有一个语义主词，但同一词至少呈现三层：

- Layer A — HERO BASE：超大完整主字，清晰可读 0.1–0.3 秒；
- Layer B — PRINT PLATE：同词的复印、网点、套印或扫描残影；
- Layer C — ACTION / FOREGROUND：同词或其字符片段沿手势、人物轮廓、镜头轨迹或消失点运动；
- Layer D — OCCLUSION / RECOVERY（可选）：撕纸、字腔、黑场或遮挡后恢复完整字形。

主字默认 ultra-black condensed grotesk 或 heavy newspaper/slab display，ALL CAPS，700–900 weight，紧字距、矩形字腔；辅字最多一个窄体 neutral sans、monospaced technical 或少量 marker accent。每镜写清准确英文、字族骨架、宽度/重量、大小层级、材质、颜色、前中后景、版式、透视/消失点、遮挡、进入、可读时刻、变形和退出。文字必须与人物和场景产生真实遮挡、视差和空间关系，不能只贴一层平面字幕。

至少轮换四种版式：越界压屏、纵排/横压缩、人物前后穿插、非规则分栏、负空间孤字、遮罩挖空、跨缝连接、反射/墙面透视、纯文字黑场。每个项目从 `references/methods.md` 选择 4–6 种真正落到镜头，不在开头空列理论名词。

### 节拍映射

- hi-hat roll：字边微震、跳帧、字符快速重组；
- snare：文字猛然放大/套印归位、肩膀下压、闪白硬切；
- 808 bass hit：画面低频压迫、字形纵拉/横压、广角动作落点；
- vocal keyword：准确嘴型、下颌、呼吸、眼神、手势与主字进入；
- 段落变化：切场景、景别、版式或印刷方法。

## 3. 最终提示词与长度硬门

最终只生成一个不可变字符串 `final_h3_prompt`。**自然语言说明和段落标题必须以中文为主；只有准确屏幕词、实际歌词、必要的曲风/字体术语可以是英文。禁止输出整篇英文提示词。**

不要把 `FINAL_VIDEO_PROMPT_START/END` 发送给模型；它们只能作为聊天界面外部边界。展示给用户的代码块内容就是 `hub_generate_video.prompt`，逐字复制，不翻译、不摘要、不重排。

### 字符预算

- 硬范围：**5200–6800 个字符**，含汉字、英文、路径、标点、空格和换行；低于 5200 视为被摘要，不得派单。
- 安全目标：5700–6500 字符；禁止超过 6800，也不要为了“丰富”重复句子。
- 项目/参考/创意：≤650 字符；音乐/歌词/表演：≤1300；风格/字体系统：≤1050；8–10 个镜头合计≤3200；全局与负面：≤550。
- 单镜目标 270–350 字符；不要在每镜重复全局材质、字体总规则和角色一致性。增加丰富度时，优先增加具体的动作起点、镜头反馈、字体层运动和音乐节点，而不是增加抽象形容词。
- 草稿超预算时必须在展示和派单前压缩：先删重复形容词与重复全局规则，再合并相邻镜头说明；保留真实参考、音乐/歌词、准确英文词、人物动作、TYPE LAYER STACK、节拍、角色一致性和负面约束。
- 若无法可靠完成字符计数，将镜头固定为 8 个并把目标压到 5600 字符以内。任何已知或疑似超过 6800 的文本都不得派单。
若无法可靠完成字符计数，将镜头固定为 8 个并把目标压到 5600 字符以内。任何已知或疑似超过 6800 的文本都不得派单。

### 固定结构

```text
【项目设置】
MiniMax-H3，15 秒，16:9，复古潮流拼贴音乐短片，音乐与画面同步生成。

【参考素材说明】
[真实路径与限定用途；没有的维度写“AI 原创”，不写虚构文件。]

【核心创意】
[1–3 句。]

【音乐、歌词与表演】
Music Prompt：[曲风、BPM、拍号、groove、鼓组、808 走向、4–6 音问答 motif、声线或 instrumental only、rap flow/cadence、vocal layering、0–15 秒结构。]
Vocal / lyric：[原创 rap/K-pop hip-hop 按 Rap A1、Rap A2、Pre-hook、Hook 1、Hook 2、可选 Response/ad-lib、Final tag 写 5–7 行实际歌词；BGM 写 no vocals, no lyrics。]
人物表演：[按动作库选出的表演弧线、动作族与空间路线；大动作、空间借力、服装动作、静点、嘴型/呼吸与节拍关系。]

【视觉与动态字体系统】
[色盘、成像、主/辅字体、四种以上版式、TYPE LAYER STACK、前中后景/透视/遮挡、4–6 种已落镜方法、剪辑规则。]

【画面过程描述】
Shot 1 — [时间]｜[景别/镜头]｜[空间]
场景与人物：动作族：[本镜动作族]；空间区段：[本镜区段]；[进入路径→重心与发力→空间/服装接触→惯性与落点→镜头反馈。]
Typography: "[EXACT ENGLISH TEXT]"；[字骨架/大小/材质/颜色]；Layer A/B/C（可选 D）的前中后景、透视、遮挡与可读时刻。
Layer A — HERO BASE：[完整主字的尺度、材质、位置和可读时刻。]
Layer B — PRINT PLATE：[同词套印/网点/复印残影的偏移、深度和恢复点。]
Layer C — ACTION / FOREGROUND：[同词/字符碎片沿人物或镜头轨迹进入，被谁遮挡，如何退出。]
Rhythm / Cut：[vocal/snare/hi-hat/808 触发]；[硬切方式]。

[继续到 Shot 8–10；至少两镜由版式而不是人物动作主导，并明确开场、变化和最终收束。]

【全局要求与负面约束】
[角色一致、真实肤质、英文文字准确、快切和静动冲突；禁止换脸换装、普通字幕、单层贴字、乱码、Logo、柔和转场、廉价效果。]
```

## 4. Hub video agent 逐字派单锁定

只有两道前置门均通过且 `final_h3_prompt` 通过语言、结构与长度检查后，才能派单。

调用 `task` 时，必须使用“最高优先级：Hub 适配与逐字派单协议”中的 `VERBATIM_H3_PROMPT` 模板，把完整 `final_h3_prompt` 嵌入任务。不得只发送 brief、shot summary、style summary 或 task description 后让 video agent 自己重写 prompt。video agent 的唯一合法动作是把 marker 之间的字符串原样放入 `hub_generate_video.prompt`。

调用前最后检查：

1. Character gate 与 Music gate 已通过；
2. 提示词中文说明为主，所有屏幕可见字是准确英文；
3. 原创 rap/K-pop hip-hop 含 5–7 行实际歌词、连续 Rap A1/A2、pre-hook、Hook、cadence 变化、beat switch，且声线匹配人物；BGM 明确无人声；
4. 8–10 镜、至少 2 个设计主导镜头；人物使用 5–7 个不同动作族，含 3 个大动作、2 个空间借力、1 个服装动作、2 个静点和至少 4 个连贯空间区段；
5. 音乐有 4–6 音问答 motif、Hook 主句/回应句、rap 内押/尾押、一次 flow 或编曲变化和明确结尾，而不是口号或无主题循环；
6. 多数文字镜头含 Layer A/B/C，且不是单层字幕；
7. `final_h3_prompt` 在 5200–6800 字符内，且包含七个完整结构段和至少 8 个 Shot；
8. 展示字符串、`VERBATIM_H3_PROMPT` 内字符串与 `hub_generate_video.prompt` 字符级一致；
9. 没有把完整 prompt 压缩成一段角色/风格/歌词/动作摘要。

任一项失败：先自动修正；不要把失败草稿展示或派单。
