import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_json(relative_path: str, default=None):
    path = ROOT / relative_path
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_crypto_universe(settings: dict) -> list[dict]:
    universe_cfg = settings.get("universe", {})
    catalog_path = universe_cfg.get("catalog_path", "config/crypto_catalog.json")

    catalog = _load_json(catalog_path, default=[])
    if isinstance(catalog, dict):
        catalog = catalog.get("cryptos", [])

    if universe_cfg.get("include_enabled_watchlist_only", False):
        cryptos = [c for c in catalog if c.get("enabled")]
    elif universe_cfg.get("track_all_ready_from_catalog", True):
        cryptos = [c for c in catalog if c.get("status") == "ready" and c.get("tickerYahoo")]
    else:
        cryptos = [c for c in catalog if c.get("enabled") and c.get("status") == "ready" and c.get("tickerYahoo")]

    max_crypto = universe_cfg.get("max_enabled_crypto")
    if max_crypto:
        cryptos = cryptos[: int(max_crypto)]

    return cryptos
