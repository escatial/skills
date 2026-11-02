' =====================================================================
'  AmosEngine 脚本化 SEM 分析（不用画图，直接出结果）
'
'  适合：批量跑模型、竞争模型比较、可复现（脚本可作为论文附录）
'
'  【使用方法】
'  1. Visual Studio 新建 VB.NET「控制台应用程序」
'  2. 添加引用：AMOS 安装目录下的 AmosEngineLib.dll
'  3. 改「配置区」，运行
' =====================================================================

Imports AmosEngineLib

Module MainModule

    Sub Main()

        ' ============ 配置区 ============
        Dim DataFile As String = "D:\data\survey.sav"
        Dim BootstrapN As Integer = 5000      ' 中介效应必须 ≥ 2000
        ' ================================

        Dim Sem As New AmosEngineLib.AmosEngine

        Try
            ' ---- 输出设置 ----
            Sem.TextOutput()
            Sem.Standardized()          ' 标准化解（必开）
            Sem.Smc()                   ' 输出 R²
            Sem.Mods(10)                ' 修正指数（阈值 10）
            Sem.FitAllModels()

            ' ---- 中介效应：Bootstrap + 偏差校正 CI ----
            Sem.Bootstrap(BootstrapN)
            Sem.ConfidenceBC(95)        ' Bias-Corrected 95% CI

            ' ---- 载入数据 ----
            Sem.BeginGroup(DataFile)

            ' =========== 测量模型 ===========
            ' 语法：观测变量 = 潜变量 + 误差
            ' (1) 表示把系数固定为 1（用于标定潜变量量纲，每个因子需要一个）

            ' 自变量 F1
            Sem.AStructure("A1 = (1) F1 + (1) e1")
            Sem.AStructure("A2 =     F1 + (1) e2")
            Sem.AStructure("A3 =     F1 + (1) e3")
            Sem.AStructure("A4 =     F1 + (1) e4")

            ' 中介变量 F2
            Sem.AStructure("B1 = (1) F2 + (1) e5")
            Sem.AStructure("B2 =     F2 + (1) e6")
            Sem.AStructure("B3 =     F2 + (1) e7")
            Sem.AStructure("B4 =     F2 + (1) e8")

            ' 因变量 F3
            Sem.AStructure("C1 = (1) F3 + (1) e9")
            Sem.AStructure("C2 =     F3 + (1) e10")
            Sem.AStructure("C3 =     F3 + (1) e11")

            ' =========== 结构模型 ===========
            ' 中介路径：F1 → F2 → F3，同时保留 F1 → F3 的直接路径
            ' (a)(b) 给路径命名，便于后续定义间接效应
            Sem.AStructure("F2 = (a) F1 + (1) d1")
            Sem.AStructure("F3 = (b) F2 + (c) F1 + (1) d2")

            Sem.Dispose()

            Console.WriteLine("分析完成。结果已输出。")

        Catch ex As Exception
            Console.WriteLine("出错：" & ex.Message)
            Sem.Dispose()
        End Try

        Console.ReadLine()
    End Sub

End Module


' =====================================================================
'  语法速查
' =====================================================================
'
'  Sem.AStructure("Y = X + (1) e")     Y 被 X 预测，误差 e 系数固定为 1
'  Sem.AStructure("Y = (1) F + (1) e") 载荷固定为 1（标定潜变量）
'  Sem.AStructure("Y = (a) X + (1) e") 把该路径命名为 a
'  Sem.AStructure("F1 <--> F2")        画协方差（双向）
'
'  多群组：
'    Sem.GroupName("Male")
'    Sem.BeginGroup(DataFile, "male_sheet")
'    ... AStructure ...
'    Sem.GroupName("Female")
'    Sem.BeginGroup(DataFile, "female_sheet")
'    ... AStructure ...
'
'  竞争模型：
'    Sem.Model("Full",       "")           ' 无约束
'    Sem.Model("Constrained","a = 0")      ' 约束 a 路径为 0
'
'  缺失值 FIML：
'    Sem.ModelMeansAndIntercepts()
'
' =====================================================================
'  间接效应的置信区间
' -----------------------------------------------------------------
'  AmosEngine 本身不直接给命名路径乘积的 CI。
'  在 Amos Graphics 中可用 "User-defined estimand"（Plugins → Custom
'  Estimands）自定义：
'
'      Dim indirect As Double
'      indirect = a * b
'      Estimand("Indirect") = indirect
'
'  配合 Bootstrap，即可得到间接效应的 Bias-Corrected CI。
'  多重中介时，为每条路径分别定义 estimand。
' =====================================================================
