from datetime import datetime, timedelta
import pandas_ta as ta

from const import DISCORD_POSITIVE_COLOR, DISCORD_NEGATIVE_COLOR, DISCORD_NEUTRAL_COLOR
from vci import history as vci_history
from tcbs import history as tcbs_history


def get_past_date(x):
    past_date = datetime.today() - timedelta(days=x)
    return past_date.strftime("%Y-%m-%d")


def emamarsi(close, ma, ema, rsi, marsi):
    sma_ = ta.sma(close, length=ma)
    ema_ = ta.ema(close, length=ema)
    rsi_ = ta.rsi(close, length=rsi)
    marsi_ = ta.sma(rsi_, length=marsi)

    price_up = ta.roc(close, length=1) > 0
    rsi_up = ta.above(rsi_, marsi_)
    buy = ta.cross(ema_, sma_) & rsi_up & price_up.astype(int)
    sell = ta.cross(sma_, ema_)
    return sma_, ema_, rsi_, marsi_, buy, sell


def data_builder(source, symbol, asset_type, since, to, interval, ma, ema, rsi, marsi):
    """Build stock data and technical calculations."""
    if source == "vci":
        raw_data = vci_history(
            symbol=symbol,
            asset_type=asset_type,
            start=get_past_date(since),
            end=get_past_date(to),
            interval=interval,
        )
    elif source == "tcbs":
        raw_data = tcbs_history(
            symbol=symbol,
            asset_type=asset_type,
            end=get_past_date(to),
            interval=interval,
            count_back=since,
        )
    else:
        raise ValueError("Invalid source. Choose 'vci' or 'tcbs'.")

    raw_data = raw_data.set_index("time")

    sma_, ema_, rsi_, marsi_, buy, sell = emamarsi(
        raw_data.close,
        ma,
        ema,
        rsi,
        marsi,
    )

    updated_data = raw_data.join(
        [
            sma_,
            ema_,
            rsi_,
            marsi_.rename("MARSI"),
            buy.rename("Buy"),
            sell.rename("Sell"),
        ]
    )
    return updated_data


def signal_builder(symbol, title, data):
    """Build signal message for Discord."""
    time = data.index[-1]
    price = data.close.iloc[-1]
    is_buy = bool(data.Buy.iloc[-1])
    is_sell = bool(data.Sell.iloc[-1])

    action = "BUY" if is_buy else "SELL" if is_sell else None

    if action is None:
        return False, f"__{time}__ {symbol} No signal"

    color = (
        DISCORD_POSITIVE_COLOR
        if is_buy
        else DISCORD_NEGATIVE_COLOR if is_sell else DISCORD_NEUTRAL_COLOR
    )
    content = f"*{symbol}* **{action}** {price}"
    description = f"__{time}__ **{action}** @ {price}"

    return True, {
        "username": "Signal BOT",
        "content": content,
        "embeds": [
            {
                "title": title,
                "description": description,
                "color": color,
            },
        ],
    }
