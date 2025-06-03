from datetime import datetime, timedelta
import ta

from const import ACTION_BUY, ACTION_SELL
from vci import history as vci_history
from tcbs import history as tcbs_history


def get_past_date(x):
    past_date = datetime.today() - timedelta(days=x)
    return past_date.strftime("%Y-%m-%d")


def emamarsi(close, ma, ema, rsi, marsi):
    sma_ = ta.trend.SMAIndicator(close, ma).sma_indicator()
    ema_ = ta.trend.EMAIndicator(close, ema).ema_indicator()
    rsi_ = ta.momentum.RSIIndicator(close, rsi).rsi()
    marsi_ = ta.trend.SMAIndicator(rsi_, marsi).sma_indicator()

    price_up = ta.momentum.ROCIndicator(close, 1).roc() > 0
    rsi_up = rsi_ > marsi_
    buy = ta.utils.crossed_above(ema_, sma_) & rsi_up & price_up
    sell = ta.utils.crossed_below(ema_, sma_)
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
            sma_.rename("sma"),
            ema_.rename("ema"),
            rsi_.rename("rsi"),
            marsi_.rename("ma_rsi"),
            buy.rename("Buy"),
            sell.rename("Sell"),
        ]
    )
    return updated_data


def signal_builder(symbol, data):
    """Build signal message for Discord."""
    time = data.index[-1]
    price = data.close.iloc[-1]
    is_buy = bool(data.Buy.iloc[-1])
    is_sell = bool(data.Sell.iloc[-1])

    action = ACTION_BUY if is_buy else ACTION_SELL if is_sell else None

    if action is None:
        return False, {
            "description": f"__{time}__ {symbol} No signal",
        }

    content = f"*{symbol}* **{action}** {price}"
    description = f"__{time}__ {symbol} **{action}** @ {price}"

    return True, {
        "action": action,
        "content": content,
        "description": description,
    }
