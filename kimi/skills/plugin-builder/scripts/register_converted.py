#!/usr/bin/env python3
"""register_converted.py — convert_plugin_repo.py 产物的批量登记闭环。

读 <market_dir>/conversion-report.json 的 registration_plan（convert 已按
plugin_common.build_registration_plan 写好；旧报告缺该字段时用同一函数现算，
两处判定不会分叉），把 registerable 桶的插件逐个登记进个人市场（走客户端官方
CLI kimi-daimon kimi-plugin register-personal，只登记不安装），含 hooks/setup.sh、
依赖不可用、校验 error、转换失败的插件自动分流跳过。逐个收集 CLI 返回的
kimi-work:// 链接，结束后与注册表目录对账（只数 <id>.json，marketplace.orig
无 .json 后缀天然排除），把机器可读结果写进 <market_dir>/registration-report.json，
并整体重写 <market_dir>/plugin-builder-report.md（把「登记结果」段落填实——
人读报告只有这一份，json 不作为会话交付物），最后打印可直接转述给用户的总结
（数字由本工具产出，不靠 agent 自己算）。

用法：
  python3 register_converted.py <market_dir> [--share-dir <dir>] [--market <name>]
      [--also name1,name2] [--skip-validate] [--dry-run]

- <market_dir>：convert 的产物目录（含 conversion-report.json，默认 <share>/plugin-sources/<market>/）。
- --also：把暂缓桶里已获用户审阅确认的插件一并登记（逗号分隔的名字）。
- 登记失败的插件记入报告并继续，不中断整批；瞬时失败自动重试一次。
"""
import argparse, json, os, re, subprocess, sys, time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plugin_common as pc
import convert_plugin_repo as cpr

REPORT_NAME = "registration-report.json"


def _trim(text, limit=600):
    text = str(text or "").strip()
    return text if len(text) <= limit else text[:limit] + "…"


def _clean_error(text):
    """登记失败的错误信息压成单行：优先取 CLI JSON 的 error 字段（如
    「插件包的包总大小超过限制。」），取不到就把全文压缩空白后截断——
    多行 JSON/日志混排会把报告和 stdout 的列表结构冲乱。"""
    m = re.search(r'"error"\s*:\s*"([^"]+)"', str(text or ""))
    if m:
        return m.group(1)
    return _trim(" ".join(str(text or "").split()), 300)


def _entry_name(r):
    return (r.get("kimi_name") or r.get("index_name") or r.get("origin")
            or r.get("source_dir") or "<unknown>")


def load_plan(market_dir):
    """读 conversion-report.json，返回 (report, plan, name→plugin_dir 映射)。"""
    report_path = os.path.join(market_dir, "conversion-report.json")
    if not os.path.isfile(report_path):
        sys.exit(f"错误：找不到 {report_path}——先跑 convert_plugin_repo.py 生成产物，"
                 f"或确认 <market_dir> 指对（默认 <share>/plugin-sources/<market>/，旧产物为 plugins/<market>/）。")
    report = pc.load_json(report_path)
    results = report.get("results") or []
    plan = report.get("registration_plan") or pc.build_registration_plan(results)
    dirs = {}
    for r in results:
        out = r.get("output_dir")
        if out:
            dirs[_entry_name(r)] = out
    return report, plan, dirs


def resolve_market(market_dir, report, override=None):
    """批量登记的市场名：--market 显式 > 报告里的 market 字段 > 目录名 > personal。"""
    if override:
        return pc.validate_market_name(pc.normalize_market_name(override))
    market = report.get("market")
    if market:
        return pc.validate_market_name(pc.normalize_market_name(str(market)))
    base = os.path.basename(os.path.normpath(market_dir))
    if pc.MARKET_NAME_RE.match(base):
        return base
    return pc.DEFAULT_MARKET


