---
name: Python 代码规范
description: "这个 Skill 为 Python 开发者提供代码审查和规范检查。依据 PEP 8 和最佳实践检查代码。
# Python 代码规范

## 这是什么
这个 Skill 为 Python 开发者提供代码审查和规范检查。依据 PEP 8 和最佳实践检查代码。

## 什么时候使用
- 审查 Python 代码时
- 编写新的 Python 代码时
- 重构 Python 代码时
- 当你说\"审查这段代码\"或\"检查问题\"时"
---

# Python 代码规范

## 这是什么
这个 Skill 为 Python 开发者提供代码审查和规范检查。依据 PEP 8 和最佳实践检查代码。

## 什么时候使用
- 审查 Python 代码时
- 编写新的 Python 代码时
- 重构 Python 代码时
- 当你说"审查这段代码"或"检查问题"时

## 如何使用

### 代码审查检查清单

### 1. PEP 8 合规性
- 使用 4 个空格缩进（不是制表符）
- 最大行长度：88 字符（Black 默认值）
- 函数/变量使用 snake_case
- 类使用 PascalCase
- 常量使用 UPPER_SNAKE_CASE

### 2. 导入顺序
```python
# 1. 标准库
import os
import sys
from typing import List, Dict

# 2. 第三方库
import pandas as pd
from fastapi import APIRouter

# 3. 本地应用
from app.models import User
from app.utils import helper_func
```

### 3. 类型提示
```python
# ✅ 好
def process_data(users: List[User]) -> Dict[str, int]:
    ...

# ✅ 好：可选类型
def get_user(user_id: int) -> Optional[User]:
    ...

# ❌ 避免：没有类型提示
def process_data(users):
```

### 4. 命名规范
```python
# 函数/变量：snake_case
def get_user_data():
    user_count = 10

# 类：PascalCase
class UserService:
    ...

# 常量：UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
API_BASE_URL = "https://api.example.com"

# 私有变量（以下划线开头）
class User:
    def __init__(self, name: str):
        self._internal_cache = {}  # 单下划线：内部使用
        self.__private_field = None  # 双下划线：名称重整
```

### 5. 文档字符串
```python
def calculate_sum(numbers: List[float]) -> float:
    """计算数字列表的总和。
    
    参数:
        numbers: 数字值列表
        
    返回:
        所有数字的总和
        
    异常:
        ValueError: 列表为空时抛出
    """
    if not numbers:
        raise ValueError("无法计算空列表的总和")
    return sum(numbers)
```

### 6. 异常处理
```python
# ✅ 好：具体异常
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"无效值: {e}")
    raise  # 记录后重新抛出

# ❌ 避免：空捕获
try:
    result = risky_operation()
except:  # 范围太大！
    pass

# ✅ 好：上下文管理器
with open("file.txt", "r") as f:
    content = f.read()
```

### 7. 函数
```python
# ✅ 好：小而专注的函数
def validate_email(email: str) -> bool:
    """验证邮箱格式。"""
    return "@" in email

def process_user(user: User) -> ProcessedUser:
    """处理用户数据。"""
    validated = validate_email(user.email)
    return ProcessedUser(...)

# ❌ 避免：过大的函数（>30行）
def do_everything():  # 太大！
    # 100行代码...
```

### 8. 类
```python
class UserService:
    """用户管理服务。"""
    
    def __init__(self, db: Database):
        self._db = db
    
    def get_user(self, user_id: int) -> Optional[User]:
        """根据ID获取用户。"""
        return self._db.query(user_id)
    
    @property
    def is_active(self) -> bool:
        """检查服务是否活跃。"""
        return self._db.is_connected()
```

### 9. 列表推导式
```python
# ✅ 好
squares = [x**2 for x in range(10)]
evens = [x for x in numbers if x % 2 == 0]

# ✅ 好：生成器（大数据集）
sum_of_squares = sum(x**2 for x in range(10**6))

# ❌ 避免：复杂嵌套推导式
[[print(x) for x in row] for row in matrix]  # 难以阅读
```

### 10. 字符串格式化
```python
# ✅ 好：f-string（Python 3.6+）
name = "Alice"
greeting = f"你好, {name}!"

# ✅ 好：.format()
greeting = "你好, {}!".format(name)

# ❌ 避免：% 格式化
greeting = "你好, %s!" % name
```

## 常见陷阱

### 1. 可变默认参数
```python
# ❌ 错误
def add_item(item, list=[]):
    list.append(item)
    return list

# ✅ 正确
def add_item(item, list=None):
    if list is None:
        list = []
    list.append(item)
    return list
```

### 2. 使用 `==` 还是 `is`
```python
# None 检查用 `is`
if value is None:  # ✅ 好
if value == None:   # ❌ 不好

# 相等性比较用 ==
if value == 10:  # ✅ 好
if value is 10:   # ❌ 不好（可能有效但不可靠）
```

### 3. 忽略异常
```python
# ❌ 错误：静默失败！
try:
    do_something()
except Exception:
    pass

# ✅ 好
try:
    do_something()
except SpecificException as e:
    logger.warning(f"已优雅处理: {e}")
```

### 4. 不使用 `__all__`
```python
# module.py
def public_func():
    pass

def _internal_func():
    pass

__all__ = ["public_func"]  # 显式导出
```

## 自动格式化工具

推荐工具：
- **Black** - 代码格式化
- **isort** - 导入排序
- **flake8** - 风格检查
- **mypy** - 类型检查
- **ruff** - 快速代码检查（推荐！）

## 使用示例

### 审查请求
> "按照 Python 最佳实践审查这段代码"

我会检查：
- PEP 8 合规性
- 类型提示是否存在
- 异常处理
- 命名规范
- 安全问题
- 性能问题

### 重构请求
> "重构这段代码，遵循 Python 最佳实践"

我会：
- 添加类型提示
- 改进命名
- 添加文档字符串
- 修复反模式
- 建议更好的替代方案

---

**注意：以下规则适用于 Trae 的每次回复**

## Trae 回复规范

1. **所有回复必须使用简体中文**
2. **代码注释使用中文**
3. **技术文档使用中文**
4. **错误信息使用中文**
5. **保持友好的中文交流风格**

### 交流示例

❌ 错误：
```
Hello! Let me help you with this Python code.
```

✅ 正确：
```
你好！让我帮你看看这段 Python 代码。
```

❌ 错误：
```
The function name should be in snake_case.
```

✅ 正确：
```
函数名应该使用 snake_case 格式。
```