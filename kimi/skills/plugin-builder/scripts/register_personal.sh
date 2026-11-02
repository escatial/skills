#!/bin/bash
# register_personal.sh — 通用：把任意本地插件目录登记进个人市场（只登记不安装）
#
# 用法：
#   bash register_personal.sh [--skip-validate] [--market <name>] <插件目录> [share-dir]
#
# 通用部分（不要改）：kimi-daimon 查找逻辑、share 目录解析、登记命令。
# 不通用部分（agent 按用户实际情况填）：<插件目录> —— 必须含 kimi.plugin.json
# （相对/绝对路径均可，脚本自己转绝对路径）；可选第二参数 share-dir 覆盖默认解析
# （必须是目录路径，选项值请放插件目录之前，否则会被拒绝而不是静默吞掉）。
# 例外：--json 在任何位置都被接受并忽略——脚本固定以 --json 调 CLI，stdout 本即
# JSON；技能文档展示了内部 CLI 调用带 --json，agent 顺手传给本脚本不应构成错误。
#
# share 目录解析顺序：第二参数 > $KIMI_SHARE_DIR > macOS 默认
# （~/Library/Application Support/kimi-desktop/daimon-share）> 非 macOS 回退 ~/.kimi。
#
# 登记走客户端官方 CLI `kimi-daimon kimi-plugin register-personal`（校验 + 写
# <share>/daimon/plugin-market/<market>/<id>.json，registeredBy "cli"），不安装。
# 市场名解析：--market 显式 > 产物路径的市场段（plugin-sources/ 或旧 plugins/ 根）
# > personal；非 personal 市场的插件安装后以 <id>@<market> 为插件 id，
# 并在市场目录生成 marketplace.orig 只读派生清单。
# 登记后插件出现在客户端插件页「个人」页签（未安装）；用户点 ＋ 安装，
# daemon 侧热更活跃会话——无需重启客户端。

set -euo pipefail

# 先过滤 --json（任意位置都接受并忽略）：脚本固定以 --json 调 CLI，stdout 本即
# JSON，不需要也不应该因为这个 flag 报错。
ARGS=()
for arg in "$@"; do
    if [ "$arg" = "--json" ]; then
        continue
    fi
    ARGS+=("$arg")
done
set -- ${ARGS[@]+"${ARGS[@]}"}

SKIP_VALIDATE=0
MARKET=""
while [ $# -gt 0 ]; do
    case "${1:-}" in
        --skip-validate) SKIP_VALIDATE=1; shift ;;
        --market) MARKET="${2:?--market 需要市场名}"; shift 2 ;;
        --market=*) MARKET="${1#--market=}"; shift ;;
        --*) echo "错误：未知选项「$1」（支持：--skip-validate / --market；输出本即 JSON，--json 可省略）。" >&2; exit 1 ;;
        *) break ;;
    esac
done

