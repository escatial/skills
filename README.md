# AI Agent Skills 合集

本仓库收录了本机各 AI Agent 的全部技能（Skills），按 Agent 归类整理。

- 整理时间：2026-11-03
- 共 **18 个集合、1003 个技能**
- 每个子目录内含 `README.md` 索引（技能名 + 简要说明，提取自各技能的 `SKILL.md` frontmatter）

## 目录结构

| Agent / 来源 | 集合路径 | 数量 | 本机原始位置 |
| --- | --- | --- | --- |
| DeepSeek Harness | `deepseek-harness/skills` | 210 | `~/.agents/skills`（DSH 会话技能库，读取 agents 标准目录） |
| Claude Code | `claude-code/skills` | 211 | `~/.claude/skills` |
| Codex CLI | `codex/skills` | 2 | `~/.codex/skills`（含 `.system` 内置系统技能） |
| Codex CLI（openai/skills 精选） | `codex/openai-curated-skills` | 39 | `~/.codex/vendor_imports/skills/skills/.curated` |
| ZCode | `zcode/skills` | 55 | `~/.zcode/skills` |
| Kimi | `kimi/skills` | 50 | `D:\KimiData\daimon-share\daimon\skills`（Kimi 官方技能库，与 Kimi 桌面端 official-skill-origins 一致） |
| MiniMax | `minimax/skills` | 1 | `~/.minimax/skills`（各 agents/*/skills 子目录为空） |
| Trae（用户技能） | `trae/skills` | 17 | `~/.trae/skills` |
| Trae（内置技能） | `trae/builtin-skills` | 7 | `~/.trae/builtin/global/skills` |
| WorkBuddy | `workbuddy/skills` | 5 | `~/.workbuddy/skills` |
| CodeBuddy | `codebuddy/skills` | 14 | `~/.codebuddy/skills` |
| CodeBuddy（技能市场） | `codebuddy/skills-marketplace` | 295 | `~/.codebuddy/skills-marketplace/skills` |
| MarsCode（内置） | `marscode/builtin-skills` | 8 | `~/.marscode/builtin/global/skills` |
| OpenClaw（飞书插件） | `openclaw/feishu-plugin-skills` | 10 | `~/.openclaw/extensions/feishu-openclaw-plugin/skills` |
| OpenClaw（AutoClaw） | `openclaw/autoclaw-skills` | 63 | `~/.openclaw-autoclaw/skills` |
| MiniMax Hub | `minimax-hub/skills` | 5 | `~/.hub/skills` |
| MiniMax Hub（config-v2） | `minimax-hub/config-v2-skills` | 10 | `~/.hub/.config-v2/skills` |
| CC Switch | `cc-switch/skills` | 1 | `~/.cc-switch/skills` |

## 整理说明

- **去重策略**：未做跨 Agent 去重，按“归agent原样保留”的原则整理。很多技能（如 `reverse-engineer-anything`、`conf-papers`、MATLAB/Simulink 系列）被多个 Agent 同步安装，属于正常重复。
- **排除项**：
  - `~/.agents/skills/conf-papers.bak.20260501`（备份目录）
  - `~/.codebuddy/skills-marketplace.backup-13840`（整个备份目录）
  - `autoglm-browser-agent/dependency/mcporter.exe`（110MB，超过 GitHub 单文件 100MB 限制）
  - WorkBuddy 的 3 个迁移元数据 json（`.disable_to_model_invocation_migration.json` 等）
  - `~/.claude/skills` 根目录的仓库元数据文件（`README.md`、`license.txt`、`SECURITY.md`）
  - Codex `.system` 内的 marker 文件
- **未发现技能的 Agent**：`.kimi` / `.kimi-code`（Kimi CLI 未安装任何用户技能，桌面端技能位于 `D:\KimiData`）、`.lingma`（通义灵码）、GitHub Copilot、Cursor（本机无 skills 目录）。
- DeepSeek Harness 的会话技能（archify、matlab-* 系列等）实际读取自 `~/.agents/skills`（agents 标准目录）。

## 使用方式

各 Agent 的技能均为标准结构：目录内含 `SKILL.md`（YAML frontmatter 定义 `name` / `description`，正文为任务指令）。要安装到对应 Agent，将技能目录复制回该 Agent 的技能目录即可（各集合的原始位置见上表）。

## 许可

技能内容来自各官方技能市场及个人整理，版权归原作者所有，仅供个人备份与学习使用。
