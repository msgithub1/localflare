import webview
import threading
from flask import Flask, render_template_string, jsonify, request
import os
import time
import requests
from werkzeug.serving import make_server
from typing import Optional, Callable, Any, Dict

class LocalFlare:
    def __init__(self, import_name: str, title: str = "LocalFlare App"):
        self.flask_app = Flask(import_name)
        self.title = title
        self.window = None
        self._thread = None
        self._port = 9517
        self._host = '127.0.0.1'
        self._debug = False
        self._template_folder = None
        self._server = None
        self._message_handlers: Dict[str, Callable] = {}

        # 添加默认的API路由
        self._setup_default_routes()

    def _setup_default_routes(self):
        """设置默认的API路由"""
        @self.flask_app.route('/api/send', methods=['POST'])
        def send_message():
            data = request.get_json()
            if not data or 'type' not in data:
                return jsonify({'error': 'Invalid message format'}), 400
            
            message_type = data['type']
            if message_type in self._message_handlers:
                try:
                    result = self._message_handlers[message_type](data.get('data', {}))
                    return jsonify({'success': True, 'result': result})
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
            return jsonify({'error': f'No handler for message type: {message_type}'}), 404

        @self.flask_app.route('/api/ping', methods=['GET'])
        def ping():
            return jsonify({'status': 'ok'})

    def on_message(self, message_type: str):
        """装饰器：注册消息处理器"""
        def decorator(f):
            self._message_handlers[message_type] = f
            return f
        return decorator

    def _get_js_proxy_code(self) -> str:
        """生成JavaScript Proxy代码"""
        return '''
        <script>
        const createProxy = () => {
            const handler = {
                get: function(target, prop) {
                    if (typeof prop === 'symbol') {
                        return target[prop];
                    }
                    
                    return async function(...args) {
                        try {
                            const response = await fetch('/api/send', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({
                                    type: prop,
                                    data: args[0] || {}
                                })
                            });
                            
                            const result = await response.json();
                            if (!result.success) {
                                throw new Error(result.error);
                            }
                            return result.result;
                        } catch (error) {
                            console.error('Error:', error);
                            throw error;
                        }
                    };
                }
            };
            
            return new Proxy({}, handler);
        };

        window.api = createProxy();
        </script>
        '''

    def route(self, rule: str, **options) -> Callable:
        """装饰器：添加URL规则"""
        def decorator(f):
            @self.flask_app.route(rule, **options)
            def wrapper(*args, **kwargs):
                result = f(*args, **kwargs)
                # 如果返回的是HTML字符串，注入Proxy代码
                if isinstance(result, str) and '<html' in result.lower():
                    # 在</head>标签前注入Proxy代码
                    proxy_code = self._get_js_proxy_code()
                    if '</head>' in result:
                        result = result.replace('</head>', f'{proxy_code}</head>')
                    else:
                        # 如果没有head标签，在body开始处注入
                        result = result.replace('<body', f'<head>{proxy_code}</head><body')
                return result
            return wrapper
        return decorator

    def _wait_for_server(self, timeout: int = 10) -> bool:
        """等待服务器启动"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f'http://{self._host}:{self._port}/api/ping')
                if response.status_code == 200:
                    return True
            except requests.exceptions.ConnectionError:
                time.sleep(0.1)
        return False

    def run(self, host: str = '127.0.0.1', port: int = 9517, debug: bool = False,
            template_folder: Optional[str] = None) -> None:
        """运行应用"""
        self._host = host
        self._port = port
        self._debug = debug
        self._template_folder = template_folder

        # 创建服务器
        self._server = make_server(host, port, self.flask_app)

        # 启动Flask服务器
        def run_flask():
            self._server.serve_forever()

        self._thread = threading.Thread(target=run_flask)
        self._thread.daemon = True
        self._thread.start()

        # 等待服务器启动
        if not self._wait_for_server():
            raise RuntimeError("服务器启动超时")

        # 创建窗口
        url = f'http://{host}:{port}'
        self.window = webview.create_window(
            self.title,
            url,
            width=800,
            height=600,
            resizable=True,
            text_select=True,
            confirm_close=True
        )
        webview.start(debug=debug)

    def render_template(self, template_name: str, **context) -> str:
        """渲染模板"""
        if self._template_folder:
            template_path = os.path.join(self._template_folder, template_name)
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            return render_template_string(template, **context)
        return render_template_string(template_name, **context)

    def add_url_rule(self, rule: str, endpoint: Optional[str] = None,
                     view_func: Optional[Callable] = None, **options) -> None:
        """添加URL规则"""
        self.flask_app.add_url_rule(rule, endpoint, view_func, **options)

    def errorhandler(self, code_or_exception: Any) -> Callable:
        """错误处理器装饰器"""
        return self.flask_app.errorhandler(code_or_exception)

    def before_request(self, f: Callable) -> Callable:
        """请求前处理器装饰器"""
        return self.flask_app.before_request(f)

    def after_request(self, f: Callable) -> Callable:
        """请求后处理器装饰器"""
        return self.flask_app.after_request(f) 