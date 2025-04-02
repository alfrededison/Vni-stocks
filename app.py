import pytz
from datetime import datetime
from flask import Flask, render_template
import os
import time

from builder import data_builder, signal_builder
from const import TYPE_DERIVATIVE, VN30_DISCORD_URL
from discord import send_discord
from tcbs import stock_screening_insights

os.environ["TZ"] = "Asia/Ho_Chi_Minh"
if hasattr(time, "tzset"):
    time.tzset()

_VN30 = "VN30F1M"

start, end, interval = 9, 0, "1H"
ma, ema, rsi, marsi = 5, 3, 14, 5

current_file_path = os.path.dirname(os.path.abspath(__file__))
data_file_path = os.path.join(current_file_path, "data.csv")
all_stocks_file_path = os.path.join(current_file_path, "all.csv")

app = Flask(__name__)


@app.route("/")
def home():
    """Show status."""
    from pandas import read_csv

    try:
        data = read_csv(data_file_path)
    except FileNotFoundError:
        data = "No data available."

    try:
        stocks = read_csv(all_stocks_file_path)
        total = len(stocks)
        newH = len(stocks.loc[stocks.percent1YearFromPeak > 0])
        newL = len(stocks.loc[stocks.percent1YearFromBottom < 0])
    except FileNotFoundError:
        total = 0
        newH = 0
        newL = 0

    return render_template(
        "home.html",
        vn30f1m=data,
        total=total,
        newH=newH,
        newL=newL,
    )


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


@app.route("/filter")
def filter():
    """Get filtered data."""
    all = stock_screening_insights({"exchangeName": "HOSE,HNX,UPCOM"})
    all.to_csv(all_stocks_file_path)
    return f"[{datetime.now(pytz.utc)}] Filtered data saved. Total: {len(all)}"


if __name__ == "__main__":
    app.run()
