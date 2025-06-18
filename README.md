# LocalFlare

[中文版本](README_zh.md)

LocalFlare is a lightweight desktop application development framework that combines Flask's simplicity with the power of local browser functionality.

## Features

- Flask-like simple API
- Built-in browser window
- Local service process
- Lightweight and high performance
- Easy to use and extend

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from localflare import LocalFlare

app = LocalFlare(__name__)

@app.route('/')
def index():
    return 'Hello, LocalFlare!'

if __name__ == '__main__':
    app.run()
```

## License

Apache-2.0
