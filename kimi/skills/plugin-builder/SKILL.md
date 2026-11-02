---
name: plugin-builder
description: 把想法 / 文件 / GitHub 仓库变成 Kimi 插件，脚手架+校验后登记进个人市场（daimon-share，缺省 personal 市场），用户在插件页「个人」页签点 ＋ 一键安装、免重启。自带脚本（scripts/）+ 官方登记 CLI（kimi-daimon kimi-plugin register-personal）+ cachebuster，全程本地无 token。描述创建尽量自动填字段，只在真推不出（如 MCP URL、图标）时问用户。触发：做个 Kimi 插件 / 把仓库包成插件 / 加进我的插件市场 / 改插件名·改描述·更新插件 / plugin builder / 把网页·网站做成技能或插件 / 给个网址生成技能 / web to skill。
---

# Kimi 插件构建（自带脚本版）

把 **想法 / 上传文件 / GitHub 仓库** 变成 Kimi 插件，脚手架 + 本地校验后**登记进个人市场**（注册表在 `~/Library/Application Support/kimi-desktop/daimon-share` 下的 `daimon/plugin-market/<market>/<id>.json`，缺省市场为 `personal`），用户在插件页**「个人」页签**点 ＋ 安装，**daemon 侧热更活跃会话，无需重启**。

> **实现载体**：本技能 = **SKILL.md + 自带脚本**（`scripts/*.py`），本地全流程**完全不依赖外部 catalog CLI**；登记动作走 Kimi 桌面版客户端官方 CLI `kimi-daimon kimi-plugin register-personal`。运行环境：有终端 / shell 的 agent（如 Kimi Code）+ 已安装 Kimi 桌面版客户端。**全程本地、无需 token。**
> **描述创建**：能从描述推出的字段都自己填（可用脚本 flag 传，或建完直接编辑 kimi.plugin.json），只有 **MCP server URL、找不到的图标** 这类私有信息才问用户；**绝不留 TODO / 假 URL / 失效图标**。

## 自带脚本（你的"手"）

| 脚本 | 作用 |
|---|---|
| `scripts/create_plugin.py <name> [flags]` | 脚手架 kimi.plugin.json + skills/（产物默认在 `<share>/plugin-sources/<market>/<name>/`，`--market` 缺省 personal）；`--with-register` 一步登记。**只用于新建** |
| `scripts/update_plugin.py <dir> [flags]` | **改已有插件的元数据（首选）**：displayName/描述/图标等，改字段+升 `+local` 版本+重登记一步完成；非 personal 市场的插件须传 `--market <market>` |
| `scripts/validate_plugin.py <dir>` | 本地校验（必填/semver/组件路径/图标/TODO） |
| `scripts/register_personal.sh <dir>` | **bash 登记（首选）**：把任意插件目录登记进个人市场（走官方 CLI `kimi-daimon kimi-plugin register-personal`），`--market <market>` 指定市场（缺省按产物路径 `plugin-sources/<market>/<name>/`（也兼容旧 `plugins/` 根） 的市场段推断，推断不到回退 personal），自动转绝对路径，登记完即可在「个人」页签看到；输出本即 JSON，`--json` 可传可不传（任何位置都接受并忽略） |
| `scripts/register_personal.py <dir>` | 同上，python 版实现；与 bash 版二选一即可 |
| `scripts/register_converted.py <market_dir>` | **批量登记（convert 产物的标准登记路径）**：读 `conversion-report.json` 的 `registration_plan`，逐个登记 registerable 桶（CLI JSON 的 `ok` 字段判成败、收集 `link`、失败重试一次不中断整批），hooks/setup.sh/依赖不可用/校验 error 自动分流跳过；结束与注册表对账（排除 marketplace.orig）并写 `registration-report.json`（机器交付）、整体重写 `plugin-builder-report.md` 把「登记结果」段落填实，打印可直接转述给用户的总结数字；`--also name1,name2` 把暂缓桶里用户已审阅的插件一并登记 |
| `scripts/cachebuster.py <dir>` | 只升 `+local.时间戳` 版本号（改了 SKILL.md 正文/脚本源码后用；改元数据用 update_plugin.py） |
| `scripts/convert_plugin_repo.py <github-url-or-dir>` | **批量转换（不做登记）**：把一个插件/技能仓库（任意来源：kimi.plugin.json / .codex-plugin / .claude-plugin / 根部 plugin.json 均可识别）批量转成本项目插件（kimi.plugin.json），自动识别单插件仓库 / 多插件 monorepo / 索引仓库（plugins.json 条目支持 url 或仓库内相对路径 path）；产物与报告按市场默认落在 `<share>/plugin-sources/<market>/`（market：`--market` > 本地目录索引配置顶层 name > personal），逐个跑 validate + 依赖检查后出转换报告 |
| `scripts/check_plugin_deps.py <插件目录或父目录>` | **依赖可用性检查**：对照本项目运行时内置工具集，核实 MCP server 的命令/npm 包/PyPI 包/URL、hooks 引用脚本、SKILL.md 引用的 MCP server 是否真实存在可装，判「真正可用/不可用」 |

