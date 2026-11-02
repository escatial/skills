---
name: web设计
description: "用于创建复杂的、多组件的claude.ai HTML artifacts的前端web技术套件（React、Tailwind CSS、shadcn/ui）。用于需要状态管理、路由或shadcn/ui组件的复杂artifacts——不适用于简单的单文件HTML/JSX artifacts。
## 触发条件

**触发关键词**：
- Web Artifact、HTML Artifact、VUE
- React组件、shadcn/ui、VUE组件
- Tailwind CSS、前端框架、VUE
- 打包HTML、单页应用

**触发场景**：
- 用户要求\"创建复杂HTML artifact\"
- 用户要求\"构建React应用\"
- 用户要求\"使用shadcn/ui\"
- 用户要求\"打包前端项目\"
- 用户要求\"创建交互式网页\"

**不触发**：
- 简单HTML文件（非复杂artifact）
- 后端项目（非前端）"
---

## 重要：避免"AI垃圾"

避免使用过多的居中布局、紫色渐变、统一圆角和Inter字体。

## 快速开始

### 步骤1：初始化项目

运行初始化脚本创建新React项目：
```bash
bash scripts/init-artifact.sh <project-name>
cd <project-name>
```

这会创建一个完全配置的项目：
- React + TypeScript（通过Vite）
- Tailwind CSS 3.4.1 with shadcn/ui主题系统
- 路径别名配置
- 40+ shadcn/ui组件预装
- 所有Radix UI依赖项
- Parcel配置用于打包

### 步骤2：开发Artifact

编辑生成的文件来构建artifact。

### 步骤3：打包成单个HTML文件

将React应用打包成单个HTML artifact：
```bash
bash scripts/bundle-artifact.sh
```

这创建`bundle.html`——一个自包含的artifact，所有JavaScript、CSS和依赖项内联。

### 步骤4：与用户分享Artifact

最后，在对话中与用户分享捆绑的HTML文件。

### 步骤5：测试/可视化（可选）

注意：这是完全可选的步骤。

使用可用工具测试/可视化artifact。