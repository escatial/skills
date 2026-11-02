' =====================================================================
'  AMOS 自动绘图插件：Auto CFA
'  按「因子 × 指标数」自动画出完整 CFA 路径图
'    - 自动画潜变量（椭圆）
'    - 自动画观测指标 + 误差项 + 载荷路径
'    - 自动给误差项编号 e1, e2, e3 ...
'    - 自动在因子间两两画协方差
'    - 自动排版
'
'  【使用方法】
'  1. 用 Visual Studio 新建 VB.NET「类库(Class Library)」项目
'  2. 添加引用：AMOS 安装目录下的 Amos.exe（或 AmosGraphics 相关程序集）
'     以及 System.ComponentModel.Composition
'  3. 把本文件内容粘贴进去，改下面的「模型配置区」
'  4. 编译成 DLL
'  5. 把 DLL 复制到 AMOS 安装目录的 Plugins 文件夹
'  6. 重启 AMOS → 菜单 Plugins → Auto CFA
' =====================================================================

Imports Amos
Imports System.Collections.Generic

<System.ComponentModel.Composition.Export(GetType(Amos.IPlugin))>
Public Class CPlugin
    Implements Amos.IPlugin

    ' ============ 模型配置区：改这里 ============

    ' 因子名
    Private FactorNames() As String = {"F1", "F2", "F3"}

    ' 每个因子对应的观测题项名（顺序与 FactorNames 对应）
    ' 留空 {} 则只画方框不命名，之后在 AMOS 里手动拖变量名
    Private Items()() As String = New String()() {
        New String() {"A1", "A2", "A3", "A4"},
        New String() {"B1", "B2", "B3", "B4"},
        New String() {"C1", "C2", "C3"}
    }

    ' 是否在因子间两两画协方差（CFA 通常为 True）
    Private DrawCovariances As Boolean = True

    ' 排版参数
    Private StartX As Integer = 400      ' 潜变量横坐标
    Private StartY As Integer = 120      ' 第一个潜变量纵坐标
    Private FactorGapY As Integer = 260  ' 潜变量之间的纵向间距
    Private OvalW As Integer = 80
    Private OvalH As Integer = 50

    ' ==========================================

    Public Function MainSub() As Integer Implements Amos.IPlugin.MainSub
        pd.ViewPathDiagram()
        pd.DisplayInputPD()

        Dim nF As Integer = FactorNames.Length
        Dim F(nF - 1) As PDElement
        Dim i As Integer, j As Integer, k As Integer

        ' ---- 1. 画潜变量 + 指标 ----
        For i = 0 To nF - 1
            F(i) = pd.DiagramDrawUnobserved(StartX, StartY + i * FactorGapY, OvalW, OvalH)
            F(i).NameOrCaption = FactorNames(i)

            Dim nItem As Integer = Items(i).Length
            For k = 1 To nItem
                ' 这一步会自动画出：观测方框 + 误差圆 + 载荷箭头
                pd.DiagramDrawIndicatorVariable(F(i))
            Next
        Next

        ' ---- 2. 给观测指标命名 ----
        NameObservedVariables()

        ' ---- 3. 给误差项自动编号 ----
        NameErrorTerms()

        ' ---- 4. 因子间协方差 ----
        If DrawCovariances Then
            For i = 0 To nF - 1
                For j = i + 1 To nF - 1
                    pd.DiagramDrawCovariance(F(i), F(j))
                Next
            Next
        End If

        ' ---- 5. 排版 ----
        For i = 0 To nF - 1
            pd.EditTouchUp(F(i))
        Next
        pd.EditFitToPage()
        pd.Refresh()

        Return 0
    End Function


    ' 按绘制顺序给观测方框命名
    Private Sub NameObservedVariables()
        Dim flat As New List(Of String)
        For i As Integer = 0 To Items.Length - 1
            For k As Integer = 0 To Items(i).Length - 1
                flat.Add(Items(i)(k))
            Next
        Next

        Dim idx As Integer = 0
        Dim E As PDElement
        For Each E In pd.PDElements
            If E.IsObservedVariable AndAlso E.NameOrCaption = "" Then
                If idx < flat.Count Then
                    E.Undraw()
                    E.NameOrCaption = flat(idx)
                    E.Draw()
                    idx += 1
                End If
            End If
        Next
    End Sub


    ' 给所有未命名的误差项编号 e1, e2, ...
    Private Sub NameErrorTerms()
        Dim E As PDElement
        Dim c As Integer = 0
        For Each E In pd.PDElements
            If E.NameOrCaption = "" _
               AndAlso E.IsUnobservedVariable _
               AndAlso E.IsUniqueVariable Then
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
        Return "自动绘制验证性因子分析路径图（含误差项命名与因子间协方差）"
    End Function

End Class