## 0. 前置

- 本地流程只需 **bash / python3 / git / curl**（脚本自足，不用 catalog CLI）。
- 脚本都**用解释器调**：`python3 scripts/xxx.py …` 或 `bash scripts/xxx.sh …`。

## 1. 认输入（四种入口）

- **A. 描述** → 进 §2 自动填。
- **B. 上传文件**（SKILL.md / 脚本 / manifest）→ 以它为基础。
- **C. GitHub 仓库** → `git clone --depth 1 <url> /tmp/<repo>`，读 README/package.json 判断包法（CLI+skills → skill-only；有 MCP → 配 MCP；纯脚本 → 写 SKILL.md 指导调用）。**若仓库本身是插件/技能集合（带 marketplace.json / plugins.json 索引或多插件 monorepo），或用户给的是 tree/blob 子路径链接、想批量转换导入，直接走 §5.2 的 convert_plugin_repo.py**——支持/拒绝的 URL 形态与 ref 规则见 `references/repo-conversion.md`「链接形态约定」，不符合约定的输入按那里的提示引导用户改写，不要自行拼接或猜测 URL。
- **D. 网页 URL**（把某个网站变成技能/插件）→ 进 §3 网页模式。

## 2. 从描述自填 + 只问私有信息

- **自动填**：name(kebab) / displayName / 描述 / keywords / category / skillInstructions / SKILL.md 正文。
- **判 hosted/local**：remote MCP URL → hosted；stdio/本地依赖 → local。
- **只问**：MCP-backed 缺 server → 问 MCP server URL / stdio 命令 + 是否 OAuth；icon 找不到 → 问用户（也可不设，客户端用默认图标兜底）；写/删操作 → 提醒并写"用前确认"（登记直接进行，不在此列）。

## 3. 网页模式（Web → Skill：把网站变成技能）

用户发一个网址，要「把这个网站做成技能/插件」。目标产物：一个 skill-only 插件，让 agent 以后能用内置浏览器（InAppBrowser 工具）在这个网站上快速取数/操作。**典型场景：用户有某网站账号，但网站没有公开 API / MCP。**

> 前置：本模式依赖 `InAppBrowser` 工具（daimon bundle ≥ 0.5.51 的内置浏览器控制面，action 语义见内置 skill `in-app-browser`）。当前会话没有该工具时，明确告诉用户需要升级客户端/内核，**不要**退回 curl / loopback HTTP 等旁路。

### 第一步：分析网站（agent 当"侦探"）

1. `navigate` 打开用户给的 URL（`newTab: true`），保留 `tabId`。
2. **登录态**：页面要求登录时，请用户在内置浏览器里登录一次，然后用 `wait` / `snapshot` 轮询确认登录完成再继续。**绝不向用户索要 cookie / token / 密码。**
3. `snapshot` / `read_page` 读页面结构，找到核心功能入口（搜索框、列表、详情页）。
4. `network start` 开始抓包 → 用 `click` / `fill` / `send_keys` 亲手操作一遍核心功能（如发起一次真实检索）→ `network stop` + `network list` + `network detail` 逐个读 XHR/fetch 请求，反推内部接口契约：URL、方法、参数、鉴权方式（cookie 会话还是 token）、响应 JSON 结构。
5. `evaluate` 验证假设：在页面上下文里试调一次推断出的接口，确认返回结构（页面内 fetch 自动携带登录 cookie）。

### 第二步：路线决策（三选一，按优先级）

