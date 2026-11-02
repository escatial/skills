---
name: autoglm-stock-analysis
description: 股票分析技能（AutoGLM 版）。当用户提到任何股票、证券、基金、市场行情分析需求时必须使用此技能，包括：分析某只股票、研究公司基本面、看K线图走势、查财报数据、评估买入卖出时机、对比多只股票、分析行业板块、解读财经新闻对股价影响、用户发来图表截图等。只要涉及股票投资分析的任何问题都应触发此技能。
---

# autoglm-stock-analysis

利用三个 Python 脚本实现股票信息采集与图表分析，输出结构化研究报告。

---

## 工具调用方式

### 1. 搜索 — `websearch.py`

```bash
python websearch.py "搜索词"
```

返回 JSON，关键字段：`result[].title` / `result[].snippet` / `result[].url`

**示例：**
```bash
python websearch.py "贵州茅台 2024年报 业绩"
python websearch.py "AAPL 最新财报 营收"
python websearch.py "新能源汽车板块 今日行情"
```

---

### 2. 打开网页 — `open-link.py`

```bash
python open-link.py "https://example.com"
```

返回 JSON，关键字段：`content` 或 `text`（页面正文）

**推荐数据源：**

| 场景 | URL 示例 |
|------|---------|
| A股行情（东方财富） | `https://quote.eastmoney.com/sh600519.html` |
| 雪球股票页 | `https://xueqiu.com/S/SH600519` |
| 港股（雪球） | `https://xueqiu.com/S/00700` |
| 美股（Yahoo Finance） | `https://finance.yahoo.com/quote/AAPL` |
| 历史财务数据 | `https://www.macrotrends.net/stocks/charts/AAPL/apple/revenue` |
| A股公告（巨潮） | `https://www.cninfo.com.cn` |

> A股代码规则：沪市 `SH` 前缀，深市 `SZ` 前缀，如 `SH600519`（茅台）

---

### 3. 图片识别 — `image-recognition.py`

```bash
python image-recognition.py "<image_url>" "<prompt>"
```

`image_url` 参数支持两种格式：
- **公网 URL**：`"https://example.com/chart.png"`
- **base64 字符串**：`"data:image/png;base64,iVBORw0KGgo..."` 或直接裸 base64 数据

返回 JSON，关键字段：`result` 或 `content`

**K线图分析专用 prompt：**
```
请分析这张K线图：
1) 当前趋势（上升/下降/震荡）
2) 关键支撑位和压力位价格
3) 均线（MA5/20/60）排列状态
4) 成交量特征与量价关系
5) MACD/RSI/KDJ 等技术指标信号
6) K线形态（头肩顶底、双顶底、旗形、三角形等）
7) 综合判断近期走势方向
```

**财务图表分析 prompt：**
```
请提取图表中的关键数据：营收/利润趋势、同比增速、关键财务指标数值，并分析趋势变化
```

---

## 分析流程

### 第一步：判断分析类型

| 用户意图 | 执行策略 |
|---------|---------|
| 快速行情查询 | 1次 websearch，直接回答 |
| 基本面分析 | websearch × 2~3 + open-link 财报页 |
| 技术面分析（有图） | image-recognition 读图 + websearch 补充新闻 |
| 技术面分析（无图） | websearch K线数据 + open-link 行情页 |
| 综合研究报告 | 全流程（见下） |
| 多股对比 | 每股各执行 websearch × 1，制作对比表 |

---

### 第二步：信息采集

**基础搜索（每次分析必做）：**
```bash
python websearch.py "[股票名] 今日股价 行情"
python websearch.py "[股票名] 最新财报 业绩 营收"
python websearch.py "[股票名] 近期新闻 利好利空"
```

**深度数据（综合报告时补充）：**
```bash
python open-link.py "https://xueqiu.com/S/SH600519"
python open-link.py "https://finance.yahoo.com/quote/AAPL/financials"
python websearch.py "[股票名] 分析师评级 目标价 2024"
```

**图片分析（用户提供图片时）：如果没有URL可以使用autoglm-file-upload skill上传文件获取URL**
```bash
# 公网 URL
python image-recognition.py "https://..." "请分析这张K线图的趋势、关键价位和技术指标信号"
```

---

### 第三步：输出报告

```markdown
## [股票名称]（[代码]）分析报告
> 数据时间：[当前日期]

### 📊 基本信息
- **当前价格**：XX 元 | 涨跌幅：+X.XX%
- **市值**：XXX 亿 | **PE**：XX | **PB**：XX
- **所属行业**：XX | **概念板块**：XX

### 🏢 基本面分析
- **核心业务**：...
- **最新财务**：营收 XX 亿（同比 +XX%）/ 净利润 XX 亿（同比 +XX%）/ 毛利率 XX%
- **竞争优势**：...
- **近期事件**：...

### 📈 技术面分析
- **趋势判断**：上升 / 下降 / 震荡
- **关键价位**：支撑位 XX 元 / 压力位 XX 元
- **均线状态**：多头排列 / 空头排列 / 纠缠
- **量价关系**：...
- **指标信号**：MACD ... / RSI ... / KDJ ...

### 📰 市场情绪
- 最新新闻：...
- 机构观点：...

### ⚖️ 风险提示
1. ...
2. ...

### 💡 综合评估
| 维度 | 评分 | 说明 |
|------|------|------|
| 基本面 | ⭐⭐⭐⭐ | ... |
| 技术面 | ⭐⭐⭐ | ... |
| 市场情绪 | ⭐⭐⭐ | ... |

**适合投资者类型**：价值型 / 成长型 / 短线

---
⚠️ 免责声明：本分析基于公开信息整理，仅供参考，不构成投资建议。股市有风险，投资需谨慎。
```

---

## 特殊场景

### 场景A：用户发来K线截图
图片来源：
- 对话中的图片公网 URL → `python image-recognition.py "https://..." "prompt"`
- 用户提供 base64 数据 → `python image-recognition.py "data:image/png;base64,..." "prompt"`

分析后再执行 websearch 补充近期基本面新闻，合并输出。

### 场景B：对比多只股票
```bash
python websearch.py "贵州茅台 PE PB ROE 2024"
python websearch.py "五粮液 PE PB ROE 2024"
```
输出对比表格，维度：估值（PE/PB）、成长性（营收/利润增速）、盈利质量（ROE/毛利率）

### 场景C：行业板块分析
```bash
python websearch.py "[行业名] 板块 景气度 2024"
python websearch.py "[行业名] 龙头股 排名"
```
判断行业景气周期位置，列出 3~5 只代表标的简要对比

### 场景D：快速问答
仅 1 次 websearch，给出 3~5 句核心判断 + 免责声明，无需完整报告格式。

---

## 注意事项

1. **脚本路径**：所有脚本与 SKILL.md 同级，直接 `python websearch.py` 调用
2. **JSON 解析**：脚本输出为 JSON，提取 `result`、`content`、`text` 字段使用
3. **搜索时效**：搜索词加上年份（如"2024"）确保结果最新
4. **open-link 失败**：若返回空，改用 websearch 搜索该页面摘要
5. **免责声明**：每次报告末尾必须包含投资风险声明