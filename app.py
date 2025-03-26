import pytz
from datetime import datetime
from flask import Flask
import os
import time

from builder import data_builder, signal_builder
from const import TYPE_DERIVATIVE, VN30_DISCORD_URL
from discord import send_discord

os.environ["TZ"] = "Asia/Ho_Chi_Minh"
if hasattr(time, "tzset"):
    time.tzset()

_VN30 = "VN30F1M"

start, end, interval = 9, 0, "1H"
ma, ema, rsi, marsi = 5, 3, 14, 5

current_file_path = os.path.dirname(os.path.abspath(__file__))
data_file_path = os.path.join(current_file_path, "data.csv")
style_file_path = os.path.join(current_file_path, "style.css")
script_file_path = os.path.join(current_file_path, "script.js")

app = Flask(__name__)


@app.route("/")
def home():
    """Show status."""
    try:
        from pandas import read_csv
        data = read_csv(data_file_path)
        style = open(style_file_path).read()
        script = open(script_file_path).read()
        return f"<style>{style}</style>{data.tail(20).to_html()}<script>{script}</script>"
    except FileNotFoundError:
        return "No data available."


@app.route("/trigger")
def trigger():
    """Trigger the job."""
    title = f"Strategy: EMA({ema}) SMA({ma}) RSI({rsi}) MARSI({marsi})"
    data = data_builder(
        _VN30,
        TYPE_DERIVATIVE,
        start,
        end,
        interval,
        ma,
        ema,
        rsi,
        marsi,
    )

    triggered, msg = signal_builder(_VN30, title, data)
    app.logger.info(f"Signal: {triggered} {msg}")

    if triggered:
        resp = send_discord(VN30_DISCORD_URL, msg)
        app.logger.info(f"Discord response: {resp.status_code}")

    data.to_csv(data_file_path)
    return f"[{datetime.now(pytz.utc)}] {triggered} {msg}"


if __name__ == "__main__":
    app.run()