| 路线 | 适用 | 说明 |
|---|---|---|
| **A. 注入式 JS（主力）** | 站点有可调用的内部 JSON 接口 | 生成的脚本在页面上下文执行（`evaluate`），fetch 内部 API，自动带登录态。单次查询 1~2 次工具调用 |
| **B. DOM 工作流（兜底）** | 接口加密/签名/抓不到，只能走界面 | SKILL.md 写清操作序列（navigate → fill → click → snapshot/read_page 取结果），脆但能用 |
| **C. 独立 CLI 直连（禁止）** | — | 需要导出 cookie/token 鉴权：HttpOnly cookie 导不出，存凭证有安全风险。**不做，也不生成** |

### 第三步：生成插件

1. `create_plugin.py` 建 skill-only 脚手架（name 用站点名 kebab，如 `hn-search`）。
2. 路线 A：把注入脚本写到 `skills/<name>/scripts/<name>.js`（以 `scripts/web_inject_template.js` 为模板）：自包含 async 函数、入参（查询词等）由 agent 运行时填入、内部 API 地址与参数写死、**返回紧凑 JSON**（只留有用字段，控制体积）。
3. 写 `skills/<name>/SKILL.md`：
   - frontmatter `description` 写清触发场景（站点名 + 典型需求，如「搜 Hacker News / 查 HN 帖子」）；
   - 正文写运行时流程：`list_tabs` / `find_tab` 找站点标签页（没有就 `navigate` 打开）→ 确认已登录（未登录提示用户登录并 `wait` 轮询）→ 读取本 skill 的 `scripts/<name>.js`，把用户参数填入后调 `InAppBrowser` 的 `evaluate` 注入执行 → 把返回的 JSON 整理给用户；
   - 写清限制：脚本 15 秒超时、结果要紧凑、大结果集分页；接口失效时回退路线 B 或提示重新生成。
4. `validate_plugin.py` 校验 → `register_personal.sh` 登记（同 §4/§5）。

### 性能规则（生成物必须内建，血泪教训）

慢的根源不是浏览器，是「步骤太多 × 每步 LLM 往返」和「脚本挂起等平台超时」。生成的 skill 必须遵守：

- **循环 N 次的页面操作，一律改成一次注入、页面内并发取数**：脚本内用 `Promise.all` / 限流并发（模板里有 `mapLimit`）批量抓 N 个条目，一次 `evaluate` 拿完。N 个条目绝不允许生成「逐条 `navigate` + `read_page`」的 SKILL.md 流程——那是 N×2 次工具调用、N×2 轮 LLM 往返。
- **脚本自带超时**：每个 fetch 用 `AbortController` 设 ≤8 秒主动中止、失败快速返回错误，绝不允许挂起等平台 15 秒超时兜底。
- **只回紧凑字段**：列表/详情都在页面内提取关键字段后返回，详情正文按 `maxChars` 截断；禁止引导 agent 用 `read_page` 把全文读进上下文（上下文膨胀会让后续每步 LLM 越来越慢）。
- **分层交付**：SKILL.md 的流程设计为「先一次注入给列表」，逐条核验/深度分析等重活作为用户可选的第二步，不默认全做。

### 红线（网页模式追加）

- **不导出、不存储任何凭证**：cookie / token / 密码一律不进生成物；注入脚本依赖「内置浏览器里已登录」这一运行前提。
- **不编造接口**：内部 API 的 URL/参数/响应结构必须来自真实抓包（`network detail`）或 `evaluate` 验证，禁止凭印象写。
- **浏览器动作串行**：同会话的 InAppBrowser action 严格串行，生成的脚本/SKILL.md 不假设并行操作。

## 4. 脚手架 + 填 + 校验

