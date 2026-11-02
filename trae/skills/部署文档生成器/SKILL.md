---
name: 部署文档生成器
description: "当用户提及“部署”、“发布”、“上线”、“生产环境”等关键词时，自动生成一份完整、可定制的部署说明文档。本技能支持多种技术栈（前端：Vue/React/Angular/静态HTML；后端：FastAPI/Express/Django/Flask/Spring Boot等）、多种部署方式（Docker / 直接运行 / 静态托管）、多种服务器环境（宝塔 / LNMP / 纯Nginx / Caddy / Apache）以及多种数据库（SQLite / PostgreSQL / MySQL）。生成的文档结构清晰、步骤可执行，并会根据用户提供的项目信息动态调整内容。
用户消息中包含以下任一关键词：

部署、发布、上线、生产环境部署

如何部署、部署说明、部署文档

生成部署方案、写一个部署指南"
---

## 工作流程

当触发本技能时，请按以下步骤生成部署文档：

### 第一步：收集项目信息

通过分析用户提供的代码、配置文件或直接提问，获取以下关键信息（缺失项使用合理默认值）：

| 类别     | 必要信息                             | 默认值/推断方式                                              |
| -------- | ------------------------------------ | ------------------------------------------------------------ |
| 项目名称 | 项目名                               | 从目录名或 `package.json`/`pyproject.toml` 中提取            |
| 前端     | 框架类型、是否使用路由、构建输出目录 | 检测 `vite.config` / `webpack` / `angular.json`；默认输出 `dist` |
| 前端     | 是否需子路径部署（如 `/admin/`）     | 检测 `base` 配置；若无则默认根路径 `/`                       |
| 后端     | 框架类型、入口文件、监听端口         | 检测 `main.py` / `app.js` / `manage.py`；默认端口 8000 (FastAPI) / 3000 (Express) / 8000 (Django) |
| 后端     | API 根路径（如 `/api/v1`）           | 分析路由注册代码；默认 `/api`                                |
| 数据库   | 类型及是否需要持久化                 | 检测 `SQLite` / `PostgreSQL` / `MySQL`；SQLite 建议挂载目录  |
| 服务器   | 环境类型（宝塔 / 纯Nginx / 云厂商）  | 若用户未提供，则给出通用 Nginx 配置，并提示适配              |
| 域名     | 完整域名或 IP                        | 若未提供，使用 `example.com` 作为占位符                      |
| 反向代理 | 是否使用 Nginx/Caddy 等              | 默认使用 Nginx，若用户偏好 Caddy 或 Apache 可切换            |

### 第二步：确定部署架构

根据项目组合，推荐最合适的部署方式（优先级从高到低）：

1. **前后端分离 + Docker**：后端用 Docker 容器化，前端静态文件由 Nginx 托管 → 适用于需要隔离环境、易于扩展的项目
2. **全静态 + 无后端**：仅前端，直接上传到对象存储或 Web 服务器 → 适用于纯前端应用
3. **单体应用 + 直接运行**：后端直接通过 systemd 或进程管理器运行，前端打包后一并由 Nginx 服务 → 适用于小型项目或无 Docker 环境
4. **Serverless**：如前端部署到 Vercel/Netlify，后端部署到云函数 → 适用于用户明确要求

**默认推荐**：前后端分离 + Docker（后端）+ 静态托管（前端）+ Nginx 反向代理。这是最通用、最稳定的组合。

### 第三步：生成部署文档

按照下方“通用部署文档模板”生成 Markdown 内容。所有 `{{变量}}` 需替换为实际值；不需要的章节可删除或标注“可选”。

---

## 通用部署文档模板

```markdown
# {{项目名称}} 部署说明

> 本文档适用于 {{前端框架}} + {{后端框架}} 项目，部署环境为 {{服务器环境}}。

## 部署方案概览

**推荐方式**：{{选择的部署架构}}

**原因**：
{{简短说明，例如：后端无状态易于容器化，前端静态文件可 CDN 加速，Nginx 反代可统一入口。}}

**访问地址**：
- 前端：`{{协议}}://{{域名}}{{前端子路径}}`
- 后端 API：`{{协议}}://{{域名}}{{前端子路径}}/api/...`（实际转发到容器 `{{后端容器内地址}}:{{后端端口}}/{{API根路径}}`）

---

## 一、前置准备

### 1. 服务器环境
- 操作系统：Linux (Ubuntu 20.04+ / CentOS 7+)
- 必需软件：
  - [ ] Docker & Docker Compose（若使用容器）
  - [ ] Nginx（或 Caddy / Apache）
  - [ ] Node.js 18+（仅构建前端时需要）
  - [ ] Python 3.11+ / Java 17+ / 其他运行时（若不使用 Docker）

