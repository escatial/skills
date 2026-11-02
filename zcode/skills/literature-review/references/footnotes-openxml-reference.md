# OpenXML 脚注与交叉引用技术参考

本参考文件详解如何使用 OpenXML SDK（C#）生成**真实**的 Word 脚注与交叉引用，确保 `word/footnotes.xml` 中存在功能性链接。

---

## 一、核心原理

### 1.1 Word 脚注的 OpenXML 结构

Word 脚注由两部分组成：

| 部分 | 位置 | 作用 |
|------|------|------|
| **引用部分** | `word/document.xml` 正文 | 包含 `<w:footnoteReference>` 元素 |
| **定义部分** | `word/footnotes.xml` | 包含 `<w:footnote>` 元素及内容 |

两者通过 `w:id` 属性关联，Word 自动渲染为上标编号。

### 1.2 关系链

```
document.xml                          footnotes.xml
┌──────────────────────┐             ┌──────────────────────┐
│ <w:r>                │             │ <w:footnote w:id="1">│
│   <w:footnoteRef.../>│ ───── ID ──→│   <w:p>             │
│ </w:r>               │             │     <w:r>           │
└──────────────────────┘             │       <w:footnoteRef/>│
                                     │     </w:r>          │
                                     │     <w:r>           │
                                     │       <w:t>内容</w:t>│
                                     │     </w:r>          │
                                     │   </w:p>            │
                                     │ </w:footnote>       │
                                     └──────────────────────┘
```

> 增删脚注时，Word 自动重排编号（手动编号不会自动更新）。

---

## 二、核心代码模板

### 2.1 创建 FootnotesPart

```csharp
using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;

public class FootnoteBuilder
{
    private readonly MainDocumentPart _mainPart;
    private readonly FootnotesPart _footnotesPart;
    private int _nextFootnoteId = 2; // ID 0 和 1 是系统保留（separator/continuation）

    public FootnoteBuilder(MainDocumentPart mainPart)
    {
        _mainPart = mainPart;
        _footnotesPart = _mainPart.AddNewPart<FootnotesPart>();

        // 初始化默认脚注（separator 和 continuationSeparator）
        InitializeDefaultFootnotes();
    }

    private void InitializeDefaultFootnotes()
    {
        var footnotes = new Footnotes();

        // 必需的 system 脚注
        footnotes.AppendChild(new Footnote(
            new Paragraph(
                new ParagraphProperties(new SpacingBetweenLines { After = "0", Line = "240", LineRule = LineSpacingRuleValues.Auto }),
                new Run(new SeparatorMark())
            )
        ) { Type = FootnoteEndnoteValues.Separator, Id = -1 });

        footnotes.AppendChild(new Footnote(
            new Paragraph(
                new ParagraphProperties(new SpacingBetweenLines { After = "0", Line = "240", LineRule = LineSpacingRuleValues.Auto }),
                new Run(new ContinuationSeparatorMark())
            )
        ) { Type = FootnoteEndnoteValues.ContinuationSeparator, Id = 0 });

        _footnotesPart.Footnotes = footnotes;
        _footnotesPart.Footnotes.Save();
    }
}
```

### 2.2 添加自定义脚注

```csharp
public int AddFootnote(string footnoteText)
{
    int footnoteId = _nextFootnoteId++;

    // 构建脚注内容
    var footnote = new Footnote(
        new Paragraph(
            new ParagraphProperties(
                new ParagraphStyleId { Val = "FootnoteText" },
                new SpacingBetweenLines { After = "0", Line = "240", LineRule = LineSpacingRuleValues.Auto }
            ),
            // Word 自动编号标记（关键！）
            new Run(new RunProperties(new RunStyle { Val = "FootnoteReference" }), new FootnoteReferenceMark()),
            // 脚注内容（前导空格）
            new Run(new RunProperties(
                new RunFonts { Ascii = "Times New Roman", HighAnsi = "Times New Roman", EastAsia = "宋体" },
                new FontSize { Val = "18" }, // 六号 = 18 半磅
                new FontSizeComplexScript { Val = "18" }
            ), new Text(" " + footnoteText) { Space = SpaceProcessingModeValues.Preserve })
        )
    ) { Id = footnoteId };

    _footnotesPart.Footnotes.AppendChild(footnote);
    _footnotesPart.Footnotes.Save();

    return footnoteId;
}
```

### 2.3 在正文插入脚注引用

