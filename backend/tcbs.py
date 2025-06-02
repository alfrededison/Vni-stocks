# @title Hàm lấy dữ liệu bộ lọc (legacy)
import pandas as pd
import json
import requests
from typing import Dict, Optional
from datetime import datetime


_BASE_URL = "https://apipubaws.tcbs.com.vn"
_STOCKS_URL = "stock-insight"
_FUTURE_URL = "futures-insight"

_INTERVAL_MAP = {
    "1m": "1",
    "5m": "5",
    "15m": "15",
    "30m": "30",
    "1H": "60",
    "1D": "D",
    "1W": "W",
    "1M": "M",
}
_OHLC_MAP = {
    "tradingDate": "time",
    "open": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "volume": "volume",
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

tcbs_headers = {
    "sec-ch-ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    "DNT": "1",
    "Accept-language": "vi",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",  # noqa
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Referer": "https://tcinvest.tcbs.com.vn/",
    "sec-ch-ua-platform": '"Windows"',
}


def stock_screening_insights(
    params, size=2000, id=None, drop_lang="vi", headers=tcbs_headers
):
    """
    Get stock screening insights from TCBS Stock Screener
    Parameters:
        params (dict): a dictionary of parameters and their values for the stock screening.
        The keys should be the names of the filters, and the values should be either a single value or
            a tuple of two values (min and max) for the filter.
        For example:
            params = {
                "exchangeName": "HOSE,HNX,UPCOM",
                "epsGrowth1Year": (0, 1000000)
            }
        size (int): number of data points per page. Default is 2000 to get all data.
        id (str): ID of the stock screener. You can ignore this parameter.
        drop_lang (str): language of the column names to drop. Default is 'vi'.
        headers (dict): headers of the request. You can ignore this parameter.
    """
    url = "https://apipubaws.tcbs.com.vn/ligo/v1/watchlist/preview"

    # create a list of filters based on the params dictionary
    filters = []

    for key, value in params.items():
        # if the value is a tuple, it means it has a min and max value
        if isinstance(value, tuple):
            min_value, max_value = value
            filters.append({"key": key, "operator": ">=", "value": min_value})
            filters.append({"key": key, "operator": "<=", "value": max_value})
        # otherwise, it is a single value
        else:
            filters.append({"key": key, "value": value, "operator": "="})

    payload = {
        "tcbsID": id,
        "filters": filters,
    }
    if size is not None:
        payload["size"] = size

    # send request to get response
    response = requests.request(
        "POST",
        url,
        headers=headers,
        data=json.dumps(payload),
    ).json()

    df = pd.json_normalize(response["searchData"]["pageContent"])

    # drop all columns has column name ended with `.vi`
    df = df[df.columns.drop(list(df.filter(regex=f"\.{drop_lang}$")))]

    # drop na columns
    df = df.dropna(axis=1, how="all")

    return df


def history(
    symbol: str,
    asset_type: str,
    end: Optional[str] = None,
    interval: Optional[str] = "1D",
    count_back: Optional[int] = 365,
    show_log: bool = False,
) -> Dict:
    """
    Tham số:
        - end (tùy chọn): thời gian kết thúc lấy dữ liệu. Mặc định là None (ngày hiện tại).
        - interval (tùy chọn): Khung thời gian trích xuất dữ liệu giá lịch sử (1m, 5m, 15m, 30m, 1H, 1D, 1W, 1M).
        - show_log (tùy chọn): Hiển thị thông tin log giúp debug dễ dàng.
        - count_back (tùy chọn): Số lượng dữ liệu trả về từ thời điểm cuối. Mặc định là 365.
    """
    # Validate inputs
    if interval not in _INTERVAL_MAP:
        raise ValueError(
            f"Giá trị interval không hợp lệ: {interval}. Vui lòng chọn: {_INTERVAL_MAP.keys()}"
        )

    if count_back is None:
        count_back = 365

    end_time = datetime.strptime(end, "%Y-%m-%d") if end is not None else datetime.now()
    end_stamp = int(end_time.timestamp())

    if interval in ["1D", "1W", "1M"]:
        end_point = "bars-long-term"
    elif interval in ["1m", "5m", "15m", "30m", "1H"]:
        end_point = "bars"

    # translate the interval to TCBS format
    interval_value = _INTERVAL_MAP[interval]

    # Construct the URL for fetching data
    if asset_type == "derivative":
        url = f"{_BASE_URL}/{_FUTURE_URL}/v2/stock/{end_point}?resolution={interval_value}&ticker={symbol}&type={asset_type}&to={end_stamp}&countBack={count_back}"  # noqa
    else:
        url = f"{_BASE_URL}/{_STOCKS_URL}/v2/stock/{end_point}?resolution={interval_value}&ticker={symbol}&type={asset_type}&to={end_stamp}&countBack={count_back}"  # noqa

    if show_log:
        print(f"Tải dữ liệu từ {url}")

    # Send a GET request to fetch the data
    response = requests.get(url, headers=tcbs_headers)

    if response.status_code != 200:
        raise ConnectionError(
            f"Tải dữ liệu không thành công: {response.status_code} - {response.reason}"
        )

    json_data = response.json()

    if show_log:
        print(
            f"Truy xuất thành công dữ liệu {symbol} {count_back} nến đến {end_time}, khung thời gian {interval}."
        )

    if not json_data:
        raise ValueError(
            "Không tìm thấy dữ liệu. Vui lòng kiểm tra lại mã chứng khoán hoặc thời gian truy xuất."
        )
    else:
        df = _as_df(
            history_data=json_data["data"],
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
    if not history_data:
        raise ValueError("Input data is empty or not provided.")

    # TCBS data is already a list of dictionaries
    df = pd.DataFrame(history_data)
    # Apply column mapping directly through rename
    df.rename(columns=_OHLC_MAP, inplace=True)

    # Ensure all required columns exist
    required_columns = ["time", "open", "high", "low", "close", "volume"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}. Available columns: {df.columns.tolist()}"
        )

    # Standard column order
    df = df[["time", "open", "high", "low", "close", "volume"]]

    # Time conversion - handle different formats based on source
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], errors="coerce")

    # Price scaling for non-index/derivative assets
    if asset_type not in ["index", "derivative"]:
        df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].div(
            1000
        )

    # Round price columns
    df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].round(
        floating
    )

    # Apply data types
    for col, dtype in _OHLC_DTYPE.items():
        if col in df.columns:
            if (
                dtype == "datetime64[ns]"
                and hasattr(df[col], "dt")
                and df[col].dt.tz is not None
            ):
                df[col] = df[col].dt.tz_localize(None)  # Remove timezone info
                if interval == "1D":
                    df[col] = df[col].dt.date
            df[col] = df[col].astype(dtype)

    # Add metadata
    df["name"] = symbol
    df["category"] = asset_type
    df["source"] = "TCBS"

    return df
