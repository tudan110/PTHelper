# PTHelper 🚀

PT 站点自动感谢工具 | 自动批量发送种子感谢 | PT 站点辅助工具

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 功能特性 ✨

- ✅ 自动解析指定页码范围的种子
- ✅ 批量发送感谢（失败后可手动重试）
- ⏱️ 可配置请求间隔（避免封禁）
- 📊 实时日志记录（成功/失败统计）
- 🔒 安全的 Cookie 管理（通过 .env 文件）

## 快速开始 🚀

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置账号

复制模板文件并填写你的PT站点信息：

```bash
cp config/config.env.example config/config.env
vim config/config.env
```

配置文件示例：

```env
# 必填项
PT_DOMAIN=your.ptsite.com
PT_COOKIE="c_secure_uid=XXXX; c_secure_pass=XXXX"

# 可选配置
PAGE_START=1       # 起始页码
PAGE_END=3         # 结束页码
REQUEST_TIMEOUT=60 # 请求超时(秒)
REQUEST_DELAY=1    # 请求间隔(秒)
USER_AGENT=...     # 用户代理（可选）
```

### 3. 运行脚本

```bash
python src/pt_say_thanks.py
```

## 高级用法 🛠️

### 重试失败的种子

当出现失败种子时，日志会输出类似：

```text
WARNING - 以下种子感谢失败: {'24903', '27669'}
INFO - 提示：可以复制这些 ID 并遍历调用 say_thanks() 函数重试，参考 /tests/test_pt_say_thanks.py test_retry_failed_torrent_ids 方法。
```

### 手动重试方法：

```python
from src.pt_say_thanks import say_thanks

failed_ids = {'24903', '27669'}
for tid in failed_ids:
    say_thanks(tid, headers=headers, thanks_url=thanks_url)
```

## 自定义配置项

| 参数名               | 说明       | 默认值 |
|:------------------|:---------|:----|
| `PT_DOMAIN`       | PT站点域名   | 无   |
| `PT_COOKIE`       | 登录Cookie | 无   |
| `PAGE_START`      | 起始页码     | 1   |
| `PAGE_END`        | 结束页码     | 1   |
| `REQUEST_DELAY`   | 请求间隔(秒)  | 0.5 |
| `REQUEST_TIMEOUT` | 请求超时(秒)  | 60  |

## 开发者指南 👨💻

### 项目结构

```text
PTHelper/
├── config/              # 配置文件
├── docs/                # 文档
├── logs/                # 运行日志
├── src/                 # 主代码
├── tests/               # 单元测试
├── .gitignore           # Git忽略文件
├── LICENSE              # 开源协议
├── README.md            # 项目说明
└── requirements.txt     # 依赖列表
```

### 常见问题 ❓

Q：如何获取 Cookie？
A：登录 PT 站点后，通过浏览器开发者工具获取 Cookie 头部的值

Q：担心请求太频繁被封怎么办？
A：在非高峰期运行；减小页码范围；增大 REQUEST_DELAY 值（建议≥1秒）

Q：失败种子如何排查？
A：检查日志中的错误信息，或手动访问 https://站点/details.php?id=种子ID&hit=1

## 免责声明 ⚠️

请合理使用本工具，遵守 PT 站点的：

- 访问频率限制
- 自动化工具使用规则
- 用户规则

过度使用可能导致账号被封禁！

📮 问题反馈： 创建Issue
📜 开源协议： MIT License