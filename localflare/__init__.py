from webview import create_window, start
from threading import Thread
from flask import Flask, render_template_string, jsonify, request
from os import path
from time import time, sleep
from requests import get, exceptions
from werkzeug.serving import make_server
from typing import Optional, Callable, Any, Dict, Set
from re import search, sub, IGNORECASE
from secrets import token_bytes
from base64 import urlsafe_b64encode

class LocalFlare:
    def __init__(self, import_name: str, title: str = "LocalFlare App"):
        self.flask_app = Flask(import_name)
        self.title = title
        self.window = None
        self._thread = None
        self._host = '127.0.0.1'
        self._port = 0  # 使用0让Flask自动分配端口
        self._debug = False
        self._template_folder = "."
        self._server = None
        self._message_handlers: Dict[str, Callable] = {}
        self._valid_tokens: Set[str] = set()  # 存储有效的token
        self._current_token = self._generate_token()  # 生成初始token
        
        # 添加默认的API路由
        self._setup_default_routes()

    def _generate_token(self) -> str:
        """生成随机token
        
        使用secrets模块生成密码学安全的随机token：
        1. 生成32字节的随机数据
        2. 使用base64编码，但移除填充字符
        3. 替换URL不安全的字符
        """
        # 生成32字节的随机数据
        random_bytes = token_bytes(64)
        # 使用base64编码，但移除填充字符
        token = urlsafe_b64encode(random_bytes).decode('ascii').rstrip('=')
        self._valid_tokens.add(token)
        return token

    def _verify_token(self, token: str) -> bool:
        """验证token"""
        return token in self._valid_tokens

    def _setup_default_routes(self):
        """设置默认的API路由"""
        @self.flask_app.route('/api/send', methods=['POST'])
        def send_message():
            # 验证token
            token = request.headers.get('X-App-Token')
            if not token or not self._verify_token(token):
                return jsonify({'error': 'Invalid token'}), 401

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

    def _get_js_proxy_code(self) -> str:
        """生成JavaScript Proxy代码"""
        return f'''
        <script>
        const createProxy = () => {{
            const token = '{self._current_token}';

            const handler = {{
                get: function(target, prop) {{
                    if (typeof prop === 'symbol') {{
                        return target[prop];
                    }}
                    
                    return async function(...args) {{
                        try {{
                            const response = await fetch('/api/send', {{
                                method: 'POST',
                                headers: {{
                                    'Content-Type': 'application/json',
                                    'X-App-Token': token
                                }},
                                body: JSON.stringify({{
                                    type: prop,
                                    data: args[0] || {{}}
                                }})
                            }});
                            
                            const result = await response.json();
                            if (!result.success) {{
                                throw new Error(result.error);
                            }}
                            return result.result;
                        }} catch (error) {{
                            console.error('Error:', error);
                            throw error;
                        }}
                    }};
                }}
            }};
            
            return new Proxy({{}}, handler);
        }};

        window.api = createProxy();
        </script>
        '''

    def _inject_proxy_code(self, html: str) -> str:
        """使用正则表达式注入代理代码"""
        proxy_code = self._get_js_proxy_code()
        
        # 尝试在</head>标签前注入
        if search(r'</head>', html, IGNORECASE):
            return sub(r'</head>', f'{proxy_code}</head>', html, flags=IGNORECASE)
        
        # 如果没有head标签，尝试在第一个<body>标签后注入
        if search(r'<body[^>]*>', html, IGNORECASE):
            return sub(r'(<body[^>]*>)', f'\\1{proxy_code}', html, flags=IGNORECASE)
        
        # 如果都没有，在文档开始处注入
        return f'{proxy_code}{html}'

    def on_message(self, message_type: str):
        """装饰器：注册消息处理器"""
        def decorator(f):
            self._message_handlers[message_type] = f
            return f
        return decorator

    def route(self, rule: str, **options) -> Callable:
        """装饰器：添加URL规则"""
        def decorator(f):
            @self.flask_app.route(rule, **options)
            def wrapper(*args, **kwargs):
                result = f(*args, **kwargs)
                # 如果返回的是HTML字符串，注入Proxy代码
                if isinstance(result, str) and '<html' in result.lower():
                    result = self._inject_proxy_code(result)
                return result
            return wrapper
        return decorator

    def _wait_for_server(self, timeout: int = 10) -> bool:
        """等待服务器启动"""
        start_time = time()
        while time() - start_time < timeout:
            try:
                response = get(f'http://{self._host}:{self._port}/api/ping')
                if response.status_code == 200:
                    return True
            except exceptions.ConnectionError:
                sleep(0.1)
        return False

    def run(self, host: str = '127.0.0.1', port: Optional[int] = None, debug: bool = False,
            template_folder: Optional[str] = ".") -> None:
        """运行应用"""
        self._host = host
        if port is not None:
            self._port = port
        self._debug = debug
        self._template_folder = template_folder

        # 创建服务器
        self._server = make_server(host, self._port, self.flask_app)
        # 获取实际分配的端口
        self._port = self._server.port

        # 启动Flask服务器
        def run_flask():
            self._server.serve_forever()

        self._thread = Thread(target=run_flask)
        self._thread.daemon = True
        self._thread.start()

        # 等待服务器启动
        if not self._wait_for_server():
            raise RuntimeError("服务器启动超时")

        # 创建窗口
        url = f'http://{host}:{self._port}'
        self.window = create_window(
            self.title,
            url,
            width=800,
            height=600,
            resizable=True,
            text_select=True,
            confirm_close=True
        )
        start(debug=debug)

    def render_template(self, template_name: str, **context) -> str:
        """渲染模板"""
        if self._template_folder:
            template_path = path.join(self._template_folder, template_name)
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
                f.close()
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