### 2. 域名与网络
- 域名 `{{域名}}` 已解析到服务器公网 IP
- 防火墙开放端口：`80`、`443`（HTTPS 可选）

### 3. 项目文件
将项目源码上传到服务器，推荐目录结构：

```text
/home/{{用户名}}/projects/{{项目名称}}/
├── frontend/      # 前端源码
├── backend/       # 后端源码
└── docker-compose.yml   # 若使用 Docker
```

---

## 二、后端部署

{{#if 使用 Docker}}
### 方式 A：Docker 容器化部署（推荐）

#### 2.1 创建 Dockerfile

在 `backend/` 目录下创建 `Dockerfile`：

```dockerfile
# 示例：Python FastAPI
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE {{后端端口}}
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{{后端端口}}"]
```

#### 2.2 配置持久化目录

若使用 SQLite 或需要持久化文件，创建数据目录：

```bash
mkdir -p /data/{{项目名称}}
# 例如：/data/{{项目名称}}/db.sqlite3
```

#### 2.3 编写 docker-compose.yml

**文件位置**：项目根目录或 `/opt/docker/{{项目名称}}/docker-compose.yml`（两者均可，推荐放在项目根目录便于版本控制）

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    container_name: {{项目名称}}-backend
    restart: unless-stopped
    ports:
      - "127.0.0.1:{{宿主机映射端口}}:{{后端端口}}"
    environment:
      - DATABASE_URL=sqlite:///data/db.sqlite3
      - SECRET_KEY={{随机密钥}}
    volumes:
      - /data/{{项目名称}}:/app/data
```

> 说明：映射到 `127.0.0.1` 防止端口直接暴露公网，由 Nginx 代理访问。

#### 2.4 启动容器

```bash
cd {{docker-compose.yml所在目录}}
docker compose up -d --build
```

#### 2.5 验证

```bash
curl http://127.0.0.1:{{宿主机映射端口}}/{{API根路径}}/health
```

{{else}}
### 方式 B：直接运行（无 Docker）

#### 2.1 安装依赖

```bash
cd /home/{{用户名}}/projects/{{项目名称}}/backend
# Python
pip install -r requirements.txt
# Node.js
npm install
# 其他语言...
```

#### 2.2 使用进程管理器（以 PM2 / systemd 为例）

**PM2 (Node.js)**：
```bash
npm install -g pm2
pm2 start app.js --name {{项目名称}}-backend
pm2 save
```

**Systemd (Python)**：创建 `/etc/systemd/system/{{项目名称}}-backend.service` 文件。

#### 2.3 验证

```bash
curl http://localhost:{{后端端口}}/{{API根路径}}/health
```

{{/if}}

---

## 三、前端构建与发布

### 3.1 安装依赖并打包

```bash
cd /home/{{用户名}}/projects/{{项目名称}}/frontend
npm install
npm run build   # 产物通常位于 dist/ 或 build/
```

### 3.2 发布到 Web 目录

**静态文件托管**（不经过后端容器）：

```bash
# 创建站点目录
sudo mkdir -p /var/www/{{域名}}/{{前端子路径}}
# 复制构建产物
sudo cp -r dist/* /var/www/{{域名}}/{{前端子路径}}/
```

> 若使用对象存储（如 AWS S3、阿里云 OSS），可同步到 Bucket。

---

## 四、配置反向代理（Nginx）

### 4.1 添加 Nginx 站点配置

创建 `/etc/nginx/sites-available/{{域名}}`（或宝塔对应位置）：

```nginx
server {
    listen 80;
    server_name {{域名}};

    # 可选：将根路径重定向到子路径
    location = / {
        return 301 {{前端子路径}}/;
    }

    # 代理后端 API 请求
    location ^~ {{前端子路径}}/api/ {
        proxy_pass http://127.0.0.1:{{宿主机映射端口}}/{{API根路径}}/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 托管前端静态文件
    location ^~ {{前端子路径}}/ {
        alias /var/www/{{域名}}/{{前端子路径}}/;
        index index.html;
        try_files $uri $uri/ {{前端子路径}}/index.html;  # 支持 history 路由
    }
}
```

### 4.2 测试并重载 Nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
```

> **其他 Web 服务器**：若使用 Caddy，配置类似；宝塔面板直接在图形界面添加上述 location 规则。

---

## 五、完整部署步骤（一键脚本建议）

```bash
# 1. 上传代码
scp -r ./{{项目名称}} root@{{服务器IP}}:/home/{{用户名}}/projects/

# 2. 构建并启动后端
cd /home/{{用户名}}/projects/{{项目名称}}
docker compose up -d --build   # 若使用 Docker

# 3. 构建前端
cd frontend && npm install && npm run build

# 4. 复制前端文件
sudo mkdir -p /var/www/{{域名}}/{{前端子路径}}
sudo cp -r dist/* /var/www/{{域名}}/{{前端子路径}}/

# 5. 更新 Nginx 配置并重载
sudo nginx -t && sudo systemctl reload nginx
```

---

## 六、验证部署

### 6.1 前端页面
浏览器打开 `http://{{域名}}{{前端子路径}}`，应正常显示。

### 6.2 API 接口
```bash
curl http://{{域名}}{{前端子路径}}/api/{{测试端点}}
# 例如 /api/sources
```

### 6.3 检查日志

- 后端容器日志：`docker logs {{项目名称}}-backend`
- Nginx 错误日志：`/var/log/nginx/error.log`

---

## 七、常见问题与解决方案

| 问题                   | 可能原因                                         | 解决方法                                                     |
| ---------------------- | ------------------------------------------------ | ------------------------------------------------------------ |
| 前端页面 404           | 静态文件路径错误或 Nginx `alias` 配置不正确      | 检查 `alias` 末尾的 `/`，确保 `try_files` 包含 `index.html`  |
| API 请求 404           | Nginx `proxy_pass` 缺少末尾 `/` 或后端路由不匹配 | 确认 `proxy_pass` 指向正确的 `http://.../{{API根路径}}/`     |
| 后端无法连接数据库     | 数据库文件权限或挂载路径错误                     | 检查容器内 `/app/data` 目录权限，使用 `docker exec` 进入调试 |
| 刷新页面后 404         | 未配置 `try_files` 回退到 `index.html`           | 在 Nginx location 中添加 `try_files $uri $uri/ /index.html;` |
| 容器内 SQLite 数据丢失 | 未挂载宿主机目录                                 | 在 `docker-compose.yml` 中添加 `volumes` 映射                |

---

## 八、更新与维护

### 后端更新
```bash
cd {{docker-compose.yml目录}}
docker compose down
git pull origin main   # 若有版本控制
docker compose up -d --build
```

### 前端更新
```bash
cd frontend
npm run build
sudo cp -r dist/* /var/www/{{域名}}/{{前端子路径}}/
```

---

## 九、安全建议

- 将 `docker-compose.yml` 中的 `API_KEY` / `SECRET_KEY` 使用环境变量文件（`.env`）管理，不要写死在配置中。
- 为 Nginx 配置 HTTPS（使用 Let's Encrypt）。
- 后端容器只监听 `127.0.0.1`，不暴露 `0.0.0.0`。
- 定期更新基础镜像和依赖包。

---

## 附录：不同技术栈的配置调整

### 前端子路径为根路径（`/`）
若前端直接部署在域名根目录，则：
- `{{前端子路径}}` 设为空字符串或 `/`
- Nginx `location ^~ /api/` 直接放在 `server` 块中，`location /` 托管静态文件。

### 后端非 FastAPI（如 Express）
修改 `proxy_pass` 目标端口和路径即可，例如 Express 默认 API 路径为 `/api`。

### 使用 PostgreSQL / MySQL
在 `docker-compose.yml` 中添加数据库服务容器，并修改后端 `DATABASE_URL` 环境变量。

---

**部署完成后，请将本文档中的占位符替换为实际值并归档。**
```

## 第四步：根据用户补充信息微调

生成文档后，主动询问用户是否有特殊要求（如使用 HTTPS、特定端口、多环境配置等），并根据反馈更新文档。

## 注意事项

- **通用性核心**：避免硬编码任何特定工具、路径或平台。使用占位符并提供多种选项。
- **docker-compose.yml 位置**：推荐放在项目根目录（便于版本控制），但也可以放在 `/opt/docker/项目名/`。两种方式均在文档中说明，让用户自行选择。
- **路径规范**：使用符合 Linux 文件系统层次标准的路径（如 `/var/www`），同时给出宝塔用户的替代路径 `/www/wwwroot`。
- **安全性**：提醒用户不要暴露敏感信息，使用环境变量。
- **可执行性**：所有命令应可直接复制粘贴运行（需替换占位符）。

## 示例对话

**用户**：帮我写一个部署文档，项目是 Vue3 + FastAPI，数据库 SQLite，域名 api.example.com，前端部署在 /dashboard/ 下。

**AI**：（根据上述流程生成文档，自动推断前端框架 Vue3，后端 FastAPI，API 根路径 `/api/v1`，子路径 `/dashboard/`，并给出 Nginx 配置。）

---