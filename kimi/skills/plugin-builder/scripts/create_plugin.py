#!/usr/bin/env python3
"""create_plugin.py — 脚手架一个 Kimi 插件（复用 plugin_common）。"""
import argparse, json, os, sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plugin_common as pc

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("plugin_name")
    p.add_argument("--type", choices=["skill-only", "mcp", "mcp+skills"], default="skill-only")
    p.add_argument("--path", default=None,
                   help="源码根目录（默认 <share-dir>/plugin-sources）；显式路径保持原样使用")
    p.add_argument("--market", default=None,
                   help="目标市场名（缺省 personal）：产物落在 <path>/<market>/<name>/，"
                        "--with-register 时同名将透传给登记 CLI")
    p.add_argument("--display-name"); p.add_argument("--description")
    p.add_argument("--short"); p.add_argument("--long")
    p.add_argument("--category", default=pc.DEFAULT_CATEGORY)
    p.add_argument("--keywords"); p.add_argument("--author"); p.add_argument("--homepage")
    p.add_argument("--icon-url"); p.add_argument("--mcp-url"); p.add_argument("--skill-instructions")
    p.add_argument("--with-agents", action="store_true",
                   help="声明 agents 组件（子代理角色定义，生成 agents/<name>.md stub）")
    p.add_argument("--with-commands", action="store_true",
                   help="声明 commands 组件（用户可触发的斜杠命令，生成 commands/<name>.md stub）")
    p.add_argument("--with-session-start", dest="with_session_start", action="store_true",
                   help="声明 sessionStart（每个会话开始时自动加载插件自带 skill 的提醒；"
                        "type 不含 skills 时自动升级为 mcp+skills）")
    p.add_argument("--with-system-prompt", dest="with_system_prompt", action="store_true",
                   help="声明 systemPromptPath（注入每个会话系统提示的行为约定，生成 system-prompt.md stub）")
    p.add_argument("--with-hooks", action="store_true",
                   help="声明 hooks（会话事件时自动执行插件内命令，生成 hooks/session-start.sh stub）")
    p.add_argument("--with-register", dest="with_register", action="store_true",
                   help="脚手架完成后直接登记进个人市场（只登记不安装；--market 缺省 personal）")
    p.add_argument("--share-dir",
                   help="daimon-share 目录（默认 $KIMI_SHARE_DIR > macOS 客户端默认 > ~/.kimi）")
    p.add_argument("--daimon-bin", default=None,
                   help="kimi-daimon 二进制路径（默认读 $DAIMON_RUNTIME_BINARY_PATH，runtime 环境必然存在）")
    p.add_argument("--node", help="node 二进制路径（默认从 PATH 找）")
    p.add_argument("--force", action="store_true")
    return p.parse_args()

