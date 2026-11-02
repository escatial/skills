# AMOS 自动化：自动绘图 + 脚本化分析

AMOS 提供 **.NET 编程接口**，有两条自动化路线。两条路线解决的问题不同，通常**配合使用**。

| | AmosEngine | Amos Graphics Plugin |
|---|---|---|
| 干什么 | **不画图**，直接跑模型出结果 | **自动画路径图** |
| 语言 | VB.NET / C# 控制台程序 | VB.NET 类库（DLL 插件） |
| 适合 | 批量建模、可复现、写进附录 | 生成论文里的路径图 |
| 输出 | 文本/表格结果 | .amw 路径图文件 |

---

## 路线 A：AmosEngine —— 脚本化建模与估计

### 基本骨架

```vb
Module MainModule
    Sub Main()
        Dim Sem As New AmosEngineLib.AmosEngine

        Sem.TextOutput()            ' 输出文本结果
        Sem.Standardized()          ' 标准化解（必开）
        Sem.Smc()                   ' 输出 R²
        Sem.FitAllModels()

        Sem.BeginGroup("D:\data\survey.sav")

        ' 测量模型：观测变量 = 潜变量 + 误差
        ' (1) 表示把该路径固定为 1（标定潜变量的量纲）
        Sem.AStructure("A1 = (1) F1 + (1) e1")
        Sem.AStructure("A2 =     F1 + (1) e2")
        Sem.AStructure("A3 =     F1 + (1) e3")

        Sem.AStructure("B1 = (1) F2 + (1) e4")
        Sem.AStructure("B2 =     F2 + (1) e5")
        Sem.AStructure("B3 =     F2 + (1) e6")

        Sem.AStructure("C1 = (1) F3 + (1) e7")
        Sem.AStructure("C2 =     F3 + (1) e8")
        Sem.AStructure("C3 =     F3 + (1) e9")

        ' 结构模型：F1 → F2 → F3（中介）
        Sem.AStructure("F2 = F1 + (1) d1")
        Sem.AStructure("F3 = F1 + F2 + (1) d2")

        Sem.Dispose()
    End Sub
End Module
```

### 中介效应必备设置

```vb
Sem.Bootstrap(2000)        ' Bootstrap 抽样次数（≥2000，推荐5000）
Sem.ConfidenceBC(95)       ' 偏差校正置信区间 Bias-Corrected CI
Sem.Standardized()
```

### 常用方法速查

| 方法 | 作用 |
|---|---|
| `Sem.TextOutput()` | 输出文本结果 |
| `Sem.Standardized()` | 标准化估计值 |
| `Sem.Smc()` | 多元相关平方（R²） |
| `Sem.Mods(4)` | 输出修正指数 MI（阈值 4） |
| `Sem.Bootstrap(n)` | Bootstrap |
| `Sem.ConfidenceBC(95)` | 偏差校正 CI |
| `Sem.BeginGroup(file, sheet)` | 载入数据（支持 .sav/.xls） |
| `Sem.AStructure("...")` | 设定一条结构方程 |
| `Sem.GroupName("...")` | 多群组命名 |
| `Sem.Model("名称", "约束")` | 定义竞争模型 |
| `Sem.Dispose()` | 释放（必须调用） |

### AStructure 语法要点

```
"因变量 = 自变量 + 误差项"

(1) X       固定系数为 1
(a) X       给该路径命名为 a（用于设定等式约束）
<---        也可写作 "F1 <--- X"（等价）
```

---

## 路线 B：Amos Graphics Plugin —— 自动绘图

### 插件结构（VB.NET，编译成 DLL）

```vb
Imports Amos
<System.ComponentModel.Composition.Export(GetType(Amos.IPlugin))>
Public Class CPlugin
    Implements Amos.IPlugin

    Public Function MainSub() As Integer Implements Amos.IPlugin.MainSub
        ' 你的绘图代码
    End Function

    Public Function Name1() As String Implements Amos.IPlugin.Name
        Return "插件显示名"
    End Function

    Public Function Description() As String Implements Amos.IPlugin.Description
        Return "插件说明"
    End Function
End Class
```

**安装**：编译为 DLL → 复制到 AMOS 安装目录的 `Plugins` 文件夹 → 重启 AMOS → 在 `Plugins` 菜单中出现。

### 核心 API（已验证）

**`pd`** 是全局路径图对象。

#### 绘制

| 方法 | 作用 |
|---|---|
| `pd.DiagramDrawUnobserved(x, y, w, h)` | 画潜变量（椭圆），**返回 PDElement** |
| `pd.DiagramDrawIndicatorVariable(F)` | 给潜变量 F 加**一个指标 + 误差项 + 载荷路径**（一步完成，最有用） |
| `pd.DiagramDrawUniqueVariable(E)` | 加误差/唯一变量 |
| `pd.DiagramDrawCovariance(A, B)` | 画双向箭头（协方差） |
| `pd.FileNew(...)` | 新建路径图 |
| `pd.SetDataFile(...)` | 绑定数据文件 |

#### 遍历与操作图元

```vb
Dim E As PDElement
For Each E In pd.PDElements
    If E.IsUnobservedVariable Then ...
    If E.IsUniqueVariable Then ...        ' 误差项
    If E.IsExogenousVariable Then ...     ' 外生变量
    E.NameOrCaption = "F1"                ' 读写变量名
    E.Selected = True
    E.Draw() / E.Undraw()
Next
```

