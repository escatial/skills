---
name: amos-sem-workflow
description: AMOS 结构方程建模（SEM）一条龙工作流助手，覆盖从原始问卷数据到论文成文的完整链路：数据清洗（缺失值、异常值、反向计分、Mahalanobis 距离）→ 进入 AMOS 前的"达标预检验"（样本量与 N:p 比、正态性偏度峰度、Little's MCAR、Harman 单因子共同方法偏差、Cronbach's α、KMO 与 Bartlett、EFA、CR 组合信度、AVE 收敛效度、√AVE 与 HTMT 区分效度、VIF 多重共线性）→ AMOS 自动绘图（用 AmosGraphics Plugin 的 VB.NET 代码自动画 CFA/SEM 路径图，自动命名误差项与潜变量、自动画协方差）→ 自动分析（AmosEngine 脚本化建模与估计，免手动点击）→ 模型评估（χ²/df、CFI、TLI、IFI、RMSEA、SRMR、GFI 等拟合指标；修正指数 MI；模型比较）→ 中介与调节效应（Bootstrap 偏差校正置信区间、多群组分析、潜变量交互）→ 结果的 APA 格式文字撰写。触发词包括 AMOS、结构方程、SEM、验证性因子分析、CFA、路径分析、中介效应、调节效应、Bootstrap、拟合指标、模型修正、修正指数、MI、组合信度、AVE、区分效度、共同方法偏差、多群组、AmosEngine、Amos 插件、自动绘图、问卷数据分析。
---

# AMOS SEM 一条龙工作流

## 核心姿态

大多数人做 AMOS 的顺序是错的：**先画图跑模型，跑不出来再回头查数据。**

正确的顺序是——**在进 AMOS 之前，先做一遍"达标预检验"。**

数据不达标就进 AMOS，你会遇到：模型不收敛、载荷是负的、拟合指标怎么修都不过、Heywood case（负误差方差）。然后你就会开始"修正指数疯狂加路径"——这是审稿人一眼就能看出来的数据操纵。

**这个 skill 的第一原则：把关口前移。**

不要承诺"跑一遍就能发表"。不要用修正指数把模型硬拗到拟合。**拟合好但没有理论支撑的模型，一文不值。**

---

## 五个阶段

```
① 数据清洗
      ↓
② 达标预检验  ← 关键关口。不达标不许进 AMOS
      ↓
③ AMOS 自动绘图（Plugin）+ 自动分析（AmosEngine）
      ↓
④ 模型评估与修正 · 中介/调节/多群组
      ↓
⑤ APA 格式结果撰写
```

---

## ① 数据清洗

| 步骤 | 做什么 | 判定 |
|---|---|---|
| 反向计分 | 先做，别忘了 | 反向题必须转换后再算 α |
| 缺失值 | 检查缺失比例与模式 | < 5% 可处理；做 **Little's MCAR 检验** |
| 单变量异常 | 标准化后 \|z\| > 3.29 | 逐个核查，不要无脑删 |
| 多变量异常 | **Mahalanobis D²**，p < .001 | 删除需说明理由与数量 |
| 无效样本 | 规律作答、极短作答时间、全选同一选项 | 事先定规则 |

> 详见 `references/01-data-cleaning.md`

---

## ② 达标预检验（进 AMOS 前必过的关）

**这是整个工作流最有价值的一步。** 逐项检查，任何一项不达标 → **回去修数据/修量表，不要进 AMOS。**

| # | 检验 | 常用标准 | 不达标怎么办 |
|---|---|---|---|
| 1 | **样本量** | N ≥ 200；**N : 待估参数 ≥ 5:1（理想 10:1）** | 继续收数据 / 简化模型 |
| 2 | **正态性** | \|偏度\| < 2~3，\|峰度\| < 7~8 | 严重偏离 → **Bootstrap ML** 或稳健估计 |
| 3 | **共同方法偏差** | Harman 单因子：第一因子 < 40% | 加 CLF 潜在共同方法因子检验 |
| 4 | **信度** | Cronbach's α ≥ .70 | 删题（看 CITC < .30） |
| 5 | **EFA 适合性** | **KMO ≥ .70**，Bartlett **p < .001** | 不适合做因子分析 → 检查量表 |
| 6 | **收敛效度** | 标准化载荷 ≥ .50（最好 ≥ .70）；**CR ≥ .70**；**AVE ≥ .50** | 删低载荷题项 |
| 7 | **区分效度** | **√AVE > 该因子与其他因子的相关**；或 **HTMT < .85** | 合并因子 / 重新界定构念 |
| 8 | **多重共线性** | VIF < 5；因子间相关 < .85 | 合并或删除 |

