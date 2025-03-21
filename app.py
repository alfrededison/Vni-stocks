from datetime import datetime, timedelta
from vnstock import Vnstock
import pandas_ta as ta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger
from flask import Flask, redirect


# import os
# import time
# os.environ["TZ"] = "Asia/Ho_Chi_Minh"
# time.tzset()


_VNI = "VN30F1M"
stock = Vnstock().stock(symbol=_VNI, source="VCI")

start, end, interval = 30, 0, "1H"
ma, ema, rsi, marsi = 5, 3, 14, 3

global_data = None
last_update = None


def get_past_date(x):
    past_date = datetime.today() - timedelta(days=x)
    return past_date.strftime("%Y-%m-%d")


def get_stock_data(start, end, symbol=_VNI, interval="1D"):
    return stock.quote.history(
        symbol=symbol,
        start=get_past_date(start),
        end=get_past_date(end),
        interval=interval,
    ).set_index("time")


def emamarsi(close, ma, ema, rsi, marsi):
    sma_ = ta.sma(close, length=ma)
    ema_ = ta.ema(close, length=ema)
    rsi_ = ta.rsi(close, length=rsi)
    marsi_ = ta.sma(rsi_, length=marsi)

    rsi_up = ta.above(rsi_, marsi_)
    buy = ta.cross(ema_, sma_) & rsi_up
    sell = ta.cross(sma_, ema_)
    return sma_, ema_, rsi_, marsi_, buy, sell


def update_data(start, end, interval, ma, ema, rsi, marsi):
    """Update global states with new stock data and calculations."""
    global global_data, last_update
    data = get_stock_data(start=start, end=end, interval=interval)
    sma_, ema_, rsi_, marsi_, buy, sell = emamarsi(
        data.close,
        ma,
        ema,
        rsi,
        marsi,
    )

    global_data = data.join(
        [
            sma_,
            ema_,
            rsi_,
            marsi_,
            buy.rename("Buy"),
            sell.rename("Sell"),
        ]
    )
    last_update = datetime.now()


def send_discord(data):
    import requests
    import json

    url = (
        "https://discord.com/api/webhooks/1248546907534528532/"
        "AJxoxGHJoZRt1zGobHoH6U-ZhM0ETHqg8bUgyu3BhxcSNKFG_ucYmIsQjyL_Cx5J8Cv0"
    )

    return requests.post(
        url,
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
        },
    )


def color_selector(is_buy, is_sell):
    return 43127 if is_buy else 15859772 if is_sell else 0


def build_discord_msg(content, title, desciption, color):
    return {
        "username": _VNI,
        "content": content,
        "embeds": [
            {
                "title": title,
                "description": desciption,
                "color": color,
            },
        ],
    }


def process_signal():
    time = global_data.index[-1]
    price = global_data.close.iloc[-1]
    is_buy = bool(global_data.Buy.iloc[-1])
    is_sell = bool(global_data.Sell.iloc[-1])

    action = "BUY" if is_buy else "SELL" if is_sell else None

    if action is None:
        return f"__{time}__ No signal"

    color = color_selector(is_buy, is_sell)
    content = f"*{_VNI}* **{action}** {price}"
    title = f"Strategy: EMA({ema}) SMA({ma}) RSI({rsi}) MARSI({marsi})"
    description = f"__{time}__ **{action}** @ {price}"

    return build_discord_msg(content, title, description, color)


def main():
    update_data(start, end, interval, ma, ema, rsi, marsi)
    msg = process_signal()
    if isinstance(msg, dict):
        send_discord(msg)


sched = BackgroundScheduler(daemon=True)
trigger = OrTrigger(
    [
        CronTrigger(day_of_week="mon-fri", hour="9-11", minute="*/15"),
        CronTrigger(day_of_week="mon-fri", hour="13-14", minute="*/15"),
    ]
)
sched.add_job(main, trigger)
sched.start()

app = Flask(__name__)


@app.route("/")
def home():
    """Show next trigger run time."""
    next_run = sched.get_jobs()[0].next_run_time
    return f"Welcome Home :) Next trigger at: {next_run}"


@app.route("/update")
def update():
    """Update stock data and calculations."""
    update_data(start, end, interval, ma, ema, rsi, marsi)
    return redirect("/status")


@app.route("/status")
def status():
    """Show current global state values."""
    if global_data is None:
        return "No data available."
    return f"Last update: {last_update} <br> {global_data.tail(10).to_html()}"


@app.route("/signal")
def signal():
    """Send signal to Discord."""
    if global_data is None:
        return "No data available."
    return process_signal()


if __name__ == "__main__":
    app.run()