```bash
python3 scripts/create_plugin.py "<产品名>" \
  --type skill-only \                # 或 mcp / mcp+skills
  --display-name "<展示名>" --description "<简介>" \
  --category PRODUCTIVITY [--icon-url <已验证图>] [--mcp-url <MCP URL>]
```
- 生成到 **`<share>/plugin-sources/<market>/<name>/`**（`<share>` 复用登记时的 share 解析，优先 `KIMI_SHARE_DIR`；create 的 `--share-dir` 同时覆盖默认源码根与登记根；`--path` 可显式覆盖源码根；`--market` 指定市场，缺省 personal）：`<market>/<name>/kimi.plugin.json` + `skills/<name>/SKILL.md`（合法默认）。
- 图标：`--icon-url <url>` 会下载成插件根目录的 `icon.<ext>`（个人市场按插件根目录的 `icon.png|jpg|jpeg|svg|webp` 首个匹配读取，≤ 256 KiB）；manifest 里的 `interface.iconUrl` 也会保留（客户端插件页对本地插件仍用它）。没有合适图标就留空，**不要编造 URL**。
- **按需追加组件 flag**（每个都会写进 manifest 并生成对应 stub 文件，装上即生效）：
  - `--with-agents`：子代理角色 → `agents` 字段 + `agents/<name>.md`（frontmatter name/description + 角色行为正文）。
  - `--with-commands`：用户可触发的斜杠命令 → `commands` 字段 + `commands/<name>.md`（正文写 `$ARGUMENTS` 会被用户参数替换；不写则参数以 `ARGUMENTS: ...` 追加在末尾）。
  - `--with-session-start`：每个会话开始时自动加载插件自带 skill 的提醒 → `sessionStart.skill`（type 不含 skills 时自动升级为 mcp+skills）。
  - `--with-system-prompt`：注入每个会话系统提示的行为约定 → `systemPromptPath` + `system-prompt.md`（保持精简，上限 32 KB）。
  - `--with-hooks`：会话事件时自动执行的命令 → `hooks` 字段 + `hooks/session-start.sh`（SessionStart 示例）。**hooks 会随插件在会话事件发生时自动执行，登记后哪些插件带 hooks 会写进 plugin-builder-report.md 供用户查阅；validate 对任何 hooks 声明都会输出 WARN 提醒。**
  - 全组件一次生成示例：
    ```bash
    python3 scripts/create_plugin.py "<产品名>" --type mcp+skills \
      --with-agents --with-commands --with-session-start --with-system-prompt --with-hooks \
      --description "<简介>" --mcp-url <MCP URL>
    ```
- **把没用 flag 传的真实字段直接编辑进 kimi.plugin.json / SKILL.md，清掉所有 TODO。**
```bash
python3 scripts/validate_plugin.py <插件目录>     # 修完所有 ERROR
```

## 5. 登记进个人市场（★核心）

```bash
bash scripts/register_personal.sh <插件目录>                # 登记到 personal 市场（缺省）
bash scripts/register_personal.sh --market <market> <插件目录>  # 登记到指定市场
# 或等价的 python 版：python3 scripts/register_personal.py [--market <market>] <插件目录>
```

→ 调用客户端官方 CLI `kimi-daimon kimi-plugin register-personal <dir> --share-dir <daimon-share> [--market <market>] --json`：CLI 完成 realpath/树扫描/manifest 校验（version 必填），把条目写进 `<share>/daimon/plugin-market/<market>/<id>.json`（registeredBy "cli"，市场缺省为 `personal`）。**脚本不要直接读写注册表文件。登记只做校验+登记，从不安装。** 登记成功的 JSON 输出为 `{"ok": true, "link": ..., ...}`（失败 `{"ok": false, "error": ...}` 且非零退出）——批量循环用 `ok` 字段判定成败，不要 grep 文本。
→ **脚本自身的行为约定**：`register_personal.sh` 会把插件目录转成绝对路径再交给 CLI（相对路径直接可用）；stdout 保持纯 JSON（CLI 诊断日志走 stderr），批量循环可直接解析。选项（`--skip-validate` / `--market`）必须放在插件目录**之前**；`--json` 例外——任何位置都接受并忽略（脚本固定以 `--json` 调 CLI，输出本即 JSON，不需要传）。成功输出会带上条目实际落盘路径（`条目：<share>/daimon/plugin-market/<market>/<id>.json`），写错位置一眼可见。
→ **市场名（--market）**：解析顺序为 **--market 显式 > 产物路径（`plugin-sources/<market>/<name>/` 或旧 `plugins/<market>/<name>/` 的市场段）> personal**——create/convert 的产物自带市场段，登记时不用传；只有要登记到与路径不符的市场时才显式传。**personal 与各命名市场都是个人市场**——只对本人（本机账号）生效，登记后插件统一出现在「个人」页签。**非 personal 市场的插件安装后 id 变为 `<id>@<market>`**（与 personal 里同名插件可同时安装），且该市场的注册表目录会持有 `marketplace.orig`（**源市场全量插件清单**，无 `.json` 后缀、不与插件条目冲突；语义见 §5.2「产物」），由 convert 在产物目录生成一次、登记时原样复制过去。
→ `register_personal.sh` 是通用模板：kimi-daimon 路径取自 `DAIMON_RUNTIME_BINARY_PATH` 环境变量（客户端启动 daemon 时注入，跨平台，runtime 环境必然存在）、share 目录解析（`KIMI_SHARE_DIR` 环境变量 > macOS 默认 > 非 macOS 回退 `~/.kimi`）都已内置，**只需把 `<插件目录>` 填成当前要登记的插件路径**（必须含 `kimi.plugin.json`）；share 目录仅在非标准安装时才用第二参数覆盖。
→ 登记后插件立刻出现在插件页**「个人」页签**（状态：未安装）。**引导用户到「个人」页签点 ＋ 安装**——daemon 侧安装会热更活跃会话，**当前会话即可用，无需重启客户端**。
→ **含 setup.sh / hooks 的插件先不登记**：登记前按 conversion-report.json 的 `registration_plan` 分流（`hold_hooks_or_setup` 桶就是含 `hooks` 或根目录含 `setup.sh` 的插件，桶互斥、名单可直接用）——**批量登记时 `register_converted.py` 自动完成这道分流**，无需手工推导；手工逐个登记时才需要自己看报告（hooks/setup_sh 字段或 plugin-builder-report.md 的标注）。向用户列出这批插件并提示审阅（报告里有逐条明细），用户确认后用 `register_converted.py --also <名字>` 或逐个 `register_personal.sh` 登记（setup.sh 由用户自行执行后告知即可）。其余插件照常直接登记。
（`create_plugin.py --with-register` 可把这一步并进 §4。）

