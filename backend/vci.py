from typing import Dict, Optional
from datetime import datetime
import pandas as pd
import json
import requests


_TRADING_URL = "https://trading.vietcap.com.vn/api/"
_CHART_URL = "chart/OHLCChart/gap"
_INTERVAL_MAP = {
    "1m": "ONE_MINUTE",
    "5m": "ONE_MINUTE",
    "15m": "ONE_MINUTE",
    "30m": "ONE_MINUTE",
    "1H": "ONE_HOUR",
    "1D": "ONE_DAY",
    "1W": "ONE_DAY",
    "1M": "ONE_DAY",
}
_RESAMPLE_MAP = {
    "5m": "5min",
    "15m": "15min",
    "30m": "30min",
    "1W": "1W",
    "1M": "M",
}
_OHLC_MAP = {
    "t": "time",
    "o": "open",
    "h": "high",
    "l": "low",
    "c": "close",
    "v": "volume",
}
# Pandas data type mapping for history price data
_OHLC_DTYPE = {
    "time": "datetime64[ns]",  # Convert timestamps to datetime
    "open": "float64",
    "high": "float64",
    "low": "float64",
    "close": "float64",
    "volume": "int64",
}
DEFAULT_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    # "Accept-Language": "vi",
    "Cache-Control": "no-cache",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "DNT": "1",
    "Pragma": "no-cache",
}


headers = DEFAULT_HEADERS.copy()
headers["User-Agent"] = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"  # noqa
)
headers.update(
    {
        "Referer": "https://trading.vietcap.com.vn/",
        "Origin": "https://trading.vietcap.com.vn/",
    }
)


def history(
    symbol: str,
    asset_type: str,
    start: str,
    end: Optional[str] = None,
    interval: Optional[str] = "1D",
    show_log: Optional[bool] = False,
):
    """
    Tải lịch sử giá của mã chứng khoán từ nguồn dữ liệu VN Direct.

    Tham số:
        - start (bắt buộc): thời gian bắt đầu lấy dữ liệu,
            có thể là ngày dạng string kiểu "YYYY-MM-DD" hoặc "YYYY-MM-DD HH:MM:SS".
        - end (tùy chọn): thời gian kết thúc lấy dữ liệu.
            Mặc định là None, chương trình tự động lấy thời điểm hiện tại.
            Có thể nhập ngày dạng string kiểu "YYYY-MM-DD" hoặc "YYYY-MM-DD HH:MM:SS".
        - interval (tùy chọn): Khung thời gian trích xuất dữ liệu giá lịch sử.
            Giá trị nhận: 1m, 5m, 15m, 30m, 1H, 1D, 1W, 1M. Mặc định là "1D".
        - show_log (tùy chọn): Hiển thị thông tin log giúp debug dễ dàng.
            Mặc định là False.
    """
    # Validate inputs
    if interval not in _INTERVAL_MAP:
        raise ValueError(
            f"Giá trị interval không hợp lệ: {interval}. Vui lòng chọn: {_INTERVAL_MAP.keys()}"
        )

    start_time = datetime.strptime(start, "%Y-%m-%d")

    # add one more day to end_time if end is not None
    if end is not None:
        end_time = datetime.strptime(end, "%Y-%m-%d") + pd.Timedelta(days=1)

    if start_time > end_time:
        raise ValueError("Thời gian bắt đầu không thể lớn hơn thời gian kết thúc.")

    # convert start and end date to timestamp
    if end is None:
        # get tomorrow end time
        end_stamp = int((datetime.now() + pd.Timedelta(days=1)).timestamp())
    else:
        end_stamp = int(end_time.timestamp())

    start_stamp = int(start_time.timestamp())

    intvl = _INTERVAL_MAP[interval]

    # Construct the URL for fetching data
    url = _TRADING_URL + _CHART_URL

    payload = json.dumps(
        {
            "timeFrame": intvl,
            "symbols": [symbol],
            "from": start_stamp,
            "to": end_stamp,
        }
    )

    if show_log:
        print(f"Tải dữ liệu từ {url}\npayload: {payload}")

    # Send a GET request to fetch the data
    response = requests.post(url, headers=headers, data=payload)

    if response.status_code != 200:
        raise ConnectionError(
            f"Failed to fetch data: {response.status_code} - {response.reason}"
        )

    json_data = response.json()

    if show_log:
        print(
            f"Truy xuất thành công dữ liệu {symbol} từ {start}"
            f" đến {end}, khung thời gian {interval}."
        )

    # if json_data is empty, raise an error
    if not json_data:
        raise ValueError(
            "Không tìm thấy dữ liệu. Vui lòng kiểm tra lại mã chứng khoán hoặc thời gian truy xuất."
        )
    else:
        df = _as_df(
            history_data=json_data[0],
            symbol=symbol,
            asset_type=asset_type,
            interval=interval,
        )

        return df


def _as_df(
    history_data: Dict,
    symbol: str,
    asset_type: str,
    interval: str,
    floating: Optional[int] = 2,
) -> pd.DataFrame:
    """
    Converts stock price history data from JSON format to DataFrame.

    Parameters:
        - history_data: Stock price history data in JSON format.
    Returns:
        - DataFrame: Stock price history data as a DataFrame.
    """
    if not history_data:
        raise ValueError("Input data is empty or not provided.")

    # Select and rename columns directly using a dictionary comprehension
    columns_of_interest = {
        key: _OHLC_MAP[key] for key in _OHLC_MAP.keys() & history_data.keys()
    }
    df = pd.DataFrame(history_data)[columns_of_interest.keys()].rename(
        columns=_OHLC_MAP
    )
    # rearrange columns by open, high, low, close, volume, time
    df = df[["time", "open", "high", "low", "close", "volume"]]

    # Ensure 'time' column data are numeric (integers), then convert to datetime
    df["time"] = pd.to_datetime(df["time"].astype(int), unit="s").dt.tz_localize(
        "UTC"
    )  # Localize the original time to UTC
    # Convert UTC time to Asia/Ho_Chi_Minh timezone, make sure time is correct for minute and hour interval
    df["time"] = df["time"].dt.tz_convert("Asia/Ho_Chi_Minh")

    if asset_type not in ["index", "derivative"]:
        # divide open, high, low, close, volume by 1000
        df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].div(
            1000
        )

    # round open, high, low, close to 2 decimal places
    df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].round(
        floating
    )

    # if resolution is not in 1m, 1H, 1D, resample the data
    if interval not in ["1m", "1H", "1D"]:
        df = (
            df.set_index("time")
            .resample(_RESAMPLE_MAP[interval])
            .agg(
                {
                    "open": "first",
                    "high": "max",
                    "low": "min",
                    "close": "last",
                    "volume": "sum",
                }
            )
            .reset_index()
        )

    # set datatype for each column using _OHLC_DTYPE
    for col, dtype in _OHLC_DTYPE.items():
        if dtype == "datetime64[ns]":
            df[col] = df[col].dt.tz_localize(None)  # Remove timezone information
            if interval == "1D":
                df[col] = df[col].dt.date
        df[col] = df[col].astype(dtype)

    # Set metadata attributes
    df["name"] = symbol
    df["category"] = asset_type
    df["source"] = "VCI"

    return df
