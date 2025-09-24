from __future__ import annotations
import pandas as pd
import ta  # technical analysis lib

def compute_indicators(price_df: pd.DataFrame) -> pd.DataFrame:
    df = price_df.copy()

    # Series'e dönüştür (2D -> 1D fix)
    high = df["High"].astype(float).squeeze()
    low = df["Low"].astype(float).squeeze()
    close = df["Close"].astype(float).squeeze()

    # SMA
    df["SMA50"] = close.rolling(50).mean()
    df["SMA200"] = close.rolling(200).mean()

    # RSI
    df["RSI14"] = ta.momentum.RSIIndicator(close=close, window=14).rsi()

    # MACD
    macd = ta.trend.MACD(close=close)
    df["MACD"] = macd.macd()
    df["MACD_SIGNAL"] = macd.macd_signal()
    df["MACD_HIST"] = macd.macd_diff()

    # Bollinger
    bb = ta.volatility.BollingerBands(close=close, window=20, window_dev=2)
    df["BB_UPPER"] = bb.bollinger_hband()
    df["BB_LOWER"] = bb.bollinger_lband()

    # ATR
    atr = ta.volatility.AverageTrueRange(
        high=high,
        low=low,
        close=close,
        window=14,
    ).average_true_range()
    df["ATR14"] = atr

    # Sinyaller
    df["AboveSMA200"] = (close > df["SMA200"]).astype(int)
    df["MACD_Bull"] = (df["MACD"] > df["MACD_SIGNAL"]).astype(int)

    return df

def latest_signals(ind_df: pd.DataFrame) -> dict:
    # Tek satır DataFrame -> Series
    last = ind_df.iloc[[-1]].squeeze()

    return {
        "price": float(last["Close"].item() if isinstance(last["Close"], pd.Series) else last["Close"]),
        "sma50": float(last["SMA50"].item() if isinstance(last["SMA50"], pd.Series) else last["SMA50"]),
        "sma200": float(last["SMA200"].item() if isinstance(last["SMA200"], pd.Series) else last["SMA200"]),
        "rsi14": float(last["RSI14"].item() if isinstance(last["RSI14"], pd.Series) else last["RSI14"]),
        "macd_bull": bool((last["MACD"].item() if isinstance(last["MACD"], pd.Series) else last["MACD"]) >
                          (last["MACD_SIGNAL"].item() if isinstance(last["MACD_SIGNAL"], pd.Series) else last["MACD_SIGNAL"])),
        "above_sma200": bool((last["Close"].item() if isinstance(last["Close"], pd.Series) else last["Close"]) >
                              (last["SMA200"].item() if isinstance(last["SMA200"], pd.Series) else last["SMA200"])),
        "bb_lower": float(last["BB_LOWER"].item() if isinstance(last["BB_LOWER"], pd.Series) else last["BB_LOWER"]),
        "bb_upper": float(last["BB_UPPER"].item() if isinstance(last["BB_UPPER"], pd.Series) else last["BB_UPPER"]),
        "atr14": float(last["ATR14"].item() if isinstance(last["ATR14"], pd.Series) else last["ATR14"]),
    }

