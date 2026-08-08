# Crypto Deep Alert

Sistema di monitoraggio automatico delle criptovalute più rilevanti.
Calcola drawdown, rialzi, volatilità, volume e momentum su più orizzonti temporali,
e invia un report via email con gli alert più significativi.

---

## Scopo del progetto

Crypto Deep Alert non dà consigli di acquisto o vendita.
Mostra esclusivamente dati quantitativi e alert informativi per supportare
l'osservazione manuale del mercato crypto.

Ogni valutazione finanziaria finale resta a carico dell'utente.

---

## Struttura progetto

```
crypto-deep-alert/
  config/
    settings.json          # configurazione generale, soglie alert, email
    crypto_catalog.json    # universo crypto monitorato
    market_cache.json      # cache dati di mercato (placeholder)
  src/
    main.py                # orchestratore principale
    indicators.py          # calcolo metriche e classificazione segnali
    crypto_data.py         # download storico prezzi via yfinance
    universe.py            # caricamento universo dal catalogo
    report_builder.py      # costruzione report HTML
    email_sender.py        # invio email via Brevo
  requirements.txt
  README.md
```

---

## Installazione dipendenze

```bash
pip install -r requirements.txt
```

---

## Configurazione .env

Crea un file `.env` nella root del progetto con queste variabili:

```
BREVO_API_KEY=la_tua_api_key_brevo
EMAIL_FROM=mittente@esempio.com
EMAIL_TO=destinatario@esempio.com
```

---

## Esecuzione locale

```bash
cd src
python main.py
```

---

## Significato degli alert

### Alert Negativi (ribassi)

Segnalano crypto in perdita rispetto ai massimi recenti del periodo selezionato (default: 1 anno).
Utili per monitorare drawdown importanti e fasi di debolezza del mercato.

| Livello             | Soglia drawdown         |
|---------------------|-------------------------|
| OSSERVAZIONE        | da -5% a -10%           |
| BASE                | da -10% a -20%          |
| MEDIO               | da -20% a -35%          |
| ALTO                | da -35% a -50%          |
| DRAWDOWN            | da -50% a -70%          |
| DRAWDOWN ESTREMO    | da -70% a -90%          |
| PERDITA CATASTROFICA| oltre -90%              |

### Alert Positivi (rialzi)

Segnalano crypto in forte guadagno rispetto ai minimi recenti del periodo selezionato.
Utili per monitorare momentum, recuperi forti o eccessi di rialzo.

| Livello             | Soglia guadagno         |
|---------------------|-------------------------|
| POSITIVO            | da +10% a +20%          |
| MOLTO POSITIVO      | da +20% a +40%          |
| FORTE RIALZO        | da +40% a +70%          |
| RIALZO MOLTO FORTE  | da +70% a +100%         |
| RIALZO ESTREMO      | oltre +100%             |

### Alert Depeg Stablecoin

Segnalano stablecoin che si allontanano dal valore teorico di 1 USD.
Non generano alert di rialzo/ribasso normali.

| Livello             | Scostamento assoluto    |
|---------------------|-------------------------|
| DEPEG LIEVE         | tra 0,5% e 1,0%         |
| DEPEG IMPORTANTE    | tra 1,0% e 5,0%         |
| DEPEG CRITICO       | oltre 5,0%              |

---

## Universo monitorato

- **Crypto principali**: Bitcoin, Ethereum, BNB, XRP, Solana, TRON, Dogecoin, Cardano,
  Chainlink, Stellar, Bitcoin Cash, Litecoin, Avalanche, Sui, Hedera, Shiba Inu,
  Uniswap, Cronos, Bittensor, NEAR Protocol, Polkadot, Aave, Monero, Zcash
- **Stablecoin** (solo depeg): Tether, USD Coin, Dai, PayPal USD
- **Oro tokenizzato**: Tether Gold, PAX Gold

---

## Disclaimer

> Questo report è solo informativo e non costituisce consulenza finanziaria.
> Le criptovalute sono strumenti altamente volatili e rischiosi.
> I dati possono essere incompleti, non aggiornati o non disponibili.
> Prima di qualsiasi decisione valuta rischio, orizzonte temporale, diversificazione,
> sicurezza degli exchange, custodia degli asset e situazione regolamentare.
