import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from crypto_data import download_history
from indicators import compute_metrics, classify_signal
from universe import load_crypto_universe
from report_builder import build_html, build_subject
from email_sender import send_brevo_email

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str) -> dict:
    with open(ROOT / path, "r", encoding="utf-8") as f:
        return json.load(f)


def download_histories(ticker: str, data_cfg: dict) -> dict:
    interval = data_cfg.get("interval", "1d")
    periods_cfg = data_cfg.get("periods", {})
    histories = {}
    for key, yahoo_period in periods_cfg.items():
        try:
            histories[key] = download_history(ticker, period=yahoo_period, interval=interval)
        except Exception:
            histories[key] = None
    return histories


def get_alert_sort_key(alert: dict):
    atype = alert.get("alert_type")
    if atype == "negative":
        return (alert.get("score", 0), abs(alert.get("drop_from_high_pct") or 0))
    if atype == "positive":
        return (alert.get("score", 0), alert.get("gain_from_low_pct") or 0)
    return (alert.get("score", 0), 0)


def main():
    settings = load_json("config/settings.json")
    data_cfg = settings["data"]
    negative_levels = settings["alertLevels"]["negative"]
    positive_levels = settings["alertLevels"]["positive"]
    depeg_levels = settings["alertLevels"]["stablecoin_depeg"]
    alert_categories = settings.get("alertCategories", {})

    neg_enabled = alert_categories.get("negative_alerts", {}).get("enabled", True)
    pos_enabled = alert_categories.get("positive_alerts", {}).get("enabled", True)
    depeg_enabled = alert_categories.get("stablecoin_depeg_alerts", {}).get("enabled", True)

    cryptos = load_crypto_universe(settings)

    alerts = []
    skipped = []

    for crypto in cryptos:
        ticker = crypto.get("tickerYahoo")
        if not ticker:
            skipped.append({**crypto, "reason": "tickerYahoo mancante"})
            continue

        try:
            histories = download_histories(ticker, data_cfg)
            metrics = compute_metrics(histories)

            signal, score, reasons, level_cfg, alert_type = classify_signal(
                metrics=metrics,
                negative_levels=negative_levels,
                positive_levels=positive_levels,
                stablecoin_depeg_levels=depeg_levels,
                asset_meta=crypto,
            )

            if signal == "NESSUNO":
                continue

            # rispetta le categorie abilitate
            if alert_type == "negative" and not neg_enabled:
                continue
            if alert_type == "positive" and not pos_enabled:
                continue
            if alert_type == "stablecoin_depeg" and not depeg_enabled:
                continue

            price = metrics.get("last_close")
            depeg_pct = None
            abs_depeg_pct = None
            if crypto.get("isStablecoin") and price is not None:
                depeg_pct = round((price - 1.0) / 1.0 * 100, 4)
                abs_depeg_pct = round(abs(depeg_pct), 4)

            alerts.append({
                "symbol": crypto.get("symbol"),
                "name": crypto.get("name"),
                "tickerYahoo": ticker,
                "category": crypto.get("category"),
                "sector": crypto.get("sector"),
                "isStablecoin": crypto.get("isStablecoin", False),
                "isTokenizedGold": crypto.get("isTokenizedGold", False),
                "alert_type": alert_type,
                "signal": signal,
                "score": score,
                "reasons": reasons,
                "signal_color": level_cfg.get("color", "#334155"),
                "signal_background": level_cfg.get("background", "#f1f5f9"),
                "stablecoin_price": price if crypto.get("isStablecoin") else None,
                "depeg_pct": depeg_pct,
                "abs_depeg_pct": abs_depeg_pct,
                "peg_reference": 1.0 if crypto.get("isStablecoin") else None,
                **metrics,
            })

        except Exception as exc:
            skipped.append({**crypto, "reason": str(exc)})

    alerts.sort(key=get_alert_sort_key, reverse=True)

    max_items = settings["report"].get("max_items_in_email", 30)
    alerts = alerts[:max_items]

    negative_count = sum(1 for a in alerts if a.get("alert_type") == "negative")
    positive_count = sum(1 for a in alerts if a.get("alert_type") == "positive")
    depeg_count = sum(1 for a in alerts if a.get("alert_type") == "stablecoin_depeg")

    print(f"Crypto analizzate:          {len(cryptos)}")
    print(f"Alert rilevati:             {len(alerts)}")
    print(f"Alert negativi:             {negative_count}")
    print(f"Alert positivi:             {positive_count}")
    print(f"Alert depeg stablecoin:     {depeg_count}")
    print(f"Crypto saltate:             {len(skipped)}")

    if skipped:
        print("\nCrypto saltate:")
        for s in skipped:
            print(f"  - {s.get('name', '-')} ({s.get('tickerYahoo', '-')}): {s.get('reason', '-')}")

    if not alerts and not settings["report"].get("send_email_if_no_alerts", False):
        print("\nNessun alert rilevato. Email non inviata.")
        sys.exit(0)

    subject = build_subject(alerts)
    html = build_html(alerts, skipped, total_analyzed=len(cryptos))
    result = send_brevo_email(subject, html, settings)
    print(f"\nEmail inviata: {result}")


if __name__ == "__main__":
    main()
