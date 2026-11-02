---
name: web测试
description: "使用Playwright与测试本地Web应用程序的工具包。支持验证前端功能、调试UI行为、捕获浏览器截图和查看浏览器日志。
## 触发条件

**触发关键词**：
- Playwright、自动化测试
- Web测试、前端测试
- 浏览器测试、UI测试
- 截图测试、调试Web

**触发场景**：
- 用户要求\"测试Web应用\"
- 用户要求\"自动化测试\"
- 用户要求\"截图调试\"
- 用户要求\"验证UI功能\"
- 用户要求\"运行Playwright\"

**不触发**：
- 后端测试（非Web）
- 单元测试（非UI）

要测试本地Web应用程序，编写原生Python Playwright脚本。

**可用辅助脚本**：
- `scripts/with_server.py` - 管理服务器生命周期

**始终先运行`--help`**查看用法。这些脚本很大，应该作为黑盒脚本直接调用。"
---

## 决策树：选择方法

```
用户任务 → 是静态HTML吗？
    ├─ 是 → 直接读取HTML文件识别选择器
    └─ 否（动态Web应用）→ 服务器是否已运行？
        ├─ 否 → 运行：python scripts/with_server.py --help
        └─ 是 → 侦察然后行动：
            1. 导航并等待networkidle
            2. 截图或检查DOM
            3. 从渲染状态识别选择器
            4. 使用发现的选择器执行操作
```

## 示例：使用with_server.py

启动服务器：
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

## 侦察然后行动模式

1. **检查渲染的DOM**：
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   ```

2. **从检查结果识别选择器**

3. **使用发现的选择器执行操作**

## 常见陷阱

- **不要**在动态应用上等待`networkidle`之前检查DOM
- **要**在检查前等待`page.wait_for_load_state('networkidle')`

## 最佳实践

- 使用sync_playwright()
- 完成后始终关闭浏览器
- 使用描述性选择器：`text=`、`role=`、CSS选择器或ID
- 添加适当的等待

## 参考文件

- **examples/** - 显示常见模式的示例：
  - `element_discovery.py` - 发现按钮、链接和输入
  - `static_html_automation.py` - 使用file:// URL
  - `console_logging.py` - 捕获控制台日志