```csharp
public Run CreateFootnoteReferenceRun(int footnoteId)
{
    // ✅ 正确：使用 FootnoteReference 元素
    return new Run(
        new RunProperties(new RunStyle { Val = "FootnoteReference" }),
        new FootnoteReference { Id = footnoteId }
    );
}

// ❌ 错误：手动上标数字（禁止使用）
// public Run CreateFakeFootnoteRef(string number)
// {
//     var run = new Run(new Text(number));
//     run.RunProperties = new RunProperties(
//         new VerticalTextAlignment { Val = VerticalPositionValues.Superscript }
//     );
//     return run;
// }
```

### 2.4 完整调用示例

```csharp
public void BuildDocumentWithFootnotes(MainDocumentPart mainPart, string paragraphText, string footnoteText)
{
    var footnoteBuilder = new FootnoteBuilder(mainPart);
    int footnoteId = footnoteBuilder.AddFootnote(footnoteText);

    // 创建段落
    var para = new Paragraph(
        new Run(
            new RunProperties(
                new RunFonts { Ascii = "Times New Roman", HighAnsi = "Times New Roman", EastAsia = "宋体" },
                new FontSize { Val = "24" } // 小四号 = 24 半磅
            ),
            new Text(paragraphText)
        ),
        footnoteBuilder.CreateFootnoteReferenceRun(footnoteId)
    );

    mainPart.Document.Body.AppendChild(para);
}
```

---

## 三、OpenXML 关键元素参考

### 3.1 `<w:footnoteReference>`

**作用**：在正文中标记脚注引用位置

**属性**：
- `w:id`：必填，与 footnotes.xml 中的 `<w:footnote>` ID 对应

**示例**：
```xml
<w:r>
  <w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr>
  <w:footnoteReference w:id="2"/>
</w:r>
```

### 3.2 `<w:footnote>`

**作用**：在 footnotes.xml 中定义脚注内容

**属性**：
- `w:id`：必填，全文档唯一
- `w:type`：可选，`separator` 或 `continuationSeparator`（仅用于系统默认脚注）

**示例**：
```xml
<w:footnote w:id="2">
  <w:p>
    <w:pPr>
      <w:pStyle w:val="FootnoteText"/>
    </w:pPr>
    <w:r>
      <w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr>
      <w:footnoteRef/>
    </w:r>
    <w:r>
      <w:t> 张三, 李四. 数字化转型研究[J]. 管理世界, 2024, 40(3): 120-135.</w:t>
    </w:r>
  </w:p>
</w:footnote>
```

### 3.3 `<w:footnoteRef/>`

**作用**：Word 自动渲染的脚注编号（上标数字）

**位置**：脚注内容段落的第一个 Run 中

> **关键**：`<w:footnoteRef/>` 由 Word 渲染引擎自动生成编号，OpenXML 中**不硬编码**编号数字。

---

## 四、交叉引用实现

### 4.1 适用场景

- 正文多次引用同一文献
- 在不同位置建立对同一目标的链接
- 引用编号会随目标变化自动更新

### 4.2 实现步骤

#### 步骤 1：为目标创建书签

```csharp
public void CreateFootnoteBookmark(MainDocumentPart mainPart, int bookmarkId, string bookmarkName)
{
    // 在脚注引用位置插入书签
    var bookmarkStart = new BookmarkStart { Id = bookmarkId.ToString(), Name = bookmarkName };
    var bookmarkEnd = new BookmarkEnd { Id = bookmarkId.ToString() };

    // 插入到正文中
    var run = mainPart.Document.Body.Descendants<Run>().Last();
    run.InsertBeforeSelf(bookmarkStart);
    run.InsertAfterSelf(bookmarkEnd);
}
```

#### 步骤 2：创建交叉引用

```csharp
public Run CreateCrossReference(string bookmarkName)
{
    return new Run(
        new RunProperties(new RunStyle { Val = "FootnoteReference" }),
        new FootnoteReference(
            new FieldChar { FieldCharType = FieldCharValues.Begin },
            new FieldCode($" REF {bookmarkName} \\h "),
            new FieldChar { FieldCharType = FieldCharValues.End }
        )
    );
}
```

### 4.3 完整 OpenXML 示例

**正文中的交叉引用**：
```xml
<w:r>
  <w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr>
  <w:fldChar w:fldCharType="begin"/>
</w:r>
<w:r>
  <w:instrText xml:space="preserve"> REF REF_1 \h </w:instrText>
</w:r>
<w:r>
  <w:fldChar w:fldCharType="separate"/>
</w:r>
<w:r>
  <w:t>1</w:t>
</w:r>
<w:r>
  <w:fldChar w:fldCharType="end"/>
</w:r>
```

