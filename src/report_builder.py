from datetime import datetime

DISCLAIMER = (
    "Questo report è solo informativo e non costituisce consulenza finanziaria. "
    "Le criptovalute sono strumenti altamente volatili e rischiosi. "
    "I dati possono essere incompleti, non aggiornati o non disponibili. "
    "Prima di qualsiasi decisione valuta rischio, orizzonte temporale, diversificazione, "
    "sicurezza degli exchange, custodia degli asset e situazione regolamentare."
)


def build_subject(alerts: list[dict]) -> str:
    negative = sum(1 for a in alerts if a.get("alert_type") == "negative")
    positive = sum(1 for a in alerts if a.get("alert_type") == "positive")
    depeg = sum(1 for a in alerts if a.get("alert_type") == "stablecoin_depeg")
    parts = []
    if negative:
        parts.append(f"{negative} ribassi")
    if positive:
        parts.append(f"{positive} rialzi")
    if depeg:
        parts.append(f"{depeg} depeg")
    summary = ", ".join(parts) if parts else f"{len(alerts)} alert"
    return f"Crypto Deep Alert - {summary}"


def _fmt(value) -> str:
    if value is None:
        return "<span style='color:#94a3b8'>n/d</span>"
    return str(value)


def _fmt_pct(value) -> str:
    if value is None:
        return "<span style='color:#94a3b8'>n/d</span>"
    return f"{value:+.2f}%"


def _fmt_vol(value) -> str:
    if value is None:
        return "<span style='color:#94a3b8'>n/d</span>"
    v = float(value)
    if v >= 1_000_000_000:
        return f"{v / 1_000_000_000:.2f}B"
    if v >= 1_000_000:
        return f"{v / 1_000_000:.2f}M"
    if v >= 1_000:
        return f"{v / 1_000:.1f}K"
    return str(round(v, 2))


def _build_crypto_rows(alerts: list[dict]) -> str:
    if not alerts:
        return "<tr><td colspan='8' style='padding:12px;color:#64748b;'>Nessuna crypto sopra le soglie impostate.</td></tr>"

    rows = ""
    for a in alerts:
        color = a.get("signal_color", "#334155")
        bg = a.get("signal_background", "#f1f5f9")
        reasons = "<br>".join(a.get("reasons", []))
        category = a.get("category", "-")
        sector = a.get("sector", "-")

        rows += f"""
        <tr>
          <td style="border-bottom:1px solid #e2e8f0;padding:10px 8px;">
            <b>{_fmt(a.get('name'))}</b><br>
            <span style="color:#64748b;font-size:12px;">
              {_fmt(a.get('symbol'))} · {_fmt(a.get('tickerYahoo'))} · {category} · {sector}
            </span>
          </td>
          <td style="text-align:right;border-bottom:1px solid #e2e8f0;padding:10px 8px;">
            {_fmt(a.get('last_close'))}
          </td>
          <td style="text-align:right;border-bottom:1px solid #e2e8f0;padding:10px 8px;">
            {_fmt_pct(a.get('daily_change_pct'))}
          </td>
          <td style="text-align:right;border-bottom:1px solid #e2e8f0;padding:10px 8px;">
            {_fmt_pct(a.get('drop_from_high_pct_1m'))} /
            {_fmt_pct(a.get('drop_from_high_pct_3m'))} /
            {_fmt_pct(a.get('drop_from_high_pct_1y'))} /
            {_fmt_pct(a.get('drop_from_high_pct_5y'))} /
            {_fmt_pct(a.get('drop_from_high_pct_full'))}
          </td>
          <td style="text-align:right;border-bottom:1px solid #e2e8f0;padding:10px 8px;">
            {_fmt_pct(a.get('gain_from_low_pct_1m'))} /
            {_fmt_pct(a.get('gain_from_low_pct_3m'))} /
            {_fmt_pct(a.get('gain_from_low_pct_1y'))} /
            {_fmt_pct(a.get('gain_from_low_pct_5y'))} /
            {_fmt_pct(a.get('gain_from_low_pct_full'))}
          </td>
          <td style="text-align:right;border-bottom:1px solid #e2e8f0;padding:10px 8px;">
            {_fmt_pct(a.get('volatility_pct'))}<br>
            <span style="font-size:11px;color:#64748b;">
              Vol: {_fmt_vol(a.get('latest_volume'))} / avg {_fmt_vol(a.get('average_volume'))}
              ({_fmt_pct(a.get('volume_change_pct'))})
            </span>
          </td>
          <td style="border-bottom:1px solid #e2e8f0;padding:10px 8px;">
            <span style="display:inline-block;padding:4px 10px;border-radius:999px;background:{bg};color:{color};font-weight:700;font-size:12px;">
              {_fmt(a.get('signal'))}
            </span>
            <span style="font-size:11px;color:#64748b;display:block;margin-top:4px;">score: {a.get('score', '-')}</span>
          </td>
          <td style="border-bottom:1px solid #e2e8f0;padding:10px 8px;font-size:12px;color:#475569;">
            {reasons}
          </td>
        </tr>
        """
    return rows


