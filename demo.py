from localflare import LocalFlare
import os
import psutil
import shutil
from datetime import datetime

app = LocalFlare(__name__, title="LocalFlare Demo")

# 系统信息
@app.on_message('get_system_info')
def get_system_info(data):
    """获取系统信息"""
    return {
        'platform': os.name,
        'cwd': os.getcwd(),
        'env': dict(os.environ),
        'cpu_count': psutil.cpu_count(),
        'memory': {
            'total': psutil.virtual_memory().total,
            'available': psutil.virtual_memory().available,
            'percent': psutil.virtual_memory().percent
        },
        'disk': {
            'total': psutil.disk_usage('/').total,
            'free': psutil.disk_usage('/').free,
            'percent': psutil.disk_usage('/').percent
        }
    }

# 文件系统操作
@app.on_message('list_directory')
def list_directory(data):
    """列出目录内容"""
    path = data.get('path', '.')
    try:
        items = []
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            stat = os.stat(full_path)
            items.append({
                'name': item,
                'path': full_path,
                'is_dir': os.path.isdir(full_path),
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
            })
        return {'items': items}
    except Exception as e:
        raise ValueError(f"Error listing directory: {str(e)}")

@app.on_message('create_file')
def create_file(data):
    """创建文件"""
    path = data.get('path')
    content = data.get('content', '')
    if not path:
        raise ValueError("No file path provided")
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {'success': True}
    except Exception as e:
        raise ValueError(f"Error creating file: {str(e)}")

@app.on_message('delete_path')
def delete_path(data):
    """删除文件或目录"""
    path = data.get('path')
    if not path:
        raise ValueError("No path provided")
    
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        return {'success': True}
    except Exception as e:
        raise ValueError(f"Error deleting path: {str(e)}")