def main():
    a = parse_args()
    raw = a.plugin_name
    name = pc.validate_plugin_name(pc.normalize_plugin_name(raw))
    if name != raw:
        print(f"note: plugin name 归一化为 {name}")
    market = pc.DEFAULT_MARKET
    if a.market:
        market = pc.validate_market_name(pc.normalize_market_name(a.market))
        if market != a.market:
            print(f"note: market 名归一化为 {market}")
    display = a.display_name or pc.display_name_from_plugin_name(name)

    source_root = (
        Path(a.path).expanduser().resolve()
        if a.path is not None else pc.resolve_plugin_sources_dir(a.share_dir)
    )
    root = source_root / market / name
    if root.exists() and not a.force:
        sys.exit(f"error: {root} 已存在（--force 覆盖）")

    # --force 重跑 = 重新生成：读现有版本号做 patch 位递增（全新生成从 0.1.0 起步），
    # 保证个人市场按版本号字符串不等能检出更新。
    bumped_version = None
    existing_manifest = root / "kimi.plugin.json"
    if root.exists() and a.force and existing_manifest.is_file():
        try:
            current_version = pc.load_json(existing_manifest).get("version")
        except Exception:
            current_version = None
        if current_version:
            bumped_version = pc.bump_patch_version(current_version)
    root.mkdir(parents=True, exist_ok=True)

    # --with-session-start 引用插件自带的同名 skill，没有 skill 没意义：
    # type 不含 skills 时自动升级为 mcp+skills（升级要发生在 build_plugin_json 之前）。
    if a.with_session_start and a.type not in ("skill-only", "mcp+skills"):
        a.type = "mcp+skills"
        print("note: --with-session-start 需要插件带 skills，type 已升级为 mcp+skills")

    manifest = pc.build_plugin_json(name, display, a)
    if bumped_version:
        manifest["version"] = bumped_version
        print(f"version: 递增为 {bumped_version}（--force 重新生成）")
    pc.write_json(root / "kimi.plugin.json", manifest, force=True)

    # 图标约定：--icon-url 下载为插件根目录的 icon.<ext>（个人市场按文件名约定读取），
    # manifest 里的 interface.iconUrl 保留（桌面目录对本地插件仍使用它）。
    if a.icon_url:
        pc.fetch_icon_file(a.icon_url, root)

    if a.type in ("skill-only", "mcp+skills"):
        pc.create_stub_file(
            root / "skills" / name / "SKILL.md",
            f"---\nname: {name}\ndescription: {a.description or (name + ' 技能，触发词写清楚')}\n---\n\n"
            f"# {display}\n\nTODO_写清楚何时用、怎么用（脚本用 python3/bash 调）。\n",
            force=a.force)
    if a.type in ("mcp", "mcp+skills") and not getattr(a, "mcp_url", None):
        pc.create_stub_file(root / ".mcp.json", '{\n  "mcpServers": {}\n}\n', force=a.force)

    # 其余组件 stub（kimi.plugin.json 里的对应字段已由 build_plugin_json 写好）
    if a.with_agents:
        pc.create_stub_file(
            root / "agents" / f"{name}.md",
            f"---\nname: {name}\ndescription: {a.description or (name + ' 子代理')}\n---\n\n"
            f"# {display} 子代理\n\n"
            "TODO_写清楚这个子代理的角色与行为：它负责什么任务、按什么步骤做、输出什么结果。\n",
            force=a.force)
    if a.with_commands:
        pc.create_stub_file(
            root / "commands" / f"{name}.md",
            f"---\nname: {name}\ndescription: {a.description or (name + ' 命令')}\n---\n\n"
            f"# {display}\n\nTODO_写清楚这条命令要 agent 做什么。\n\n"
            "参数占位：正文里写 `$ARGUMENTS` 会被用户的参数原样替换；"
            "正文不写 `$ARGUMENTS` 时，参数会以 `ARGUMENTS: ...` 形式追加在正文末尾。\n",
            force=a.force)
    if a.with_system_prompt:
        pc.create_stub_file(
            root / "system-prompt.md",
            f"# {display} 行为约定\n\n"
            "这段文本会注入每个会话的系统提示。TODO_写清插件生效期间 agent 必须遵守的行为约定"
            "（何时用本插件的组件、输出格式、禁止事项）。保持精简，文件上限 32 KB。\n",
            force=a.force)
    if a.with_hooks:
        pc.create_stub_file(
            root / "hooks" / "session-start.sh",
            "#!/usr/bin/env bash\n"
            "SessionStart hook 示例：会话开始时由 runtime 自动执行（cwd 为插件目录）。\n"
            "TODO_换成插件真正需要的无害动作；写文件/联网/改环境前必须先获用户确认。\n"
            "set -euo pipefail\n"
            "echo \"[$(date -u +%FT%TZ)] session start\" >&2\n",
            force=a.force)

    print(f"scaffolded: {root}/kimi.plugin.json")
    print("next: 填真实字段（无 TODO）→ validate_plugin.py → register_personal.py")

    if a.with_register:
        # 登记进个人市场（走官方 CLI，只登记不安装）；登记前强制校验
        if not pc.run_validator(root):
            sys.exit("错误：插件校验未通过，未登记。先修复 ERROR 再重新 --with-register。")
        share_dir = a.share_dir or str(pc.resolve_share_dir())
        result = pc.register_personal_plugin(root, share_dir=share_dir,
                                    daimon_bin=a.daimon_bin, node_bin=a.node,
                                    market=market)
        print(f"registered to plugin market [{market}]: {share_dir}")
        # 与 register_personal.py 一致：原样透出 CLI JSON（含 link 字段），最终回复要用
        if result:
            print(f"  result -> {json.dumps(result, ensure_ascii=False)}")
        print("提醒用户：到插件页「个人」页签点 ＋ 安装即可使用（daemon 侧热更，无需重启）。")
        # setup.sh（本体/依赖安装脚本）：脚手架/登记脚本从不执行，只提示用户自行审阅后执行。
        if (root / "setup.sh").is_file():
            print(f"提示：插件含 setup.sh（本体/依赖安装脚本，登记脚本不执行）。"
                  f"请用户审阅后自行执行：bash {root / 'setup.sh'}")

if __name__ == "__main__":
    main()