### 5.1 插件本体/依赖：`setup.sh` 约定

很多插件还需要一个 CLI 本体或系统依赖（如 officecli、wecom-cli 这类二进制），只登记插件会导致「市场有了、命令没有」。
**约定：插件根目录放一个 `setup.sh` 作为本体/依赖的安装脚本；转换脚本与登记脚本都不执行它**——是否执行、何时执行由用户自己决定。

- 位置：`<插件目录>/setup.sh`（插件根目录）。
- 内容：装本体的命令，例如 `curl -fsSL https://d.officecli.ai/install.sh | bash`、`npm install -g @wecom/cli`、`brew install xxx`；写前判断已安装则跳过（`command -v xxx`），保持幂等。
- **报告与提醒**：转换时检测到 setup.sh 会逐条写进 plugin-builder-report.md（`setup.sh（本体/依赖安装脚本，未执行；请用户审阅后自行执行）`）；登记脚本检测到也会打印提示（不执行、不阻塞登记）。
- **agent 的职责**：交付时在会话中明确提醒用户——插件带 setup.sh（本体安装脚本），请审阅内容后自行执行（`bash <插件目录>/setup.sh`），完成后再到「个人」页签安装使用。**不要代用户执行它。**

## 5.2 批量转换外部插件仓库（convert_plugin_repo.py）

输入一个 **GitHub 仓库地址**（或本地目录），把仓库里的插件/技能（任意来源方言）批量转换成本项目插件。转换与登记分两步：**① convert 只转换不登记**，产物含 `plugin-builder-report.md`（人读报告，先写转换明细、登记段落占位）与 `conversion-report.json`（机器合同，带 `registration_plan` 互斥分流：registerable / hold_hooks_or_setup / hold_deps_unavailable / hold_validate_errors / failed）；**② 批量登记走 `register_converted.py <market_dir>`**（convert 的 stdout 会打印这条命令）——它按 `registration_plan` 登记 registerable 桶、自动跳过暂缓项、收集每个插件的 `kimi-work://` 链接、与注册表对账后写 `registration-report.json`（机器交付）并整体重写 `plugin-builder-report.md` 把登记段落填实、打印总结数字。**不要手写批量循环调 `register_personal.sh`**（逐个登记的脚本，只适合单插件场景或 `--also` 之外的零散补登记）——手工循环在判定方式、进度状态、对账口径上都容易出错，总结数字以 `register_converted.py` 产出的为准。

```bash
python3 scripts/convert_plugin_repo.py https://github.com/<owner>/<repo> [--output-dir <目录>] [--market <market>] [--limit N] [--jobs N]
```

