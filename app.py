from datetime import datetime, timedelta
from vnstock import Vnstock
import pandas_ta as ta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger
from flask import Flask


# import os
# import time
# os.environ["TZ"] = "Asia/Ho_Chi_Minh"
# time.tzset()


_VNI = "VN30F1M"
stock = Vnstock().stock(symbol=_VNI, source="VCI")


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
    return buy, sell


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


def main():
    print(datetime.now())

    data = get_stock_data(start=30, end=0, interval="1H")
    print(data.tail())

    ma = 5
    ema = 3
    rsi = 14
    marsi = 3
    buy, sell = emamarsi(data.close, ma, ema, rsi, marsi)
    print(buy.tail())
    print(sell.tail())

    is_buy = bool(buy[-1])
    is_sell = bool(sell[-1])

    action = "BUY" if is_buy else "SELL" if is_sell else None

    if action:
        color = color_selector(is_buy, is_sell)
        content = f"*{_VNI}* **{action}** {data.close[-1]}"
        title = f"Strategy: EMA({ema}) SMA({ma}) RSI({rsi}) MARSI({marsi})"
        description = f"__{data.index[-1]}__ **{action}** @ {data.close[-1]}"

        msgdata = build_discord_msg(content, title, description, color)
        print(msgdata)
        resp = send_discord(msgdata)
        print(resp.status_code, resp.reason)
    else:
        print(f"__{data.index[-1]}__ No signal")


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
    """Function for test purposes."""
    return "Welcome Home :) !"


if __name__ == "__main__":
    app.run()