> **关键认知**：CR 和 AVE 要在 **CFA 之后**用标准化载荷算，但载荷太低的题项在 EFA 阶段就该发现。
> **不要**把不达标的数据硬塞进 AMOS，然后用 MI 加路径去救——救不回来，还会被审稿人抓住。

> 详见 `references/02-readiness-checks.md`（含每个指标的公式与 SPSS/Python 操作）

---

## ③ AMOS 自动化

AMOS 支持 **.NET 编程接口**，有两条自动化路线：

### 路线 A：AmosEngine —— 脚本化建模与估计（不用画图）

```vb
Dim Sem As New AmosEngineLib.AmosEngine
Sem.TextOutput()
Sem.Standardized()          ' 标准化解
Sem.Smc()                   ' R²
Sem.Bootstrap(2000)         ' Bootstrap
Sem.ConfidenceBC(90)        ' 偏差校正置信区间（中介必备）

Sem.BeginGroup("data.sav")
Sem.AStructure("X1 = (1) F1 + (1) e1")
Sem.AStructure("X2 =     F1 + (1) e2")
Sem.AStructure("Y  =     F1 + (1) e3")
Sem.Dispose()
```

- 适合：**批量跑模型、可复现、写进论文附录**
- 语法核心：`AStructure("因变量 = 自变量 + 误差")`，`(1)` 表示固定载荷为 1

### 路线 B：Amos Graphics Plugin —— 自动绘制路径图

**这是"自动绘图"的实现方式。** AMOS 插件用 VB.NET 写，`pd` 对象即路径图。

已验证可用的核心 API：

| 方法 | 作用 |
|---|---|
| `pd.DiagramDrawUnobserved(x, y, w, h)` | 画一个潜变量（椭圆），返回 `PDElement` |
| `pd.DiagramDrawIndicatorVariable(F)` | 给潜变量 F **加一个观测指标 + 误差项 + 载荷路径**（一行搞定） |
| `pd.DiagramDrawUniqueVariable(E)` | 加误差/唯一变量 |
| `pd.DiagramDrawCovariance(A, B)` | 画双向箭头（因子间协方差） |
| `pd.PDElements` | 遍历全部图元 |
| `E.NameOrCaption` | 读写变量名（用于自动命名） |
| `E.IsUnobservedVariable` / `.IsUniqueVariable` / `.IsExogenousVariable` | 判断图元类型 |
| `pd.EditTouchUp(E)` / `pd.EditFitToPage()` / `pd.Refresh()` | 自动排版 |

**一个能跑的 CFA 自动绘图插件骨架**：

```vb
Imports Amos
<System.ComponentModel.Composition.Export(GetType(Amos.IPlugin))>
Public Class CPlugin
    Implements Amos.IPlugin

    Public Function MainSub() As Integer Implements Amos.IPlugin.MainSub
        pd.ViewPathDiagram()
        Dim F(3) As PDElement
        Dim i As Integer

        ' 画 3 个潜变量，每个带 4 个指标
        For i = 1 To 3
            F(i) = pd.DiagramDrawUnobserved(200 * i, 100, 60, 40)
            F(i).NameOrCaption = "F" & i
            pd.DiagramDrawIndicatorVariable(F(i))
            pd.DiagramDrawIndicatorVariable(F(i))
            pd.DiagramDrawIndicatorVariable(F(i))
            pd.DiagramDrawIndicatorVariable(F(i))
        Next

        ' 因子间两两画协方差
        For i = 1 To 3
            For j = i + 1 To 3
                pd.DiagramDrawCovariance(F(i), F(j))
            Next
        Next

        pd.EditFitToPage()
        pd.Refresh()
    End Function

    Public Function Name1() As String Implements Amos.IPlugin.Name
        Return "Auto CFA"
    End Function
    Public Function Description() As String Implements Amos.IPlugin.Description
        Return "Auto-draw a CFA path diagram"
    End Function
End Class
```

