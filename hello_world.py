from localflare import LocalFlare

app = LocalFlare(__name__, title="Hello LocalFlare")

@app.route('/')
def index():
    return '''
    <html>
        <head>
            <title>Hello LocalFlare</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #f0f0f0;
                }
                .container {
                    text-align: center;
                    padding: 2rem;
                    background-color: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #333;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>欢迎使用 LocalFlare!</h1>
                <p>这是一个简单的示例应用。</p>
            </div>
        </body>
    </html>
    '''

if __name__ == '__main__':
    app.run() 