if [ $# -lt 1 ]; then
    echo "用法: bash register_personal.sh [--skip-validate] [--market <name>] <插件目录(含 kimi.plugin.json)> [share-dir]" >&2
    exit 1
fi
if [ $# -gt 2 ]; then
    echo "错误：位置参数过多（最多 <插件目录> [share-dir] 两个）。" >&2
    exit 1
fi
PLUGIN_SOURCE="$1"
if [ $# -ge 2 ] && [[ "$2" == -* ]]; then
    echo "错误：第二参数应是 share 目录，不接受选项「$2」。选项请放在插件目录之前" >&2
    echo "      （支持：--skip-validate / --market；输出本即 JSON，--json 可省略）；">&2
    echo "      share 目录也可用环境变量 KIMI_SHARE_DIR 指定。" >&2
    exit 1
fi

# 插件目录转绝对路径（CLI 要求 pluginRootAbsolute）：不存在/不是目录直接报错。
if [ ! -d "$PLUGIN_SOURCE" ]; then
    echo "错误：插件目录不存在或不是目录：$PLUGIN_SOURCE" >&2
    exit 1
fi
PLUGIN_SOURCE="$(cd "$PLUGIN_SOURCE" && pwd -P)"

# 市场名解析：--market 显式 > 产物路径的市场段（plugin-sources/ 或旧 plugins/ 根）
# > personal。产物约定见 create_plugin.py / convert_plugin_repo.py。
if [ -z "$MARKET" ]; then
    PARENT_DIR="$(basename "$(dirname "$PLUGIN_SOURCE")")"
    GRANDPARENT_DIR="$(basename "$(dirname "$(dirname "$PLUGIN_SOURCE")")")"
    if { [ "$GRANDPARENT_DIR" = "plugin-sources" ] || [ "$GRANDPARENT_DIR" = "plugins" ]; } && [[ "$PARENT_DIR" =~ ^[a-z0-9][a-z0-9_-]{0,63}$ ]]; then
        MARKET="$PARENT_DIR"
    fi
fi

# share 目录解析：第二参数 > KIMI_SHARE_DIR > 平台默认
if [ $# -ge 2 ] && [ -n "${2:-}" ]; then
    SHARE_DIR="$2"
elif [ -n "${KIMI_SHARE_DIR:-}" ]; then
    SHARE_DIR="$KIMI_SHARE_DIR"
elif [ "$(uname -s)" = "Darwin" ]; then
    SHARE_DIR="$HOME/Library/Application Support/kimi-desktop/daimon-share"
else
    SHARE_DIR="$HOME/.kimi"
fi
# share 目录转绝对路径（与 CLI 的 resolve 行为一致，条目路径输出不受 cwd 影响）
if [ -d "$SHARE_DIR" ]; then
    SHARE_DIR="$(cd "$SHARE_DIR" && pwd -P)"
fi

# kimi-daimon 可执行文件 = $DAIMON_RUNTIME_BINARY_PATH（客户端启动 daemon 时注入的
# 运行中真实路径，跨平台；runtime 环境中必然存在，不设回退）
if [ -z "${DAIMON_RUNTIME_BINARY_PATH:-}" ]; then
    echo "错误：DAIMON_RUNTIME_BINARY_PATH 未设置（应由客户端启动 daemon 时注入）；请在 Kimi 会话环境内运行。" >&2
    exit 1
fi
if [ ! -x "$DAIMON_RUNTIME_BINARY_PATH" ]; then
    echo "错误：DAIMON_RUNTIME_BINARY_PATH 指向的 kimi-daimon 不可执行：$DAIMON_RUNTIME_BINARY_PATH" >&2
    exit 1
fi
KIMI_DAEMON="$DAIMON_RUNTIME_BINARY_PATH"

# 检查插件目录是否合法
if [ ! -f "$PLUGIN_SOURCE/kimi.plugin.json" ]; then
    echo "错误：插件目录缺少 kimi.plugin.json：$PLUGIN_SOURCE" >&2
    exit 1
fi

# 强制校验：先过 validate_plugin.py（0 error）才允许登记；validate 自身报错也算不通过。
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "$SKIP_VALIDATE" != "1" ] && [ -f "$SCRIPT_DIR/validate_plugin.py" ]; then
    if ! python3 "$SCRIPT_DIR/validate_plugin.py" "$PLUGIN_SOURCE"; then
        echo "错误：插件校验未通过，拒绝登记。先修复 ERROR；确认无需校验时用 --skip-validate 跳过。" >&2
        exit 3
    fi
fi

# 插件 id（manifest name 小写），用于输出条目落盘路径
PLUGIN_ID="$(python3 -c "
import json
print(json.load(open('$PLUGIN_SOURCE/kimi.plugin.json', encoding='utf-8'))['name'].strip().lower())
" 2>/dev/null || echo "")"

# hooks 条数（仅用于提示，不拦截登记；分流规则见 SKILL.md「先不登记」条款）
HOOKS_COUNT="$(python3 -c "
import json
m = json.load(open('$PLUGIN_SOURCE/kimi.plugin.json', encoding='utf-8'))
h = m.get('hooks')
print(len(h) if isinstance(h, (list, dict)) else 0)
" 2>/dev/null || echo 0)"

# kimi-daimon 需要 Node（>= 24）：优先用与其同目录的托管 Node（daemon 管理布局
# tools/node/<ver>/bin/，版本与 daimon 要求精确匹配），其次 PATH 里的 node。
SIBLING_NODE="$(dirname "$KIMI_DAEMON")/node"
NODE_BIN=""
if [ -x "$SIBLING_NODE" ]; then
    NODE_BIN="$SIBLING_NODE"
elif command -v node >/dev/null 2>&1; then
    NODE_BIN="$(command -v node)"
else
    echo "错误：找不到可用的 Node（kimi-daimon 同目录无托管 node，PATH 里也没有 node）。" >&2
    exit 1
fi

MARKET_ARGS=()
if [ -n "$MARKET" ]; then
    MARKET_ARGS=(--market "$MARKET")
fi

# 注意：${MARKET_ARGS[@]+"${MARKET_ARGS[@]}"} 是 bash 3.2 兼容写法（set -u 下空数组
# 不展开为任何参数；直接 "${MARKET_ARGS[@]}" 在 bash 3.2 空数组时会报 unbound variable）。
# 不合并 stderr 进 stdout：stdout 保持纯 JSON（含 ok/link 字段），批量循环可直接
# 解析；CLI 的诊断日志走 stderr，Bash 工具里同样可见。
"$KIMI_DAEMON" --node "$NODE_BIN" kimi-plugin register-personal \
    "$PLUGIN_SOURCE" \
    --share-dir "$SHARE_DIR" \
    ${MARKET_ARGS[@]+"${MARKET_ARGS[@]}"} \
    --json

ENTRY_PATH="$SHARE_DIR/daimon/plugin-market/${MARKET:-personal}/${PLUGIN_ID:-<id>}.json"
echo "已登记到个人市场（未安装，市场：${MARKET:-personal}，条目：${ENTRY_PATH}）。请用户到插件页「个人」页签点 ＋ 安装——daemon 侧热更，无需重启。" >&2

# setup.sh（插件本体/依赖安装脚本）：登记脚本从不执行，只提示用户自行审阅后执行。
if [ -f "$PLUGIN_SOURCE/setup.sh" ]; then
    echo "提示：插件含 setup.sh（本体/依赖安装脚本，登记脚本不执行）。请用户审阅后自行执行：bash $PLUGIN_SOURCE/setup.sh" >&2
fi

# hooks 提示（不拦截）：按 SKILL.md 规则，含 hooks 的插件应先经用户审阅再登记。
if [ "$HOOKS_COUNT" -gt 0 ]; then
    echo "提示：插件 manifest 声明了 $HOOKS_COUNT 条 hooks（会话事件时自动执行的命令）。按规则此类插件应先经用户审阅再登记；hooks 事件与命令明细见 plugin-builder-report.md。" >&2
fi
