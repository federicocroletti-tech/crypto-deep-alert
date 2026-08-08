import pandas as pd


def _period_metrics(close: pd.Series, volume: pd.Series | None, period_key: str) -> dict:
    if close is None or len(close) < 2:
        return {}

    last_close = float(close.iloc[-1])
    prev_close = float(close.iloc[-2])
    period_high = float(close.max())
    period_low = float(close.min())

    daily_change_pct = (last_close / prev_close - 1) * 100 if prev_close > 0 else 0.0
    drop_from_high_pct = (last_close / period_high - 1) * 100 if period_high > 0 else 0.0
    gain_from_low_pct = (last_close / period_low - 1) * 100 if period_low > 0 else 0.0
    volatility_pct = float(close.pct_change().std() * 100) if len(close) > 2 else 0.0

    result = {
        f"last_close_{period_key}": round(last_close, 6),
        f"prev_close_{period_key}": round(prev_close, 6),
        f"daily_change_pct_{period_key}": round(daily_change_pct, 2),
        f"period_high_{period_key}": round(period_high, 6),
        f"period_low_{period_key}": round(period_low, 6),
        f"drop_from_high_pct_{period_key}": round(drop_from_high_pct, 2),
        f"gain_from_low_pct_{period_key}": round(gain_from_low_pct, 2),
        f"volatility_pct_{period_key}": round(volatility_pct, 2),
    }

    if volume is not None and len(volume) >= 1:
        avg_vol = float(volume.mean())
        latest_vol = float(volume.iloc[-1])
        vol_change_pct = (latest_vol / avg_vol - 1) * 100 if avg_vol > 0 else 0.0
        result[f"average_volume_{period_key}"] = round(avg_vol, 0)
        result[f"latest_volume_{period_key}"] = round(latest_vol, 0)
        result[f"volume_change_pct_{period_key}"] = round(vol_change_pct, 2)

    return result


def compute_metrics(histories: dict) -> dict:
    metrics = {}

    for period_key, df in histories.items():
        if df is None or df.empty or "Close" not in df.columns:
            continue
        close = df["Close"].dropna()
        volume = df["Volume"].dropna() if "Volume" in df.columns else None
        metrics.update(_period_metrics(close, volume, period_key))

    # alias principali sul periodo 1y
    primary = "1y"
    metrics["last_close"] = metrics.get(f"last_close_{primary}")
    metrics["prev_close"] = metrics.get(f"prev_close_{primary}")
    metrics["daily_change_pct"] = metrics.get(f"daily_change_pct_{primary}")
    metrics["drop_from_high_pct"] = metrics.get(f"drop_from_high_pct_{primary}")
    metrics["gain_from_low_pct"] = metrics.get(f"gain_from_low_pct_{primary}")
    metrics["volatility_pct"] = metrics.get(f"volatility_pct_{primary}")
    metrics["average_volume"] = metrics.get(f"average_volume_{primary}")
    metrics["latest_volume"] = metrics.get(f"latest_volume_{primary}")
    metrics["volume_change_pct"] = metrics.get(f"volume_change_pct_{primary}")

    return metrics


def classify_signal(
    metrics: dict,
    negative_levels: dict,
    positive_levels: dict,
    stablecoin_depeg_levels: dict,
    asset_meta: dict,
) -> tuple[str, int, list[str], dict, str | None]:

    if asset_meta.get("isStablecoin"):
        return _classify_stablecoin_depeg(metrics, stablecoin_depeg_levels)

    neg = _classify_negative(metrics, negative_levels)
    pos = _classify_positive(metrics, positive_levels)

    if neg and pos:
        if neg["score"] >= pos["score"]:
            return neg["signal"], neg["score"], neg["reasons"], neg["level_cfg"], "negative"
        return pos["signal"], pos["score"], pos["reasons"], pos["level_cfg"], "positive"

    if neg:
        return neg["signal"], neg["score"], neg["reasons"], neg["level_cfg"], "negative"
    if pos:
        return pos["signal"], pos["score"], pos["reasons"], pos["level_cfg"], "positive"

    return "NESSUNO", 0, [], {}, None


def _classify_negative(metrics: dict, negative_levels: dict) -> dict | None:
    drop = metrics.get("drop_from_high_pct")
    if drop is None:
        return None

    for score, (level_key, cfg) in enumerate(negative_levels.items(), start=1):
        min_drop = cfg.get("min_drop_pct")
        max_drop = cfg.get("max_drop_pct")
        if min_drop is None:
            continue
        if max_drop is None:
            matches = drop <= min_drop
        else:
            matches = max_drop <= drop <= min_drop
        if matches:
            desc = cfg.get("description", f"Ribasso dal massimo: {drop:.2f}%.")
            return {
                "signal": cfg.get("label", level_key.upper()),
                "score": score,
                "reasons": [f"{desc} Valore rilevato: {drop:.2f}%."],
                "level_cfg": cfg,
            }
    return None


def _classify_positive(metrics: dict, positive_levels: dict) -> dict | None:
    gain = metrics.get("gain_from_low_pct")
    if gain is None:
        return None

    for score, (level_key, cfg) in enumerate(positive_levels.items(), start=1):
        min_gain = cfg.get("min_gain_pct")
        max_gain = cfg.get("max_gain_pct")
        if min_gain is None:
            continue
        if max_gain is None:
            matches = gain >= min_gain
        else:
            matches = min_gain <= gain <= max_gain
        if matches:
            desc = cfg.get("description", f"Guadagno dal minimo: {gain:.2f}%.")
            return {
                "signal": cfg.get("label", level_key.upper()),
                "score": score,
                "reasons": [f"{desc} Valore rilevato: {gain:.2f}%."],
                "level_cfg": cfg,
            }
    return None


def _classify_stablecoin_depeg(metrics: dict, depeg_levels: dict) -> tuple[str, int, list[str], dict, str | None]:
    price = metrics.get("last_close")
    if price is None:
        return "NESSUNO", 0, [], {}, None

    peg = 1.0
    depeg_pct = (price - peg) / peg * 100
    abs_depeg = abs(depeg_pct)

    for score, (level_key, cfg) in enumerate(depeg_levels.items(), start=1):
        min_dep = cfg.get("min_abs_depeg_pct")
        max_dep = cfg.get("max_abs_depeg_pct")
        if min_dep is None:
            continue
        if max_dep is None:
            matches = abs_depeg >= min_dep
        else:
            matches = min_dep <= abs_depeg < max_dep
        if matches:
            desc = cfg.get("description", f"Depeg rilevato: {depeg_pct:.3f}%.")
            return (
                cfg.get("label", level_key.upper()),
                score,
                [f"{desc} Prezzo: {price:.4f} USD. Scostamento: {depeg_pct:+.3f}%."],
                cfg,
                "stablecoin_depeg",
            )

    return "NESSUNO", 0, [], {}, None
