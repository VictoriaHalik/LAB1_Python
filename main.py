from flask import Flask

app = Flask(__name__)


@app.route('/api/v1/hello-world-4')
def index():
    return 'Hello world 4'


if __name__ == '__main__':
    app.run()