#### 排版

| 方法 | 作用 |
|---|---|
| `pd.EditTouchUp(E)` | 自动整理某元素的连线 |
| `pd.EditFitToPage()` | 缩放至适合页面 |
| `pd.Refresh()` | 刷新显示 |
| `pd.ViewPathDiagram()` / `pd.DisplayInputPD()` | 切换视图 |
| `pd.EditShapeOfObject()` | 调整形状（如箭头曲率） |
| `pd.UndoToHere()` / `pd.UndoResume()` | 撤销管理（插件里包一层，出错可回滚） |

---

### 模板 1：自动绘制 CFA

按「因子数 × 每因子指标数」自动画出完整 CFA（含误差项、载荷、因子间协方差）。

```vb
Imports Amos
<System.ComponentModel.Composition.Export(GetType(Amos.IPlugin))>
Public Class CPlugin
    Implements Amos.IPlugin

    ' ==== 在这里改你的模型 ====
    Private FactorNames() As String = {"F1", "F2", "F3"}
    Private NIndicators() As Integer = {4, 4, 3}   ' 每个因子的指标数
    ' =========================

    Public Function MainSub() As Integer Implements Amos.IPlugin.MainSub
        pd.ViewPathDiagram()
        pd.DisplayInputPD()

        Dim nF As Integer = FactorNames.Length
        Dim F(nF - 1) As PDElement
        Dim i As Integer, j As Integer, k As Integer

        ' 画潜变量 + 指标
        For i = 0 To nF - 1
            F(i) = pd.DiagramDrawUnobserved(150, 100 + i * 220, 70, 45)
            F(i).NameOrCaption = FactorNames(i)
            For k = 1 To NIndicators(i)
                pd.DiagramDrawIndicatorVariable(F(i))
            Next
        Next

        ' 因子间两两协方差
        For i = 0 To nF - 1
            For j = i + 1 To nF - 1
                pd.DiagramDrawCovariance(F(i), F(j))
            Next
        Next

        ' 自动命名误差项 e1, e2, ...
        NameErrors()

        For i = 0 To nF - 1
            pd.EditTouchUp(F(i))
        Next
        pd.EditFitToPage()
        pd.Refresh()
    End Function

    ' 给所有未命名的误差项自动编号
    Private Sub NameErrors()
        Dim E As PDElement
        Dim c As Integer = 0
        For Each E In pd.PDElements
            If E.NameOrCaption = "" AndAlso E.IsUnobservedVariable AndAlso E.IsUniqueVariable Then
                c += 1
                E.Undraw()
                E.NameOrCaption = "e" & CStr(c)
                E.Draw()
            End If
        Next
    End Sub

    Public Function Name1() As String Implements Amos.IPlugin.Name
        Return "Auto CFA"
    End Function
    Public Function Description() As String Implements Amos.IPlugin.Description
        Return "Auto-draw a CFA with covariances and named errors"
    End Function
End Class
```

> **注意**：`DiagramDrawIndicatorVariable` 画出的指标默认没有名字，需要在 AMOS 里把观测变量名拖到方框上，或用 `E.NameOrCaption` 逐个赋值（遍历时按顺序对应你的题项名）。

---

### 模板 2：给选中的外生变量两两画协方差

（改写自 AMOS 官方 Draw Covariances 插件的逻辑）

```vb
Private Sub DrawCovAmongSelected()
    Dim x As PDElement
    Dim sel As New List(Of PDElement)

    For Each x In pd.PDElements
        If x.Selected AndAlso x.IsExogenousVariable Then sel.Add(x)
    Next

    For i As Integer = 0 To sel.Count - 1
        For j As Integer = i + 1 To sel.Count - 1
            pd.DiagramDrawCovariance(sel(i), sel(j))
        Next
    Next

    If sel.Count > 0 Then pd.EditTouchUp(sel(0))
End Sub
```

---

## 实务建议：两条路线怎么配合

推荐工作流：

1. **用 AmosEngine 跑分析**（脚本化、可复现、便于批量比较竞争模型）
2. **用 Plugin 自动画图**（生成论文用的路径图）
3. 把 AmosEngine 脚本**附在论文附录或补充材料**里 → 可复现性加分

### 为什么不全用 GUI 手点

- 手点 30 个指标的 CFA，画错一条线找一小时
- 改模型要重画
- **不可复现**：审稿人问"你到底跑了什么模型"，你说不清

---

## 常见报错

| 现象 | 原因 | 解决 |
|---|---|---|
| 插件不出现在菜单 | DLL 没放对目录 / 未编译成 .NET 类库 | 检查 `Plugins` 目录；目标框架要匹配 AMOS |
| `pd` 未定义 | 少了 `Imports Amos` | 加上 |
| 模型不识别 | 变量名与数据文件列名不一致 | 名字必须**完全一致**（含大小写、空格） |
| 不收敛 | 数据不达标 / 模型设定错误 / 样本太小 | **回到达标预检验**，不要靠加 MI 救 |
| 负误差方差（Heywood case） | 样本小、载荷接近 1、模型设定问题 | 检查数据；必要时固定该误差方差为一个小正数 |
