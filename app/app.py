from flask import Flask
from flask_bootstrap import Bootstrap

from app.config import config

app = Flask(__name__)
app.config.from_object(config)
Bootstrap(app)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['BOOTSTRAP_SERVER_LOCAL'] = True

if __name__ == '__main__':
    app.run()
