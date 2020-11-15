from flask import Flask
from flask_bootstrap import Bootstrap
from views import home

app = Flask(__name__)
Bootstrap(app)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['BOOTSTRAP_SERVER_LOCAL'] = True


@app.route("/")
def index():
    return home()


if __name__ == '__main__':
    app.run()
