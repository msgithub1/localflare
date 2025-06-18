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
            f.close()
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
    return app.render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)