**安装插件**：编译为 DLL → 放入 AMOS 的 `Plugins` 目录 → 在 AMOS 中 `Plugins` 菜单调用。

> 完整可用模板（CFA 生成器、误差项自动命名、结构模型自动连线）见 `templates/`
> 详见 `references/03-amos-automation.md`

---

## ④ 模型评估

### 拟合指标（报告这一组即可）

| 指标 | 可接受 | 良好 |
|---|---|---|
| **χ²/df** | < 5 | **< 3** |
| **CFI** | ≥ .90 | **≥ .95** |
| **TLI** (NNFI) | ≥ .90 | ≥ .95 |
| **RMSEA** | ≤ .08 | **≤ .06** |
| **SRMR** | ≤ .08 | ≤ .05 |
| GFI / AGFI | ≥ .90 / ≥ .85 | 受样本量影响大，可不作为主要依据 |

- **χ² 本身几乎必然显著**（样本大就显著），不要因为 p < .05 就说模型不好。
- **别只报好看的那几个**。CFI + TLI + RMSEA + SRMR + χ²/df 是标配组合。

### 修正指数 MI —— 最容易翻车的地方

**规则：只在有理论依据时使用，且只加"同一因子内部的误差相关"。**

- ❌ 不要跨因子加误差相关（等于承认构念不干净）
- ❌ 不要为了拟合而反复加路径（这是数据操纵）
- ✅ 每加一条，都要能说出"为什么这两个题项的误差会相关"（如题项措辞相似、位置相邻）
- ✅ 在论文中**如实报告**你做了哪些修正、为什么

> 一个拟合完美但靠十几条 MI 拗出来的模型，审稿人一眼看穿。

### 中介效应

**必须用 Bootstrap**，不要用 Sobel 检验（已过时）。

- Bootstrap 抽样 **≥ 2000**（推荐 5000）
- 报告 **偏差校正置信区间（Bias-corrected CI）**
- **判定：95% CI 不包含 0 → 中介效应显著**
- 同时报告：总效应、直接效应、间接效应及其 CI

### 调节效应 / 多群组

- **多群组分析**：先做测量不变性检验（形态 → 弱 → 强 → 严格），ΔCFI < .01 视为不变性成立
- **潜变量交互**：可用乘积指标法，或改用 PLS-SEM / Mplus

> 详见 `references/04-model-fit-analysis.md`

---

## ⑤ 结果撰写

结果段落必须包含：
1. 数据清洗与样本描述
2. 达标预检验的全部结果（信度、效度、共同方法偏差）
3. 测量模型（CFA）：拟合指标 + 标准化载荷 + CR + AVE + 区分效度表
4. 结构模型：拟合指标 + 路径系数（β、S.E.、C.R.、p）+ R²
5. 中介/调节：Bootstrap CI 表
6. 修正情况（如有）：改了什么、为什么

> 可套用的 APA 段落模板见 `references/05-write-up.md`

---

## 全流程检查清单

- [ ] 反向计分已完成
- [ ] 缺失值处理并报告（含 Little's MCAR）
- [ ] Mahalanobis 多变量异常值已检查
- [ ] 样本量满足 N:p ≥ 5:1
- [ ] 偏度峰度在可接受范围（否则用 Bootstrap ML）
- [ ] Harman 单因子 < 40%
- [ ] 各维度 α ≥ .70
- [ ] KMO ≥ .70，Bartlett 显著
- [ ] 标准化载荷 ≥ .50，CR ≥ .70，AVE ≥ .50
- [ ] √AVE > 因子间相关（或 HTMT < .85）
- [ ] CFA 拟合达标后，才做结构模型
- [ ] 中介用 Bootstrap ≥ 2000 + 偏差校正 CI
- [ ] MI 修正有理论依据且如实报告
- [ ] 拟合指标报告完整组合（不挑好看的）

---

## 边界与诚信

- 所有阈值都是**领域经验标准**，不是铁律。使用时应引用文献（见 `references/06-bibliography.md`），并结合你的领域惯例。
- **不得**为了拟合而反复加 MI 路径、删题、删样本。
- **不得**只报告好看的拟合指标。
- **不得**在多个模型中挑选结果最好的那个报告，而不说明你试过多个。
- 数据不达标时，正确的做法是**回去修数据或修理论**，不是修模型。
