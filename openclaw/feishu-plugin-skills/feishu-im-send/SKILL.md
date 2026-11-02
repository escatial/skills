---
name: feishu-im-send
description: |
  飞书消息发送工具，用于发送文本、图片、文件等消息到飞书会话。

  **当以下情况时使用此 Skill**:
  (1) 需要发送消息到飞书用户或群聊
  (2) 需要发送文件（PDF、文档等）给用户
  (3) 需要发送图片到飞书会话
  (4) 用户提到"发送文件"、"发送PDF"、"发消息"、"发送图片"

---

# 飞书消息发送

## 执行前必读

- 该 Skill 中的所有发送工具均以机器人身份调用
- 发送文件前需要先上传文件获取 file_key，然后发送文件消息
- 支持的文件类型：pdf、doc、xls、ppt、mp4、opus、stream、image
- 文件大小限制：100MB

---

## 快速索引：意图 → 工具

| 用户意图 | 工具 | 必填参数 | 常用可选 |
|---------|------|---------|---------|
| 发送文本消息 | feishu_im_send_message | to, text | replyToMessageId, replyInThread |
| 发送文件 | feishu_im_send_file | to, file_path | file_name, replyToMessageId, replyInThread |
| 发送图片 | feishu_im_send_image | to, image_path | replyToMessageId, replyInThread |
| 上传并发送文件 | feishu_im_upload_and_send_file | to, file_path | file_name, replyToMessageId, replyInThread |

---

## 核心参数

### to 参数格式

| 类型 | 格式 | 示例 |
|------|------|------|
| 用户 ID | open_id (ou_xxx) | `ou_6a66f56aba9e83602b2e676bafa7ad43` |
| 群聊 ID | chat_id (oc_xxx) | `oc_xxx` |

### file_path 参数

本地文件路径，支持：
- 绝对路径：`E:\OpenClaw\grape_pdfs\grape_cluster_harvesting_2021.pdf`
- 带文件名的路径会自动识别文件类型

---

## 使用场景示例

### 场景 1: 发送 PDF 文件给用户

```json
{
  "to": "ou_6a66f56aba9e83602b2e676bafa7ad43",
  "file_path": "E:\\OpenClaw\\grape_pdfs\\grape_cluster_harvesting_2021.pdf"
}
```

### 场景 2: 发送图片

```json
{
  "to": "ou_6a66f56aba9e83602b2e676bafa7ad43",
  "image_path": "E:\\OpenClaw\\images\\screenshot.png"
}
```

### 场景 3: 发送文本消息

```json
{
  "to": "ou_6a66f56aba9e83602b2e676bafa7ad43",
  "text": "这是发送的消息内容"
}
```

### 场景 4: 回复某条消息（带上下文）

```json
{
  "to": "ou_6a66f56aba9e83602b2e676bafa7ad43",
  "file_path": "E:\\OpenClaw\\document.pdf",
  "replyToMessageId": "om_xxx",
  "replyInThread": true
}
```

---

## 常见错误与排查

| 错误现象 | 根本原因 | 解决方案 |
|---------|---------|---------|
| 文件不存在 | file_path 路径错误 | 确认文件路径正确，文件是否存在 |
| 文件太大 | 超过 100MB 限制 | 压缩文件或分段发送 |
| 文件类型不支持 | 不支持的格式 | 转换为支持的格式（pdf/doc/xls/ppt/mp4/opus/image） |
| 权限不足 | 机器人没有发消息权限 | 确认飞书应用已配置 im:message:send_as_bot 权限 |
| to 参数格式错误 | open_id/chat_id 格式不正确 | 确认是 ou_xxx（用户）或 oc_xxx（群聊）格式 |