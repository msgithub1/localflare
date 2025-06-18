# LocalFlare

[English Version](README.md) 

LocalFlare 是一个轻量级的桌面应用开发框架，它结合了 Flask 的简洁性和本地浏览器的强大功能。

## 特点

- 类似 Flask 的简洁 API
- 内置浏览器窗口
- 本地服务进程
- 轻量级和高性能
- 易于使用和扩展

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

```python
from localflare import LocalFlare

app = LocalFlare(__name__)

@app.route('/')
def index():
    return 'Hello, LocalFlare!'

if __name__ == '__main__':
    app.run()
```

## 许可证

Apache-2.0
