#!/usr/bin/env python3
"""register_personal.py — 把插件登记进个人市场（只登记不安装）。

注册表在 daimon-share 下的 daimon/plugin-market/<market>/<id>.json。市场名解析
顺序：--market 显式指定 > 产物路径的市场段（plugin-sources/ 或旧 plugins/ 根）
> personal；非 personal 市场的插件安装后以 <id>@<market> 为 id，并在市场目录生成
marketplace.orig 只读派生清单。登记动作委托给客户端官方 CLI
kimi-daimon kimi-plugin register-personal。
登记后插件出现在客户端插件页「个人」页签（未安装），用户点 ＋ 安装，
daemon 侧热更活跃会话，无需重启客户端。"""
import argparse, json, os, sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plugin_common as pc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plugin_dir")
    ap.add_argument("--share-dir",
                    help="daimon-share 目录（默认 $KIMI_SHARE_DIR > macOS 客户端默认 > ~/.kimi）")
    ap.add_argument("--market", default=None,
                    help="目标市场名（缺省：从插件目录的产物路径 plugin-sources/<market>/<name>/（兼容旧 plugins/ 根） "
                         "推断，推断不到回退 personal）")
    ap.add_argument("--daimon-bin", default=None,
                    help="kimi-daimon 二进制路径（默认读 $DAIMON_RUNTIME_BINARY_PATH，runtime 环境必然存在）")
    ap.add_argument("--node", help="node 二进制路径（默认从 PATH 找）")
    ap.add_argument("--skip-validate", action="store_true",
                    help="跳过登记前强制校验（默认校验不过拒绝登记）")
    ap.add_argument("--json", action="store_true",
                    help="兼容 flag：CLI 输出本即 JSON，传入忽略（任何位置都接受）")
    a = ap.parse_args()

    src = Path(a.plugin_dir).expanduser().resolve()
    share_dir = a.share_dir or str(pc.resolve_share_dir())

    # 强制校验：先过 validate_plugin.py（0 error）才允许登记；validate 自身报错也算不通过
    if not a.skip_validate and not pc.run_validator(src):
        sys.exit("错误：插件校验未通过，未登记。先修复 ERROR；确认无需校验时用 --skip-validate 跳过。")

    m = pc.load_json(src / "kimi.plugin.json")
    name, ver = m["name"], m.get("version", "0.1.0")

    result = pc.register_personal_plugin(src, share_dir=share_dir,
                                         daimon_bin=a.daimon_bin, node_bin=a.node,
                                         market=a.market)

    market_label = pc.resolve_register_market(src, a.market)
    entry_path = Path(share_dir) / "daimon" / "plugin-market" / market_label / f"{name.lower()}.json"
    print(f"registered to plugin market [{market_label}]: {name} @ {ver}")
    print(f"  entry -> {entry_path}")
    if result:
        print(f"  result -> {json.dumps(result, ensure_ascii=False)}")

    # setup.sh（本体/依赖安装脚本）：登记脚本从不执行，只提示用户自行审阅后执行。
    if (src / "setup.sh").is_file():
        print(f"提示：插件含 setup.sh（本体/依赖安装脚本，登记脚本不执行）。"
              f"请用户审阅后自行执行：bash {src / 'setup.sh'}")

    # hooks 提示（不拦截）：按 SKILL.md 规则，含 hooks 的插件应先经用户审阅再登记。
    hooks = m.get("hooks")
    hooks_count = len(hooks) if isinstance(hooks, (list, dict)) else 0
    if hooks_count > 0:
        print(f"提示：插件 manifest 声明了 {hooks_count} 条 hooks（会话事件时自动执行的命令）。"
              "按规则此类插件应先经用户审阅再登记；hooks 事件与命令明细见 plugin-builder-report.md。")

    print("提醒用户：到插件页「个人」页签点 ＋ 安装即可使用（daemon 侧热更，无需重启）。")


if __name__ == "__main__":
    main()
