import pandas as pd
import yfinance as yf


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
        df.columns = df.columns.get_level_values(0)
    return df


def download_history(ticker: str, period: str, interval: str = "1d") -> pd.DataFrame:
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
        df = _normalize(df)
    except Exception as exc:
        raise RuntimeError(f"Errore download yfinance per {ticker}: {exc}") from exc

    if df.empty or "Close" not in df.columns:
        raise RuntimeError(f"Nessun dato disponibile per {ticker} (periodo: {period})")

    return df
