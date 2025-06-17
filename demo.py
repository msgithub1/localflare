from localflare import LocalFlare
import os

app = LocalFlare(__name__, title="LocalFlare Demo")

# 注册消息处理器
@app.on_message('get_system_info')
def get_system_info(data):
    """获取系统信息"""
    return {
        'platform': os.name,
        'cwd': os.getcwd(),
        'env': dict(os.environ)
    }

@app.on_message('read_file')
def read_file(data):
    """读取文件内容"""
    file_path = data.get('path')
    if not file_path:
        raise ValueError("No file path provided")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return {'content': f.read()}
    except Exception as e:
        raise ValueError(f"Error reading file: {str(e)}")

@app.route('/')
def index():
    return '''
    <html>
        <head>
            <title>LocalFlare Demo</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .card {
                    background: white;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                button {
                    background: #4CAF50;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 4px;
                    cursor: pointer;
                }
                button:hover {
                    background: #45a049;
                }
                pre {
                    background: #f5f5f5;
                    padding: 10px;
                    border-radius: 4px;
                    overflow-x: auto;
                }
            </style>
        </head>
        <body>
            <h1>LocalFlare Demo</h1>
            
            <div class="card">
                <h2>系统信息</h2>
                <button onclick="getSystemInfo()">获取系统信息</button>
                <pre id="systemInfo"></pre>
            </div>

            <div class="card">
                <h2>文件读取</h2>
                <input type="text" id="filePath" placeholder="输入文件路径" style="width: 100%; margin-bottom: 10px;">
                <button onclick="readFile()">读取文件</button>
                <pre id="fileContent"></pre>
            </div>

            <script>
                // 使用Proxy API调用
                async function getSystemInfo() {
                    try {
                        const info = await window.api.get_system_info();
                        document.getElementById('systemInfo').textContent = 
                            JSON.stringify(info, null, 2);
                    } catch (error) {
                        document.getElementById('systemInfo').textContent = 
                            'Error: ' + error.message;
                    }
                }

                async function readFile() {
                    const filePath = document.getElementById('filePath').value;
                    if (!filePath) {
                        alert('请输入文件路径');
                        return;
                    }

                    try {
                        const result = await window.api.read_file({ path: filePath });
                        document.getElementById('fileContent').textContent = 
                            result.content;
                    } catch (error) {
                        document.getElementById('fileContent').textContent = 
                            'Error: ' + error.message;
                    }
                }
            </script>
        </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True) 