def _build_depeg_rows(alerts: list[dict]) -> str:
    if not alerts:
        return "<tr><td colspan='5' style='padding:12px;color:#64748b;'>Nessuna stablecoin fuori peg.</td></tr>"

    rows = ""
    for a in alerts:
        color = a.get("signal_color", "#f97316")
        bg = a.get("signal_background", "#ffedd5")
        reasons = "<br>".join(a.get("reasons", []))
        price = a.get("stablecoin_price") or a.get("last_close")
        depeg_pct = a.get("depeg_pct")
        abs_depeg = a.get("abs_depeg_pct")

        rows += f"""
        <tr>
          <td style="border-bottom:1px solid #e2e8f0;padding:10px 8px;">
            <b>{_fmt(a.get('name'))}</b><br>
            <span style="color:#64748b;font-size:12px;">{_fmt(a.get('symbol'))} · {_fmt(a.get('tickerYahoo'))}</span>
          </td>
          <td style="text-align:right;border-bottom:1px solid #e2e8f0;padding:10px 8px;">{_fmt(price)}</td>
          <td style="text-align:right;border-bottom:1px solid #e2e8f0;padding:10px 8px;">1.0000</td>
          <td style="text-align:right;border-bottom:1px solid #e2e8f0;padding:10px 8px;">
            {_fmt_pct(depeg_pct)}<br>
            <span style="font-size:11px;color:#64748b;">abs: {_fmt_pct(abs_depeg)}</span>
          </td>
          <td style="border-bottom:1px solid #e2e8f0;padding:10px 8px;">
            <span style="display:inline-block;padding:4px 10px;border-radius:999px;background:{bg};color:{color};font-weight:700;font-size:12px;">
              {_fmt(a.get('signal'))}
            </span><br>
            <span style="font-size:12px;color:#475569;">{reasons}</span>
          </td>
        </tr>
        """
    return rows


def _section_crypto(title: str, color: str, rows: str, count: int) -> str:
    return f"""
    <h3 style="color:{color};margin-top:32px;margin-bottom:8px;">{title} ({count})</h3>
    <div style="overflow-x:auto;">
    <table cellpadding="0" cellspacing="0" style="border-collapse:collapse;width:100%;font-size:13px;min-width:900px;">
      <thead>
        <tr style="background:#e2e8f0;">
          <th align="left" style="padding:8px;">Crypto</th>
          <th align="right" style="padding:8px;">Prezzo</th>
          <th align="right" style="padding:8px;">Giorno</th>
          <th align="right" style="padding:8px;">DD 1m/3m/1y/5y/max</th>
          <th align="right" style="padding:8px;">Gain 1m/3m/1y/5y/max</th>
          <th align="right" style="padding:8px;">Volatilità / Volume</th>
          <th align="left" style="padding:8px;">Alert</th>
          <th align="left" style="padding:8px;">Note</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
    </div>
    """


def _section_depeg(title: str, rows: str, count: int) -> str:
    return f"""
    <h3 style="color:#f97316;margin-top:32px;margin-bottom:8px;">{title} ({count})</h3>
    <div style="overflow-x:auto;">
    <table cellpadding="0" cellspacing="0" style="border-collapse:collapse;width:100%;font-size:13px;min-width:600px;">
      <thead>
        <tr style="background:#e2e8f0;">
          <th align="left" style="padding:8px;">Stablecoin</th>
          <th align="right" style="padding:8px;">Prezzo</th>
          <th align="right" style="padding:8px;">Peg</th>
          <th align="right" style="padding:8px;">Scostamento</th>
          <th align="left" style="padding:8px;">Alert</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
    </div>
    """


def build_html(alerts: list[dict], skipped: list[dict], total_analyzed: int) -> str:
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    negative = [a for a in alerts if a.get("alert_type") == "negative"]
    positive = [a for a in alerts if a.get("alert_type") == "positive"]
    depeg = [a for a in alerts if a.get("alert_type") == "stablecoin_depeg"]

    neg_section = _section_crypto("📉 Alert Ribassi Crypto", "#dc2626", _build_crypto_rows(negative), len(negative)) if negative else ""
    pos_section = _section_crypto("📈 Alert Rialzi Crypto", "#16a34a", _build_crypto_rows(positive), len(positive)) if positive else ""
    dep_section = _section_depeg("⚠️ Alert Depeg Stablecoin", _build_depeg_rows(depeg), len(depeg)) if depeg else ""

    skipped_html = ""
    if skipped:
        items = "".join(
            f"<li>{s.get('name', s.get('symbol', '-'))} ({s.get('tickerYahoo', '-')}): {s.get('reason', '-')}</li>"
            for s in skipped[:20]
        )
        skipped_html = f"<h3 style='margin-top:28px;color:#64748b;'>Crypto saltate</h3><ul style='font-size:13px;color:#64748b;'>{items}</ul>"

    return f"""
    <html>
      <body style="font-family:Arial,sans-serif;color:#0f172a;background:#f8fafc;padding:24px;">
        <div style="max-width:1200px;margin:auto;background:white;border-radius:12px;padding:24px;border:1px solid #e2e8f0;">
          <h2 style="margin-top:0;">🪙 Crypto Deep Alert</h2>
          <p style="color:#475569;">
            <b>Data report:</b> {now}<br>
            <b>Crypto analizzate:</b> {total_analyzed}<br>
            <b>Alert rilevati:</b> {len(alerts)}
            ({len(negative)} ribassi, {len(positive)} rialzi, {len(depeg)} depeg stablecoin)
          </p>
          {neg_section}
          {pos_section}
          {dep_section}
          <p style="margin-top:28px;padding:14px;background:#fef9c3;border:1px solid #fde68a;border-radius:8px;color:#78350f;font-size:13px;">
            ⚠️ {DISCLAIMER}
          </p>
          {skipped_html}
        </div>
      </body>
    </html>
    """
