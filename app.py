import json
import pytz
from datetime import datetime
from flask import Flask, render_template
import os
import time

from builder import data_builder, signal_builder
from const import TYPE_DERIVATIVE, VN30_DISCORD_URL
from discord import send_discord
from tcbs import stock_screening_insights
from utils import format_dataframe, highlight_signals, highlight_stocks

os.environ["TZ"] = "Asia/Ho_Chi_Minh"
if hasattr(time, "tzset"):
    time.tzset()

_VN30 = "VN30F1M"

start, end, interval = 50, -1, "1H"
ma, ema, rsi, marsi = 5, 3, 14, 5

current_file_path = os.path.dirname(os.path.abspath(__file__))
data_file_path = os.path.join(current_file_path, "data.csv")
all_stocks_file_path = os.path.join(current_file_path, "all.csv")
time_records_file_path = os.path.join(current_file_path, "time_records.json")

app = Flask(__name__)


def get_time_records():
    """Get time records."""
    try:
        with open(time_records_file_path, "r") as f:
            time_records = json.load(f)
    except FileNotFoundError:
        time_records = {}
    return time_records


def set_time_record(entry, value):
    """Set time record."""
    try:
        with open(time_records_file_path, "r") as f:
            time_records = json.load(f)
    except FileNotFoundError:
        time_records = {}

    time_records[entry] = value

    with open(time_records_file_path, "w") as f:
        json.dump(time_records, f)


def get_current_time():
    return datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")


@app.route("/")
def home():
    """Show status."""
    from pandas import read_csv

    try:
        data = read_csv(data_file_path)
        vn30f1m = format_dataframe(data.set_index("time").tail(10), highlight_signals).to_html()
    except FileNotFoundError:
        vn30f1m = "No data available."

    try:
        time_records = get_time_records()
        last_triggered = time_records.get("last_triggered", "N/A")
    except FileNotFoundError:
        last_triggered = "N/A"

    return render_template(
        "home.html",
        data=data.to_json(orient="records"),
        vn30f1m=vn30f1m,
        last_triggered=last_triggered,
    )


@app.route("/stocks")
def stocks():
    """Show filter stocks."""
    from pandas import read_csv

    try:
        stocks = read_csv(all_stocks_file_path)
        total = len(stocks)

        growth = stocks.loc[
            True
            & (stocks.revenueGrowth1Year >= 7)
            & (stocks.revenueGrowth5Year >= 7)
            & (stocks.epsGrowth1Year >= 10)
            & (stocks.epsGrowth5Year >= 10)
            & (stocks.lastQuarterProfitGrowth >= 10)
            & (stocks.secondQuarterProfitGrowth >= 10)
            & (stocks.netMargin >= 0)
            & (stocks.profitForTheLast4Quarters >= 0)
            & (stocks.avgTradingValue5Day >= 1)
            & True,
            [
                "ticker",
                "hasFinancialReport.en",
                "revenueGrowth1Year",
                "revenueGrowth5Year",
                "epsGrowth1Year",
                "epsGrowth5Year",
                "lastQuarterProfitGrowth",
                "secondQuarterProfitGrowth",
                "netMargin",
                "profitForTheLast4Quarters",
                "avgTradingValue5Day",
                "relativeStrength3Day",
                "relativeStrength1Month",
            ],
        ].set_index("ticker")
        growth = format_dataframe(
            growth.sort_values(by="hasFinancialReport.en", ascending=False),
            highlight_stocks,
        ).to_html()
    except FileNotFoundError:
        total = 0
        growth = "No data available."

    try:
        time_records = get_time_records()
        last_filtered = time_records.get("last_filtered", "N/A")
    except FileNotFoundError:
        last_filtered = "N/A"

    return render_template(
        "stocks.html",
        total=total,
        last_filtered=last_filtered,
        filtered_stocks=growth,
    )


@app.route("/trigger")
def trigger():
    """Trigger the job."""
    title = f"Strategy: EMA({ema}) SMA({ma}) RSI({rsi}) MARSI({marsi})"
    data = data_builder(
        "tcbs",
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
    set_time_record("last_triggered", get_current_time())
    return f"[{get_current_time()}] {triggered} {msg}"


@app.route("/filter")
def filter():
    """Get filtered data."""
    all = stock_screening_insights({"exchangeName": "HOSE,HNX,UPCOM"})
    all.to_csv(all_stocks_file_path)
    set_time_record("last_filtered", get_current_time())
    return f"[{get_current_time()}] Filtered data saved. Total: {len(all)}"


if __name__ == "__main__":
    app.run()
