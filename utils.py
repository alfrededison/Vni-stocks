import pandas as pd


POSITIVE_BACKGROUND = "background-color: lightgreen; color: black;"
NEGATIVE_BACKGROUND = "background-color: lightcoral; color: black;"
POSITIVE_TEXT = "color: green; font-weight: bold;"
NEGATIVE_TEXT = "color: coral; font-weight: bold;"


def highlight_signals(row: pd.Series):
    styles = ["" for _ in row]

    idx = {col: i for i, col in enumerate(row.index)}

    if row["Buy"] == 1:
        styles[idx["Buy"]] = POSITIVE_BACKGROUND
        styles[idx["close"]] = POSITIVE_BACKGROUND

    if row["Sell"] == 1:
        styles[idx["Sell"]] = NEGATIVE_BACKGROUND
        styles[idx["close"]] = NEGATIVE_BACKGROUND

    sma = row["sma_5"]
    ema = row["ema_3"]
    if pd.notna(sma) and pd.notna(ema):
        if sma > ema:
            styles[idx["sma_5"]] += NEGATIVE_TEXT
        elif ema > sma:
            styles[idx["ema_3"]] += POSITIVE_TEXT

    rsi = row["rsi"]
    marsi = row["MA-RSI"]
    if pd.notna(rsi) and pd.notna(marsi):
        if rsi > marsi:
            styles[idx["rsi"]] += POSITIVE_TEXT
        elif marsi > rsi:
            styles[idx["MA-RSI"]] += NEGATIVE_TEXT

    return styles


def highlight_stocks(row: pd.Series):
    styles = ["" for _ in row]

    idx = {col: i for i, col in enumerate(row.index)}

    if row["revenueGrowth1Year"] >= 20:
        styles[idx["revenueGrowth1Year"]] = POSITIVE_BACKGROUND

    if row["revenueGrowth5Year"] >= 20:
        styles[idx["revenueGrowth5Year"]] = POSITIVE_BACKGROUND

    if row["epsGrowth1Year"] >= 20:
        styles[idx["epsGrowth1Year"]] = POSITIVE_BACKGROUND

    if row["epsGrowth5Year"] >= 20:
        styles[idx["epsGrowth5Year"]] = POSITIVE_BACKGROUND

    if row["lastQuarterProfitGrowth"] >= 20:
        styles[idx["lastQuarterProfitGrowth"]] = POSITIVE_BACKGROUND

    if row["secondQuarterProfitGrowth"] >= 20:
        styles[idx["secondQuarterProfitGrowth"]] = POSITIVE_BACKGROUND

    if row["netMargin"] >= 10:
        styles[idx["netMargin"]] = POSITIVE_BACKGROUND

    if row["avgTradingValue5Day"] >= 10:
        styles[idx["avgTradingValue5Day"]] = POSITIVE_BACKGROUND

    if row["hasFinancialReport.en"] == "Yes":
        styles[idx["hasFinancialReport.en"]] = POSITIVE_BACKGROUND
    else:
        styles[idx["hasFinancialReport.en"]] = NEGATIVE_BACKGROUND

    if row["relativeStrength3Day"] >= 80:
        styles[idx["relativeStrength3Day"]] = POSITIVE_BACKGROUND

    if row["relativeStrength1Month"] >= 80:
        styles[idx["relativeStrength1Month"]] = POSITIVE_BACKGROUND

    return styles


def format_dataframe(df: pd.DataFrame, highlight_cells):
    """Format DataFrame for display."""
    styled_df = df.style.apply(highlight_cells, axis=1)

    # Thêm hiệu ứng hover theo điều kiện
    styled_df = styled_df.set_table_styles(
        [
            {
                "selector": "tbody tr:hover",
                "props": [("background-color", "#eef")],
            }
        ],
        overwrite=False,
    )

    return styled_df.format(precision=2)