- **已有产物保护**：目标 `<output-dir>/<market>/` 已存在时（包括空目录）默认停止，不覆盖已有报告或插件源码。同市场的新一批转换用 `--output-dir` 指向新的持久化产物根（可放在 `<share>/plugin-sources/` 下的独立批次目录），不要为了避开冲突改市场归属。只有用户明确确认可丢弃旧报告和同名插件源码（包括手工修改）后才加 `--force`；不能自行强制重试。日常编辑已有插件继续走 §6。
- **输入选择**：**默认直接传 URL**——转换器自己拉取（github.com 直连不通自动走 codeload tarball），总是最新默认分支。自己 `git clone` 再传本地目录只用于两种场景：转换前要本地探查/加工，或网络受限想手动控制拉取方式；**副本必须是现拉的**（拿昨天的旧 clone 转换，转出的就是旧快照）。**插件本体无需任何预先探查**：索引条目的镜像缺失/不完整由转换器自动回源拉取，不用统计镜像覆盖率、不用手动下载任何插件，也不必为探查单独 clone（自己 clone 的唯一价值是避免转换器二次拉取）。
- **规模与授权**：用户给出整仓地址即视为授权**全量**转换与登记，**不要为规模/范围停下来确认**（用户自己提出限制范围除外）。量级预期：几百个条目的索引仓，转换+登记是几分钟量级的任务，属正常——索引仓镜像覆盖大部分条目，回源拉取只针对镜像不完整的条目且 `--jobs` 并行，**不要凭"条目数 × clone"脑补出按小时计的时长**。**登记 ≠ 安装**：登记后插件以"未安装"形态出现在「个人」页签，由用户自行挑选安装，不存在"页签一次被塞满"的问题。**执行方式**：默认前台直接跑、阻塞等结果，不要因悲观时长估计改用 nohup 旁路、也不要中断流程去问用户；真超过前台超时上限时改后台执行 + 轮询，**轮询间隔 ≥30 秒**（每次轮询都是一轮 LLM 往返，等待本身不产生信息，看日志尾部即可）；也可以把等待折叠进一次前台调用：`cmd > run.log 2>&1 & CMD_PID=$!; while kill -0 $CMD_PID 2>/dev/null; do sleep 15; done; tail -20 run.log`。
- **仓库形态自动识别**：**遇到仓库地址直接调用脚本即可，形态由脚本自主判断**——按「根部索引 → 子目录索引 → 全仓 manifest 扫描 → skill-only 兜底」的顺序自动判定，不需要先探查仓库结构、不需要告诉脚本它是哪种形态：单插件仓库 / 多插件 monorepo（子目录各有 manifest）/ 索引仓库（根部 plugins.json 列表或 marketplace 索引，条目支持 `url` 或仓库内相对路径 `path`/`source`）/ 无 manifest 但有 SKILL.md、skills/ 的仓库（整仓包成 skill-only）。
- **产物**（--output-dir 默认 `<share>/plugin-sources/`）：`<目录>/<market>/<name>/` 每个插件一个目录，加上 4 个报告类文件——两步跑完后目录下共：`plugin-builder-report.md`（**唯一人读报告**：转换明细 + 登记结果；convert 先写转换部分与「登记未执行」占位，`register_converted.py` 跑完整篇重写、把登记段落填实）、`conversion-report.json`（机器合同：转换数据 + `registration_plan`，是 register_converted.py 的输入）、`registration-report.json`（机器交付：登记成败 + 完整链接 + 注册表对账，重跑登记时刷新；**重新 convert 时作废删除**——新转换结果与旧登记结果不允许混在一起）、`marketplace.orig`（**源市场全量插件清单**：索引输入取全部索引条目、无索引输入取全仓扫描结果，只在转换时生成一次的静态快照；之后的登记/安装/卸载都不改变它）。**两个 json 与 marketplace.orig 是机器合同与静态快照，不作为会话交付物展示**——人只看 `plugin-builder-report.md`，报告末尾注记了这三个文件的位置供需要时查阅。
- **参考约定**：输入 URL 形态与 ref 规则、manifest 方言识别、索引条目扩展形态、索引冲突策略、转换内部机制、market 名与安装路径背景等完整约定见 [`references/repo-conversion.md`](references/repo-conversion.md)（**出错时兜底查阅，无需每次通读**）。

## 6. 更新 / 开发迭代

**修改范围红线：只改源目录，绝不碰已安装目录。** 所有修改只能发生在登记的**源目录**（市场条目 `sourcePath` 指向的目录，即当初脚手架生成并登记的那个目录，新建时默认是 `<share>/plugin-sources/<market>/<name>/`；旧条目或显式指定的目录以登记记录为准，不自动搬迁）。插件一旦安装，daemon 会把源目录整盘复制成受管副本，**绝不能直接编辑已安装目录里的副本**——那样改动和源目录分叉，而且「更新」是整盘覆盖重装，副本里的直接改动会被全部冲掉。找不到源目录就先查市场条目，别去已安装目录里改。