def _run_validator_quiet(plugin_dir):
    """登记前跑 validate_plugin.py，输出全程捕获：通过时静默（批量场景 180 个插件
    不该刷 360 行校验输出），失败时把输出带进错误。校验器不存在时不阻断。"""
    validator = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "validate_plugin.py")
    if not os.path.exists(validator):
        return True, ""
    # 与 convert_plugin_repo.py 同一口径：校验子进程两侧钉死 utf-8，见该文件的说明；
    # 产物路径前缀化（pc.winlong），深路径插件扫描不撞 Windows MAX_PATH
    proc = subprocess.run([sys.executable, validator, pc.winlong(str(plugin_dir))],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                          encoding="utf-8", errors="replace",
                          env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    return proc.returncode == 0, (proc.stdout or "").strip()


def register_one(plugin_dir, share_dir, market, daimon_bin=None, node_bin=None,
                 skip_validate=False):
    """登记单个插件，返回 (ok, link, error)。校验不过或 CLI 失败（重试一次仍失败）
    都记 error，不抛异常——批量循环里单个失败不中断整批。"""
    if not skip_validate:
        valid, validate_out = _run_validator_quiet(plugin_dir)
        if not valid:
            return False, None, f"validate_plugin.py 校验未通过（登记前强制关卡）: {_trim(validate_out, 300)}"
    last_error = None
    for attempt in (1, 2):
        try:
            result = pc.register_personal_plugin(
                plugin_dir, share_dir=share_dir, daimon_bin=daimon_bin,
                node_bin=node_bin, market=market)
            try:
                pid = str(pc.load_json(
                    os.path.join(plugin_dir, "kimi.plugin.json"))["name"]).strip().lower()
            except Exception:  # noqa: BLE001 — 回退目录名（标准产物两者一致）
                pid = os.path.basename(os.path.normpath(plugin_dir))
            if market != pc.DEFAULT_MARKET:
                pid = f"{pid}@{market}"
            link = result.get("link") or pc.plugin_link(pid)
            return True, link, None
        except Exception as e:  # noqa: BLE001 — 失败记进报告继续整批
            last_error = _clean_error(e)
            if attempt == 1:
                time.sleep(1)
    return False, None, last_error


def print_summary(market, registry_dir, registered, failed, held, pre_existing,
                  missing, md_path):
    print("")
    print(f"批量登记完成（市场：{market}）")
    print(f"- 登记成功: {len(registered)}")
    print(f"- 登记失败: {len(failed)}")
    for f in failed:
        print(f"  - {f['name']}: {f['error']}")
    held_hooks = held.get("hold_hooks_or_setup") or []
    held_deps = held.get("hold_deps_unavailable") or []
    held_invalid = held.get("hold_validate_errors") or []
    held_failed = held.get("failed") or []
    print(f"- 暂缓·hooks/setup.sh（需用户审阅后才登记）: {len(held_hooks)}")
    if held_hooks:
        names = [h["name"] for h in held_hooks]
        print(f"    {', '.join(names[:20])}" + (f" …等 {len(names)} 个" if len(names) > 20 else ""))
    print(f"- 暂缓·依赖不可用: {len(held_deps)}")
    if held_deps:
        names = [h["name"] for h in held_deps]
        print(f"    {', '.join(names[:20])}" + (f" …等 {len(names)} 个" if len(names) > 20 else ""))
    if held_invalid:
        print(f"- 暂缓·校验 error: {len(held_invalid)}")
    if held_failed:
        print(f"- 转换失败: {len(held_failed)}")
    total_entries = len(registered) + len(pre_existing)
    print(f"- 注册表对账: {registry_dir} 现有 {total_entries} 个条目"
          f"（本次登记 {len(registered)}，此前已有 {len(pre_existing)}；"
          f"已排除 marketplace.orig）")
    if missing:
        print(f"  警告：以下 {len(missing)} 个插件登记成功但注册表条目缺失: {', '.join(missing)}")
    links = [r for r in registered if r.get("link")]
    if links:
        print(f"- 插件链接: 共 {len(links)} 个（完整清单在 registration-report.json 的 "
              f"registered[].link）；示例（最多 5 个，最终回复从中选用、不要自己猜名字）:")
        for r in links[:5]:
            print(f"  - [{r['name']}]({r['link']})")
        print("  引导用户到「个人」页签点 ＋ 安装（免重启）")
    else:
        print("- 插件链接: 未取得 link 字段（可在注册表条目或重登记输出中获取）")
    print(f"报告（人读，登记结果已填入）: {md_path}")


def main():
    ap = argparse.ArgumentParser(
        description="convert_plugin_repo.py 产物的批量登记：按 conversion-report.json 的 "
                    "registration_plan 登记 registerable 桶，自动分流暂缓项，"
                    "结束后与注册表对账并写 registration-report.json。")
    ap.add_argument("market_dir",
                    help="convert 的产物目录（含 conversion-report.json，默认 <share>/plugin-sources/<market>/）")
    ap.add_argument("--share-dir",
                    help="daimon-share 目录（默认 $KIMI_SHARE_DIR > macOS 客户端默认 > ~/.kimi）")
    ap.add_argument("--market", default=None,
                    help="目标市场名（缺省：报告 market 字段 > 目录名 > personal）")
    ap.add_argument("--also", default="",
                    help="逗号分隔的插件名：把暂缓桶里用户已审阅确认的插件一并登记")
    ap.add_argument("--daimon-bin", default=None,
                    help="kimi-daimon 二进制路径（默认读 $DAIMON_RUNTIME_BINARY_PATH）")
    ap.add_argument("--node", help="node 二进制路径（默认从 kimi-daimon 同目录/PATH 找）")
    ap.add_argument("--skip-validate", action="store_true",
                    help="跳过逐插件 validate（convert 已校验过时可加速；默认仍逐个校验）")
    ap.add_argument("--dry-run", action="store_true",
                    help="只打印登记计划，不实际登记")
    a = ap.parse_args()

    market_dir = str(Path(a.market_dir).expanduser().resolve())
    report, plan, dirs = load_plan(market_dir)
    market = resolve_market(market_dir, report, a.market)
    share_dir = str(Path(a.share_dir).expanduser()) if a.share_dir else str(pc.resolve_share_dir())

    targets = list(plan.get("registerable") or [])
    also = [n.strip() for n in str(a.also or "").split(",") if n.strip()]
    held = {k: plan.get(k) or [] for k in
            ("hold_hooks_or_setup", "hold_deps_unavailable", "hold_validate_errors", "failed")}
    if also:
        held_names = {h["name"] for names in held.values() for h in names}
        unknown = [n for n in also if n not in held_names and n not in targets]
        if unknown:
            sys.exit(f"错误：--also 里的名字不在登记计划中: {', '.join(unknown)}"
                     f"（核对 conversion-report.json，名字按报告里的 kimi_name 填）")
        targets += [n for n in also if n not in targets]
        for k in held:
            held[k] = [h for h in held[k] if h["name"] not in also]

    print(f"登记计划: 目标 {len(targets)} 个（registerable {len(plan.get('registerable') or [])}"
          + (f" + --also {len(also)}" if also else "") + "），"
          f"暂缓·hooks/setup.sh {len(held['hold_hooks_or_setup'])}，"
          f"暂缓·依赖不可用 {len(held['hold_deps_unavailable'])}，"
          f"暂缓·校验 error {len(held['hold_validate_errors'])}，"
          f"转换失败 {len(held['failed'])}")
    print(f"市场: {market}；share 目录: {share_dir}")
    if a.dry_run:
        for n in targets:
            print(f"  [dry-run] 将登记: {n}")
        return

    registered, failed_reg = [], []
    total = len(targets)
    try:
        for i, name in enumerate(targets, 1):
            plugin_dir = dirs.get(name) or os.path.join(market_dir, name)
            if not os.path.isfile(os.path.join(plugin_dir, "kimi.plugin.json")):
                failed_reg.append({"name": name,
                                   "error": f"插件目录缺 kimi.plugin.json: {plugin_dir}"})
                print(f"  [{i}/{total}] 失败: {name}: 缺 kimi.plugin.json")
                continue
            ok, link, error = register_one(
                plugin_dir, share_dir, market, daimon_bin=a.daimon_bin,
                node_bin=a.node, skip_validate=a.skip_validate)
            if ok:
                entry = {"name": name, "link": link}
                if name in also:
                    entry["from_hold"] = True
                registered.append(entry)
            else:
                failed_reg.append({"name": name, "error": error})
                print(f"  [{i}/{total}] 失败: {name}: {error}")
            if i % 20 == 0 or i == total:
                print(f"  进度 [{i}/{total}] 成功 {len(registered)}，失败 {len(failed_reg)}")
    except KeyboardInterrupt:
        print("\n中断：已登记部分仍会写入报告，重跑本命令可继续（重复登记幂等覆盖）。")

    # 对账：注册表目录只数 <id>.json（marketplace.orig 无 .json 后缀，天然排除）。
    registry_dir = Path(share_dir) / "daimon" / "plugin-market" / market
    entries = {p.stem for p in registry_dir.glob("*.json")} if registry_dir.is_dir() else set()
    registered_names = {r["name"] for r in registered}
    missing = sorted(registered_names - entries)
    pre_existing = sorted(entries - registered_names)

    report_doc = {
        "market": market, "share_dir": share_dir, "registry_dir": str(registry_dir),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "targets": total,
        "registered": registered,
        "failed": failed_reg,
        "held": held,
        "reconciliation": {
            "registry_entries": len(entries),
            "registered_this_run": len(registered),
            "pre_existing": len(pre_existing),
            "missing_entries": missing,
        },
    }
    report_path = os.path.join(market_dir, REPORT_NAME)
    pc.write_json(report_path, report_doc, force=True)

    # 整体重写人读报告 plugin-builder-report.md（转换数据 + 本次登记结果填实
    # 「登记结果」段落）；json 与 marketplace.orig 是机器合同/快照，不对人报告。
    md_path = os.path.join(market_dir, cpr.REPORT_MD_NAME)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(cpr.render_plugin_builder_report(report, report_doc))

    print_summary(market, registry_dir, registered, failed_reg, held,
                  pre_existing, missing, md_path)


if __name__ == "__main__":
    main()