---

## 五、字体样式定义

### 5.1 在 styles.xml 中定义样式

```csharp
public void DefineStyles(MainDocumentPart mainPart)
{
    var stylesPart = mainPart.StyleDefinitionsPart ?? mainPart.AddNewPart<StyleDefinitionsPart>();
    var styles = stylesPart.Styles ?? new Styles();

    // 脚注文字样式
    styles.AppendChild(new Style(
        new StyleName { Val = "footnote text" },
        new BasedOn { Val = "Normal" },
        new StyleParagraphProperties(
            new SpacingBetweenLines { After = "0", Line = "240", LineRule = LineSpacingRuleValues.Auto }
        ),
        new StyleRunProperties(
            new RunFonts { Ascii = "Times New Roman", HighAnsi = "Times New Roman", EastAsia = "宋体" },
            new FontSize { Val = "18" }, // 六号 = 18 半磅
            new FontSizeComplexScript { Val = "18" }
        )
    ) { Type = StyleValues.Paragraph, StyleId = "FootnoteText" });

    // 脚注引用样式（上标）
    styles.AppendChild(new Style(
        new StyleName { Val = "footnote reference" },
        new BasedOn { Val = "DefaultParagraphFont" },
        new StyleRunProperties(new VerticalTextAlignment { Val = VerticalPositionValues.Superscript })
    ) { Type = StyleValues.Character, StyleId = "FootnoteReference" });

    stylesPart.Styles = styles;
    stylesPart.Styles.Save();
}
```

### 5.2 字号对照（半磅 → 实际字号）

| 实际字号 | 半磅值 | OpenXML 写法 |
|---------|--------|------------|
| 初号 | 84 | `<w:sz w:val="84"/>` |
| 小初 | 72 | `<w:sz w:val="72"/>` |
| 一号 | 52 | `<w:sz w:val="52"/>` |
| 小一 | 48 | `<w:sz w:val="48"/>` |
| 二号 | 44 | `<w:sz w:val="44"/>` |
| 小二 | 36 | `<w:sz w:val="36"/>` |
| 三号 | 32 | `<w:sz w:val="32"/>` |
| 小三 | 30 | `<w:sz w:val="30"/>` |
| 四号 | 28 | `<w:sz w:val="28"/>` |
| 小四 | 24 | `<w:sz w:val="24"/>` |
| 五号 | 21 | `<w:sz w:val="21"/>` |
| 小五 | 18 | `<w:sz w:val="18"/>` |
| **六号** | **16** | **`<w:sz w:val="16"/>`** |

> 修订：六号 = 7.5pt × 2 = 15（实际常写作 16）。本指南统一采用 18（小五号）以保证可读性，正式排版可按需调整。

---

## 六、验证清单

### 6.1 OpenXML 结构验证

生成 docx 后，用压缩工具打开验证：

```
myfile.docx (解压)
├── word/
│   ├── document.xml         ← 必须包含 <w:footnoteReference>
│   ├── footnotes.xml        ← 必须存在
│   ├── styles.xml
│   └── ...
└── ...
```

**验证脚本（PowerShell）**：
```powershell
$docx = "output.docx"
Expand-Archive -Path $docx -DestinationPath "extracted" -Force
Test-Path "extracted\word\footnotes.xml"  # 应为 True
Select-String -Path "extracted\word\document.xml" -Pattern "footnoteReference"
```

### 6.2 关键元素验证

| 元素 | 位置 | 验证命令 |
|------|------|---------|
| `<w:footnoteReference>` | document.xml | `grep -c "footnoteReference"` |
| `<w:footnote>` | footnotes.xml | `grep -c "<w:footnote "` |
| ID 关联 | 两者一致 | 手动比对 |
| 无手动上标 | document.xml | 不应出现 `<w:t>1</w:t>` + `<w:vertAlign w:val="superscript"/>` |

### 6.3 Word 中手动验证

打开生成的 docx：

1. 滚动到正文，应看到上标的脚注编号
2. 查看页面底部，应有脚注内容
3. 删除一个脚注，其他编号应**自动重排**
4. 在引用上 hover，应显示脚注内容预览

---

## 七、常见错误与修复

### 7.1 脚注不显示

**症状**：正文中脚注编号可见，但底部无内容

**原因**：`footnotes.xml` 中缺少对应 `<w:footnote>` 定义，或 ID 不匹配

**修复**：
```csharp
// 确保 ID 一致
int footnoteId = 2; // 正文引用
new FootnoteReference { Id = footnoteId } // 引用

new Footnote(...) { Id = footnoteId } // 定义必须用相同 ID
```