# 进程管理
@app.on_message('get_processes')
def get_processes(data):
    """获取进程列表"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent']):
            try:
                pinfo = proc.info
                processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return {'processes': processes}
    except Exception as e:
        raise ValueError(f"Error getting processes: {str(e)}")

@app.on_message('kill_process')
def kill_process(data):
    """结束进程"""
    pid = data.get('pid')
    if not pid:
        raise ValueError("No process ID provided")
    
    try:
        process = psutil.Process(pid)
        process.terminate()
        return {'success': True}
    except Exception as e:
        raise ValueError(f"Error killing process: {str(e)}")

# 系统监控
@app.on_message('get_system_metrics')
def get_system_metrics(data):
    """获取系统指标"""
    try:
        return {
            'cpu': {
                'percent': psutil.cpu_percent(interval=1),
                'count': psutil.cpu_count(),
                'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            'memory': psutil.virtual_memory()._asdict(),
            'disk': psutil.disk_usage('/')._asdict(),
            'network': {
                'bytes_sent': psutil.net_io_counters().bytes_sent,
                'bytes_recv': psutil.net_io_counters().bytes_recv
            }
        }
    except Exception as e:
        raise ValueError(f"Error getting system metrics: {str(e)}")

@app.route('/')
def index():
    return '''
    <html>
        <head>
            <title>LocalFlare 高级演示</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background: #f5f5f5;
                }
                .card {
                    background: white;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                }
                button {
                    background: #4CAF50;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 4px;
                    cursor: pointer;
                    margin: 5px;
                }
                button:hover {
                    background: #45a049;
                }
                button.danger {
                    background: #f44336;
                }
                button.danger:hover {
                    background: #da190b;
                }
                input, select {
                    padding: 8px;
                    margin: 5px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    width: calc(100% - 20px);
                }
                pre {
                    background: #f8f8f8;
                    padding: 10px;
                    border-radius: 4px;
                    overflow-x: auto;
                    max-height: 300px;
                    overflow-y: auto;
                }
                .file-item {
                    display: flex;
                    align-items: center;
                    padding: 8px;
                    border-bottom: 1px solid #eee;
                }
                .file-item:hover {
                    background: #f5f5f5;
                }
                .file-icon {
                    margin-right: 10px;
                    color: #666;
                }
                .process-item {
                    display: flex;
                    justify-content: space-between;
                    padding: 8px;
                    border-bottom: 1px solid #eee;
                }
                .metric-card {
                    text-align: center;
                    padding: 15px;
                }
                .metric-value {
                    font-size: 24px;
                    font-weight: bold;
                    color: #4CAF50;
                }
                .metric-label {
                    color: #666;
                    margin-top: 5px;
                }
            </style>
        </head>
        <body>
            <h1>LocalFlare 高级演示</h1>
            
            <div class="grid">
                <!-- 系统信息 -->
                <div class="card">
                    <h2>系统信息</h2>
                    <button onclick="getSystemInfo()">刷新系统信息</button>
                    <pre id="systemInfo"></pre>
                </div>

                <!-- 文件系统 -->
                <div class="card">
                    <h2>文件系统</h2>
                    <input type="text" id="dirPath" placeholder="输入目录路径" value=".">
                    <button onclick="listDirectory()">列出目录</button>
                    <div id="fileList"></div>
                </div>

                <!-- 进程管理 -->
                <div class="card">
                    <h2>进程管理</h2>
                    <button onclick="getProcesses()">刷新进程列表</button>
                    <div id="processList"></div>
                </div>

                <!-- 系统监控 -->
                <div class="card">
                    <h2>系统监控</h2>
                    <button onclick="startMonitoring()">开始监控</button>
                    <button onclick="stopMonitoring()">停止监控</button>
                    <div id="metrics" class="grid"></div>
                </div>
            </div>

            <script>
                let monitoringInterval = null;

                // 系统信息
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

                // 文件系统
                async function listDirectory() {
                    const path = document.getElementById('dirPath').value;
                    try {
                        const result = await window.api.list_directory({ path });
                        const fileList = document.getElementById('fileList');
                        fileList.innerHTML = result.items.map(item => `
                            <div class="file-item">
                                <span class="file-icon">${item.is_dir ? '📁' : '📄'}</span>
                                <span>${item.name}</span>
                                <span style="margin-left: auto">
                                    ${item.is_dir ? '' : formatSize(item.size)}
                                </span>
                                <button onclick="deletePath('${item.path}')" class="danger">删除</button>
                            </div>
                        `).join('');
                    } catch (error) {
                        alert('Error: ' + error.message);
                    }
                }

                async function deletePath(path) {
                    if (!confirm('确定要删除吗？')) return;
                    try {
                        await window.api.delete_path({ path });
                        listDirectory();
                    } catch (error) {
                        alert('Error: ' + error.message);
                    }
                }

                // 进程管理
                async function getProcesses() {
                    try {
                        const result = await window.api.get_processes();
                        const processList = document.getElementById('processList');
                        processList.innerHTML = result.processes.map(proc => `
                            <div class="process-item">
                                <span>${proc.name} (${proc.pid})</span>
                                <span>CPU: ${proc.cpu_percent.toFixed(1)}%</span>
                                <span>内存: ${proc.memory_percent.toFixed(1)}%</span>
                                <button onclick="killProcess(${proc.pid})" class="danger">结束</button>
                            </div>
                        `).join('');
                    } catch (error) {
                        alert('Error: ' + error.message);
                    }
                }

                async function killProcess(pid) {
                    if (!confirm('确定要结束进程吗？')) return;
                    try {
                        await window.api.kill_process({ pid });
                        getProcesses();
                    } catch (error) {
                        alert('Error: ' + error.message);
                    }
                }

                // 系统监控
                async function updateMetrics() {
                    try {
                        const metrics = await window.api.get_system_metrics();
                        const metricsDiv = document.getElementById('metrics');
                        metricsDiv.innerHTML = `
                            <div class="metric-card">
                                <div class="metric-value">${metrics.cpu.percent}%</div>
                                <div class="metric-label">CPU 使用率</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">${metrics.memory.percent}%</div>
                                <div class="metric-label">内存使用率</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">${metrics.disk.percent}%</div>
                                <div class="metric-label">磁盘使用率</div>
                            </div>
                        `;
                    } catch (error) {
                        console.error('Error updating metrics:', error);
                    }
                }

                function startMonitoring() {
                    if (monitoringInterval) return;
                    updateMetrics();
                    monitoringInterval = setInterval(updateMetrics, 1000);
                }

                function stopMonitoring() {
                    if (monitoringInterval) {
                        clearInterval(monitoringInterval);
                        monitoringInterval = null;
                    }
                }

                // 工具函数
                function formatSize(bytes) {
                    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
                    let size = bytes;
                    let unitIndex = 0;
                    while (size >= 1024 && unitIndex < units.length - 1) {
                        size /= 1024;
                        unitIndex++;
                    }
                    return `${size.toFixed(1)} ${units[unitIndex]}`;
                }

                // 初始化
                getSystemInfo();
                listDirectory();
                getProcesses();
            </script>
        </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)