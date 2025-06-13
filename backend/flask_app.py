from flask import Flask
from flask_cors import CORS

from handlers import (
    get_env,
    get_signals_data,
    get_stocks,
    build_signals,
    trigger_signals,
    filter_stocks,
    test_notify,
)

app = Flask(__name__)
CORS(app)


@app.route("/env")
def env():
    return get_env()


@app.route("/signals")
def signals():
    return get_signals_data()


@app.route("/stocks")
def stocks():
    return get_stocks()


@app.route("/build")
def build():
    return build_signals()


@app.route("/trigger")
def trigger():
    return trigger_signals()


@app.route("/filter")
def filter():
    return filter_stocks()


@app.route("/test-notify")
def notify():
    return test_notify()


if __name__ == "__main__":
    app.run()