**场景一：改条目元数据（displayName/描述/图标/keywords/MCP URL 等 manifest 字段）→ 用 `update_plugin.py`，一条命令：**

```bash
python3 scripts/update_plugin.py <插件目录> --display-name "<新名>" [--description ...] [--icon-url <已验证图>] [--market <market>]
```

→ **用户说"改插件名称"，要改的就是 `interface.displayName`（插件页展示的名字）——`--display-name "<新名>"`。manifest 里的 `name` 是插件 id（市场条目按 `<id>.json` 存；非 personal 市场安装后的完整 id 为 `<id>@<market>`），不是给人看的名称，不要动它。**
→ 只改写传了 flag 的字段（未传的保持原值）→ 自动升 `+local.<时间戳>` 版本 → 自动重登记覆盖市场条目（`--no-register` 可跳过，但跳过后市场条目不会变，需稍后补跑登记）。**插件当初登记到非 personal 市场时，必须传 `--market <market>`（同一个市场名），否则条目会被登记到 personal、原市场条目残留。** 个人市场按**版本号字符串不等**检出更新：已安装的用户到「个人」页签点「更新」完成升级（重装语义，daemon 侧热更，无需重启）。
→ 也可以手动编辑 manifest 的已有字段（这是更新的标准动作），然后跑 `cachebuster.py` 升版本 + 重跑一次登记——但优先用 `update_plugin.py`，免得分步漏掉登记。

**场景二：只改 SKILL.md 正文 / 脚本源码 → 直接编辑文件，然后只升版本：**

```bash
python3 scripts/cachebuster.py <插件目录>
```

→ 把 `version` 换成 `<x.y.z>+local.<时间戳>`（不污染正式 semver）。内容随安装包走，升完版本等用户在「个人」页签点「更新」即可，无需重登记。

**红线：不要用 `create_plugin.py --force` 来改字段。** `--force` 是整盘重做：manifest 按 flag 重建（没传 flag 的字段全部回默认值）、`skills/<name>/SKILL.md` 被 stub 覆盖——用户写好的内容会丢；版本号还走 patch 位递增，污染正式 semver。它只用于"推倒重来"，日常更新一律走上面两个场景。

**`name` 是插件 id，不是名称**：用户说"改名称"永远走上面的 `--display-name`。只有真要换 id 才算新插件——市场条目按 `<id>.json` 存，改 id 会产生新条目、旧条目残留，用 `create_plugin.py` 新建一个，引导用户装新的、卸旧的。

## 规则

