# 批量转换参考约定（repo-conversion）

本文件是 plugin-builder 批量转换（`convert_plugin_repo.py`）的**查表型参考**：输入 URL 形态、
ref 规则、manifest 方言识别、索引条目扩展形态、索引冲突策略、转换内部机制、market 名规则。
**出错时兜底查阅，无需每次通读**；流程与红线见 SKILL.md §5.2。

## 链接形态约定（输入规则）

**支持的形态**：

- 仓库根 `https://github.com/<o>/<r>`（容忍 `.git` 后缀、尾斜杠、query/fragment、`http://`、`git@` 形式）；`github.com/<o>/<r>` 缺协议写法和 `<o>/<r>` 简写自动补全（简写只在不是本地目录时生效），补全结果记入转换报告。
- **通用 git 托管**：`gitee.com` 与 GitHub 结构同构，支持仓库根 / tree / blob 全形态；其他 git 托管（`cnb.cool`、`atomgit.com`、`gitlab.com` 等）支持仓库根地址（`https://<host>/<o>/<r>[.git]` 或 `git@<host>:<o>/<r>`，git clone 拉取，无 codeload 回退、tree/blob 子路径与 commit SHA 拉取不支持）。
- `.../tree/<ref>`：按该 ref 拉取整仓后自动识别（同仓库根）。
- `.../tree/<ref>/<path>`：只转换该子目录这一个插件。
- `.../blob/<ref>/<文件>`（`blame` 同构按 blob 处理）：把该文件作为严格入口——索引文件（`plugins.json`/`marketplace.json`）按索引展开（相对路径以 marketplace 根为基准：`.claude-plugin/`、`.agents/plugins/` 的上级目录，其他位置按文件所在目录；找不到回退仓库根）；manifest 文件只转换所在插件；不再扫描仓库其他配置。
- 本地目录路径（**不能与实际产物目录相同或互相包含**）。产物默认在 `<share>/plugin-sources/`，复用 `KIMI_SHARE_DIR` 等现有 share 解析规则；可用 `--output-dir` 显式指定其他目录。源目录与产物互不包含时，可以在源仓库中以 `.` 为输入。旧源码不自动迁移。

**ref 规则**：tree/blob URL 里指定的 ref **严格按它拉取**——ref 不存在（或分支名含 `/` 导致 URL 无法区分分支名与路径边界）时明确报错并提示改用 commit SHA 或不带 `/` 的标签链接，**绝不静默回退默认分支**（悄悄换 ref 会转出与用户页面所见不一致的内容）。未指定 ref 时按 default → main → master → HEAD 探测。

**明确拒绝并给改写提示**：仓库内非代码页面（`/pull`、`/issues`、`/releases`、`/commit/<sha>`、`/wiki`、`/actions` 等）；`raw.githubusercontent.com` 与 `/raw`、`/archive` 链接（提示等价的 blob/tree 写法）；`gist.github.com`；非 GitHub 系托管的多级路径与 tree/blob 子路径（提示用仓库根地址或 clone 到本地）。这些形态不再静默当整仓处理。

**错误呈现**：致命错误（无法识别来源、ref 不存在、tree 目录不存在、仓库无插件）统一输出一句干净的「错误: …」，退出码非零，不抛 traceback。

**网络**：github.com 直连不通时自动改走 codeload tarball，无需配置；其他托管只有 git clone 一条路。

## 并行与命名

市场产物目录 `<output-dir>/<market>/` 默认必须不存在（空目录也不复用）；转换先原子创建它，再写源码和报告。已有目录时停止，旧源码、转换/登记报告及 `marketplace.orig` 均保留。要保留多批产物，用不同的 `--output-dir`；仅在用户明确确认覆盖后传 `--force`，此时沿用整盘重建同名插件及覆盖报告的行为，手工修改会丢失。不同默认转换不能同时占用同一产物目录；不要并行强制覆盖同一目录。

索引条目回源拉取与逐插件转换/校验/依赖检查都按 `--jobs N` 并行（默认 8，`--jobs 1` 退回串行）；报告顺序与索引条目顺序一致，同一仓库的并发拉取自动串行复用。并行下同名插件谁拿原名、谁拿 `-2` 后缀由线程调度决定，不再保证索引顺序靠前者赢（产物内容不受影响）。

## manifest 识别与方言选择

**manifest 识别（按优先级，Codex 只是方言之一）**：`kimi.plugin.json`（本项目格式，轻转换只校正必需字段）→ `.kimi-plugin/plugin.json`（本项目格式点目录形式，轻转换）→ `.codex-plugin/plugin.json`（Codex 方言）→ `.claude-plugin/plugin.json`（Claude 方言）→ `.codebuddy-plugin/plugin.json`（CodeBuddy 方言，格式近 Claude 按 simple 转换）→ `gemini-extension.json`（Gemini 扩展方言：`${extensionPath}` 按插件根占位符改写、`${/}` 路径分隔符改写为 `/`，`contextFileName` 映射为 systemPromptPath）→ `server.json`（MCP 官方 registry 方言：packages 的 npm/pypi 条目转 npx/uvx stdio server，remotes 转 url 型 server，包成仅 mcpServers 的插件）→ 根部 `plugin.json`（通用，含 interface 按 Codex 方言处理）。

**多平台方言选择**：同一插件目录存在多个平台定义（kimi/codex/claude/codebuddy/gemini/serverjson）时，按识别优先级（`MANIFEST_CANDIDATES` 顺序：kimi > codex > claude > codebuddy > gemini > serverjson）自动选第一个方言转换，被跳过的方言逐条记进转换报告 notes（可见、可回溯，不打断批量转换）。单一平台时直接用。

