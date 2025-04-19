import pandas as pd


POSITIVE_BACKGROUND = "background-color: lightgreen; color: black;"
NEGATIVE_BACKGROUND = "background-color: lightcoral; color: black;"
POSITIVE_TEXT = "color: green; font-weight: bold;"
NEGATIVE_TEXT = "color: coral; font-weight: bold;"


def highlight_cells(row: pd.Series):
    styles = ["" for _ in row]

    idx = {col: i for i, col in enumerate(row.index)}

    if row["Buy"] == 1:
        styles[idx["Buy"]] = POSITIVE_BACKGROUND
        styles[idx["close"]] = POSITIVE_BACKGROUND

    if row["Sell"] == 1:
        styles[idx["Sell"]] = NEGATIVE_BACKGROUND
        styles[idx["close"]] = NEGATIVE_BACKGROUND

    sma = row["SMA_5"]
    ema = row["EMA_3"]
    if pd.notna(sma) and pd.notna(ema):
        if sma > ema:
            styles[idx["SMA_5"]] += NEGATIVE_TEXT
        elif ema > sma:
            styles[idx["EMA_3"]] += POSITIVE_TEXT

    rsi = row["RSI_14"]
    marsi = row["MARSI"]
    if pd.notna(rsi) and pd.notna(marsi):
        if rsi > marsi:
            styles[idx["RSI_14"]] += POSITIVE_TEXT
        elif marsi > rsi:
            styles[idx["MARSI"]] += NEGATIVE_TEXT

    return styles


def format_dataframe(df: pd.DataFrame):
    """Format DataFrame for display."""
    styled_df = df.set_index("time").style.apply(highlight_cells, axis=1)

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
