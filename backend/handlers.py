import json
import pytz
from datetime import datetime
import os
import time
from pandas import read_csv

from builder import data_builder, signal_builder
from const import ENVIRONMENT, TYPE_DERIVATIVE, NOTIFICATION_MODE
from notifications import notify
from tcbs import stock_screening_insights

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


def _get_time_records():
    try:
        with open(time_records_file_path, "r") as f:
            time_records = json.load(f)
    except FileNotFoundError:
        time_records = {}
    return time_records


def _set_time_record(entry, value):
    try:
        with open(time_records_file_path, "r") as f:
            time_records = json.load(f)
    except FileNotFoundError:
        time_records = {}

    time_records[entry] = value

    with open(time_records_file_path, "w") as f:
        json.dump(time_records, f)


def _get_current_time():
    return datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")


def get_env():
    env = {
        "stock": _VN30,
        "start": start,
        "end": end,
        "interval": interval,
        "ma": ma,
        "ema": ema,
        "rsi": rsi,
        "marsi": marsi,
        "env": ENVIRONMENT,
        "notification_mode": NOTIFICATION_MODE,
    }
    return env


def get_signals_data():
    try:
        data = read_csv(data_file_path)
        total = len(data)
        data = data.fillna("N/A").to_dict(orient="records")
    except FileNotFoundError:
        total = 0
        data = []

    time_records = _get_time_records()
    last_triggered = time_records.get("last_triggered", "N/A")

    return {
        "total": total,
        "data": data,
        "last_triggered": last_triggered,
    }


def get_stocks():
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
        ]
        filtered_stocks = growth.fillna("N/A").to_dict(orient="records")
    except FileNotFoundError:
        total = 0
        filtered_stocks = []

    time_records = _get_time_records()
    last_filtered = time_records.get("last_filtered", "N/A")

    return {
        "total": total,
        "filtered_stocks": filtered_stocks,
        "last_filtered": last_filtered,
    }


def build_signals():
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

    triggered, pkg = signal_builder(_VN30, data)

    data.to_csv(data_file_path)
    _set_time_record("last_triggered", _get_current_time())
    return {
        "triggered": triggered,
        **pkg,
    }


def test_notify():
    return notify("Vnstocks", "TEST", "Test content", "This is a test notification.")


def trigger_signals():
    _signals = build_signals()
    triggered = _signals["triggered"]

    if triggered:
        title = f"Strategy: EMA({ema}) SMA({ma}) RSI({rsi}) MARSI({marsi})"
        notify(
            title,
            _signals["action"],
            _signals["content"],
            _signals["description"],
        )

    return _signals


def filter_stocks():
    all = stock_screening_insights({"exchangeName": "HOSE,HNX,UPCOM"})
    all.to_csv(all_stocks_file_path)
    _set_time_record("last_filtered", _get_current_time())
    return {
        "total": len(all),
        "message": f"[{_get_current_time()}] Filtered data saved.",
    }