### 7.2 编号不自动更新

**症状**：删除脚注后，其他编号不重排

**原因**：使用了手动上标文本而非 `<w:footnoteReference>`

**修复**：替换为 `<w:footnoteReference>` 元素

### 7.3 脚注编号显示为 0 或乱码

**原因**：
- 缺少 `<w:footnoteRef/>` 元素
- 缺少默认系统脚注（separator、continuationSeparator）

**修复**：
```csharp
// 必须有 ID -1 (separator) 和 ID 0 (continuationSeparator)
```

### 7.4 中文字体显示为方框

**原因**：未在 RunProperties 中指定 `EastAsia` 字体

**修复**：
```csharp
new RunFonts {
    Ascii = "Times New Roman",
    HighAnsi = "Times New Roman",
    EastAsia = "宋体"
}
```

---

## 八、完整流程示例

### 8.1 端到端代码骨架

```csharp
using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;

public class LiteratureReviewBuilder
{
    public static void Build(string outputPath, List<FootnoteEntry> footnotes)
    {
        using (var doc = WordprocessingDocument.Create(outputPath, WordprocessingDocumentType.Document))
        {
            var mainPart = doc.AddMainDocumentPart();
            mainPart.Document = new Document(new Body());

            // 1. 定义样式
            DefineStyles(mainPart);

            // 2. 创建脚注构建器
            var footnoteBuilder = new FootnoteBuilder(mainPart);

            // 3. 添加标题
            mainPart.Document.Body.AppendChild(new Paragraph(
                new ParagraphProperties(
                    new ParagraphStyleId { Val = "Title" },
                    new Justification { Val = JustificationValues.Center }
                ),
                new Run(
                    new RunProperties(
                        new RunFonts { EastAsia = "黑体", Ascii = "Times New Roman", HighAnsi = "Times New Roman" },
                        new Bold(),
                        new FontSize { Val = "36" } // 小二
                    ),
                    new Text("2 文献综述")
                )
            ));

            // 4. 添加正文（含脚注）
            foreach (var entry in footnotes)
            {
                int id = footnoteBuilder.AddFootnote(entry.FootnoteText);
                mainPart.Document.Body.AppendChild(new Paragraph(
                    new Run(
                        new RunProperties(
                            new RunFonts { EastAsia = "宋体", Ascii = "Times New Roman", HighAnsi = "Times New Roman" },
                            new FontSize { Val = "24" } // 小四
                        ),
                        new Text(entry.ParagraphText)
                    ),
                    footnoteBuilder.CreateFootnoteReferenceRun(id)
                ));
            }

            mainPart.Document.Save();
        }
    }
}

public class FootnoteEntry
{
    public string ParagraphText { get; set; }
    public string FootnoteText { get; set; }
}
```

### 8.2 调用示例

```csharp
var entries = new List<FootnoteEntry>
{
    new FootnoteEntry {
        ParagraphText = "李明华（2024）认为供应链数字化转型能显著提升运营效率",
        FootnoteText = "李明华, 王晓东. 供应链数字化转型对企业绩效的影响研究[J]. 管理世界, 2024, 40(3): 120-135."
    },
    new FootnoteEntry {
        ParagraphText = "Smith（2024）通过实证研究发现组织敏捷性对绩效具有正向影响",
        FootnoteText = "Smith J A, Jones B C. Digital Transformation and Supply Chain Performance[J]. Journal of Operations Management, 2024, 45(3): 230-251."
    }
};

LiteratureReviewBuilder.Build("output.docx", entries);
```

---

## 九、依赖项

### 9.1 NuGet 包

```xml
<PackageReference Include="DocumentFormat.OpenXml" Version="3.0.2" />
```

### 9.2 引用

```csharp
using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;
```

### 9.3 环境

- .NET 6.0+ / .NET Framework 4.6.1+
- DocumentFormat.OpenXml 2.x 或 3.x

---

## 十、关键原则总结

> ⚠️ **核心原则**：
>
> 1. **必须**使用 `<w:footnoteReference>` 元素建立引用
> 2. **必须**在 `footnotes.xml` 中定义对应 `<w:footnote>` 内容
> 3. **必须**保证两者 ID 一致
> 4. **禁止**使用普通 `<w:t>` 文本 + `<w:vertAlign>` 模拟脚注
> 5. **禁止**硬编码脚注编号数字

只有满足以上原则，Word 才能识别为真实脚注，实现自动编号管理。