## 索引条目扩展形态

`source` 为裸来源标签且条目带 HTTP(S) `url` 时，使用该 URL，不把标签当成本地目录；`./`、`../`、含路径分隔符等明确路径仍按原路径规则处理。同时提供 URL 又希望使用单段本地目录名时，写成 `./目录名` 或显式 local source 对象。`source: "url" / "git-subdir" / "github"` 与对应对象形式共用远端解析，保留子目录和 sha/ref。

① 官方 Claude marketplace 外部源 `{"source": "url", "url": <repo>, "sha"/"ref": ...}` 按钉住的提交拉取（40 位 SHA 跳过 clone 直接走 codeload tarball）；② git-subdir 源 `{"source": "git-subdir", "url": <repo>, "path": <仓库内子目录>}` 拉仓库后取该子目录为插件目录；③ 技能集合条目 `{"source": "./", "skills": ["./skills/x", ...]}`（如 anthropics/skills）按数组把技能目录组装成 skill-only 插件，同 source 的多条目不合并、各自出插件；④ 条目 path 失效但仓库内能按条目名唯一匹配插件 manifest 时同名回退（典型：索引指向 ./plugins/<name> 而插件实际在仓库根部），名字对不上不猜、按失败记；⑤ `--limit N` 在索引展开阶段就截断（按**索引条目数**只解析前 N 个：指向同一插件的别名条目也占名额，与「转换出 N 个插件」不是同一口径）——外部 url 条目每个都要回源拉取，若只在转换阶段截断，`--limit 2` 也会先 clone 几百个仓库；⑥ DeepSeek `registry-snapshot.json` 索引（根部或任意子目录，如 data/）：条目 url 回源拉取，description 多语言对象按 zh 优先拍平；cordis 判定规则——回源后有可识别 manifest 或根部 SKILL.md/skills/ 的声明式子集可转，纯代码型 cordis 包（仅 package.json/cordis.patch.yml）明确记失败原因。

## 索引冲突策略

根部 plugins.json 与 marketplace.json 等多个索引候选并存时不静默——打印候选清单与冲突警告，按优先级 `plugins.json` > `.agents/plugins/marketplace.json` > `.claude-plugin/marketplace.json` 选用，并在 plugin-builder-report.md 里记录选了谁、忽略了谁。

## 转换内部机制（转换要点）

来源 manifest → 根目录 kimi.plugin.json；**来源 manifest 里的相对路径按两种口径依次解析**（真实仓库里两种写法都存在）：① 相对 manifest 所在目录（如 `.codex-plugin/plugin.json` 写 `../skills/` 指插件根的 `skills/`、`.cursor-plugin/plugin.json` 写 `./hooks/hooks.json` 指 `.cursor-plugin/hooks/hooks.json`），② 相对插件根（如 `.codex-plugin/plugin.json` 写 `./skills/` 指插件根 `skills/`）；命中后统一重写为插件根相对的 `./` 路径；mcpServers/hooks 的路径引用（./.mcp.json、./hooks/hooks.json）读文件内联；Claude 风格 hooks.json 拍平成 Kimi `[{event, command, timeout?}]`（不支持的 event 丢弃记报告）；`${PLUGIN_ROOT}`/`__REPO_ROOT__` 占位符改写为 `./` 相对路径；interface.category 自由文本映射到 Kimi 枚举；SKILL.md/agents .md 缺 frontmatter 自动补；插件本体整目录复制（排除 .git/.github/来源 manifest 目录/node_modules）。**manifest 声明了 skills/commands/agents 但内容在源目录缺失（镜像/源仓库不完整）时，字段被丢弃并记 `dropped_components`，该插件判为依赖不可用、不随批量流程自动登记**——宁可暂缓也不登记空心插件。

产物 manifest 严格遵循 kimi.plugin.json 字段规范（权威：agent-core plugin/manifest.ts + zod schema + 线上 schema + 市场登记门禁；规范外字段一律丢弃记报告，不透传）。每个插件转换后先跑 validate_plugin.py（结构 0 error），再跑 check_plugin_deps.py（依赖可用性：MCP 命令/包/URL、hooks 引用脚本、SKILL.md 引用的 MCP server 是否存在可装；`--offline` 可跳过 registry/URL 联网核实），两关都过才算「真正可用」。

## market 名与安装路径背景

**market 的确定顺序**（与输入入口无关，git URL 与本地目录同一规则）：`--market` 参数 > 源索引配置顶层 name 字段（根部 plugins.json / marketplace.json，含子目录发现的 marketplace.json；blob 链接指向索引文件时按该文件的 name；归一化为合法市场名）> personal——不能从源解析到 market 才回退 personal；单插件输入（tree 子路径 / blob manifest / 无索引仓库）源里本来没有索引，回退 personal 是预期行为。市场名规则：小写字母或数字开头，仅含小写字母/数字/下划线/连字符。

**标准安装路径 = 市场登记路径**：转换产物的标准安装方式是 `register_personal.sh` 登记 → 客户端「个人」页签点 ＋ 安装（daimon 侧无 mcpServers 限制，带不带 MCP 都能装），可用性判定也以这条路径为准。背景说明：客户端另有「从文件安装」（本地侧载，plugin-local-loader.ts），它拒绝带 mcpServers 的插件（mcp-not-supported）——那只是侧载自身的限制，不影响本转换产物的可用性结论；纯 skills/agents/commands/hooks 插件想侧载也可以。图标走插件根目录的 icon 文件约定（市场按 `icon.png|jpg|jpeg|svg|webp` 首个匹配读取；侧载读顶层 `icon` 字段，产物按 runtime 规范不写，侧载时回退首字占位）。
