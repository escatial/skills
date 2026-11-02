// web_inject_template.js — 网页模式（Web → Skill）注入脚本模板
//
// 用法：本文件是「模板」，不是可直接登记的插件内容。
// 生成插件时把它复制为 skills/<name>/scripts/<name>.js，并按真实抓包结果改写。
//
// 运行时：agent 读取该脚本，把 PARAMS 占位替换为用户参数后，
// 通过 InAppBrowser 工具的 evaluate action 注入到目标网站标签页执行。
// 脚本运行在页面上下文：fetch 自动携带该站登录 cookie，无需任何凭证。
//
// 性能约定（勿删，慢的根源是「步骤太多 × 每步 LLM 往返」和「脚本挂起等超时」）：
// - 每个 fetch 自带 8 秒 AbortController 超时，失败快速返回，绝不等平台 15s 兜底；
// - 循环 N 次的取数一律页面内并发（Promise.all / mapLimit），一次注入拿完，
//   绝不让 agent 逐条 navigate + read_page；
// - 只回紧凑字段，详情正文按 maxChars 截断，不把全文塞进结果；
// - 不读 document.cookie、不写 localStorage —— 不需要，也避免触碰凭证。

(async (PARAMS) => {
  // PARAMS 示例：{ query: "用户查询词", limit: 10, detailUrls: [...] }

  // 带超时的 fetch：单个请求 8 秒主动中止
  function fetchT(url, opts, ms) {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), ms || 8000);
    return fetch(url, Object.assign({}, opts || {}, { signal: ctrl.signal }))
      .finally(() => clearTimeout(timer));
  }
  // 限流并发：items 按 conc 个一批跑 worker（N 条数据一次注入拿完）
  async function mapLimit(items, conc, worker) {
    const out = new Array(items.length);
    let idx = 0;
    await Promise.all(new Array(Math.min(conc, items.length)).fill(0).map(async () => {
      while (idx < items.length) {
        const i = idx++;
        out[i] = await worker(items[i], i);
      }
    }));
    return out;
  }

  const { query, limit = 10 } = PARAMS;

  // TODO(生成时填写)：改成 network 抓包拿到的真实内部接口。
  // 必须来自真实 network detail / evaluate 验证，禁止凭印象编造。
  const url = `https://example.com/api/search?q=${encodeURIComponent(query)}&limit=${limit}`;

  const resp = await fetchT(url, {
    headers: { Accept: 'application/json' },
    credentials: 'include', // 同源请求默认带 cookie；跨源时显式声明
  });
  if (!resp.ok) {
    return { ok: false, status: resp.status, hint: '接口异常，可能登录已过期或接口已变更' };
  }

  const data = await resp.json();

  // TODO(生成时填写)：按真实响应结构裁剪字段，保持返回紧凑。
  const items = (data.results || []).slice(0, limit).map((it) => ({
    title: it.title,
    url: it.url,
  }));

  // 批量详情示例：如果后续需要 N 个条目的详情，在页面内并发抓，一次拿完——
  // const details = await mapLimit(PARAMS.detailUrls || [], 4, async (u) => {
  //   const r = await fetchT(u, { credentials: 'include' });
  //   const doc = new DOMParser().parseFromString(await r.text(), 'text/html');
  //   doc.querySelectorAll('script,style,noscript').forEach((n) => n.remove());
  //   return { url: u, text: (doc.body?.innerText || '').slice(0, PARAMS.maxChars || 1200) };
  // });

  return { ok: true, count: items.length, items };
})(/* agent 运行时在此处填入参数对象，例如：{"query":"rust","limit":10} */)