- **缺私有信息才问，其余自填；绝不编造。**
- **新建禁止手写 manifest / SKILL.md 骨架**：`kimi.plugin.json` 必须由 `create_plugin.py` 生成，`skills/<name>/SKILL.md` 必须从 stub 改起。agent 凭印象手写 manifest 会编出 schema 里不存在的字段（如 `entryPoints`/`permissions`/顶层 `displayName`/skills 数组），导致插件登记上但不可用。**更新已有插件时直接编辑 manifest 的已有字段（或用 `update_plugin.py`）是标准动作，不算手写骨架。**
- **更新已有插件走 `update_plugin.py`（改元数据）或 编辑文件 + `cachebuster.py`（改正文/源码）；禁止用 `create_plugin.py --force` 改字段**——--force 会按 flag 重建 manifest（未传字段回默认值）并覆盖 SKILL.md 正文，只用于推倒重来。
- **只能修改插件的源目录，绝不能修改已安装目录的内容**：更新/调试插件一律编辑登记的源目录（市场条目 `sourcePath` 指向的目录）。已安装目录是 daemon 从源目录整盘复制的受管副本，直接改它会和源目录分叉、且下次「更新」被整盘覆盖；改完源目录走 `cachebuster.py` / `update_plugin.py` 升版本，由用户在「个人」页签点「更新」生效。
- **SKILL.md frontmatter 是技能的生命线**：目录型 SKILL.md 必须有 `--- name + description ---` frontmatter，description 里写清触发场景；没有它技能不会被自动加载，用户只能手动调命令。
- **校验不过夜**：登记前必须跑 `validate_plugin.py` 且结果为 0 error；validate 自身报错/崩溃也算不通过，必须先修，禁止跳过校验直接登记。**登记脚本已内嵌这道强制关卡**：`register_personal.sh` / `register_personal.py` / `create_plugin.py --with-register` 都会在登记前自动跑 validate，0 error 才放行，绕过口仅有 `--skip-validate`（需向用户说明理由）。
- 写文件 / 发布前**先向用户确认**；创建完把 manifest 摘要给用户。**登记插件直接进行，不逐次确认**（个人市场条目可随时移除、重登记可覆盖，是可逆的本地动作）——**但含 setup.sh 或 hooks 的插件不随流程自动登记**：分流与审阅口径见 §5「含 setup.sh / hooks 的插件先不登记」（批量登记由 `register_converted.py` 自动执行），由用户决定何时登记；其余插件照常直接登记。
- **setup.sh 与 hooks 都不做事前门槛，但都必须透明可查**：插件自带的 `setup.sh`（本体/依赖安装脚本）**转换脚本与登记脚本都不执行**——是否执行、何时执行由用户自己决定；哪些插件带 hooks/setup.sh、事件与命令内容逐条写进 plugin-builder-report.md；validate 对任何 hooks 声明都会输出 WARN 提醒。
- **装完不用再提重启**：daemon 侧安装热更活跃会话。若用户说看不到插件，先确认他点过「个人」页签的 ＋ 安装。
- **PLUGIN_ID_CONFLICT 故障指引**：登记报这个错 = 该 id 已被市场外的安装路径（旧流程 / `kimi-plugin install` / 官方插件下载渠道）占用且没有市场条目——引导用户先在「已安装」页签卸载同名插件，再重新登记。
- **最终回复的「使用方式」只写自然语言需求，不贴命令**：插件登记+安装好后告诉用户的是「到「个人」页签点 ＋ 安装，然后可以直接对我说什么」，给 3-5 个自然语言需求示例（如「帮我搜周杰伦的歌」「看看网易云热搜」）。**禁止**把 `python3 scripts/xxx.py <命令> [参数]` 这类 CLI 命令清单贴给用户当使用方式——那些命令是写给 agent 看的（在插件的 SKILL.md 里），贴出来会让用户误以为要自己动手跑代码。用户要做的就是点一下安装，然后用自然语言提需求，插件由 agent 自动调用。
- **最终回复必须带上插件链接**：登记路径（`register_personal.sh/py`、`create_plugin.py --with-register`、`update_plugin.py` 重登记）的 CLI JSON 输出里有 `link` 字段（`kimi-work://plugin?id=<id>`）；`cachebuster.py` 路径脚本会打印 `plugin link -> ...`。最终回复用 markdown 链接形式原样给出：`插件链接：[<displayName>](kimi-work://plugin?id=<id>)`，并附一句「点击可打开插件详情」。链接一律从脚本/CLI 输出里取，不要自己拼；创建和更新场景都要带。**批量场景**（register_converted.py）：每个成功插件的链接在 `registration-report.json` 的 `registered[].link`；**最终回复的示例链接只从 `register_converted.py` stdout 给出的示例（最多 5 个）中选用**——不要凭插件名猜测它是否登记成功（名字耳熟不代表在清单里），也不要再读文件探查挑选，stdout 的示例就是为最终回复准备的；确需更多时按 `registered[].link` 里的真实条目补。登记成功/暂缓/被拒的数字直接引用工具打印的总结，不要自己重新数（注册表目录里的 `marketplace.orig` 不是插件条目，数文件会多算一个）。**批量场景的文件交付固定为 `plugin-builder-report.md` 一个链接**（转换+登记合订的人读报告，含暂缓名单与审阅指引）；`conversion-report.json`、`registration-report.json`、`marketplace.orig` 是机器合同与静态快照，**不要在会话里作为交付物罗列**——报告末尾已注记它们的位置，需要的人自己会找到。
- 脚本一律 `python3 scripts/…` 或 `bash scripts/…` 调用。

## 一句话流程

（有终端、无 token）认输入 → 描述自填·缺私有信息才问 → `create_plugin.py` + 填 + `validate_plugin.py` → **`register_personal.sh` 登记进个人市场（缺省 personal）→ 用户到「个人」页签点 ＋ 安装（免重启，当前会话即可用）** → 更新：改名称等元数据用 `update_plugin.py`（`--display-name` 改展示名，id 不动；改字段+升版本+重登记一步完成），改正文/源码则编辑后跑 `cachebuster.py` 升版本 → 「个人」页签点「更新」。批量转换仓库：`convert_plugin_repo.py` 出产物与 `registration_plan` → `register_converted.py <market_dir>` 批量登记+对账+总结 → 暂缓的 hooks/setup.sh 插件经用户审阅后用 `--also` 补登记。
