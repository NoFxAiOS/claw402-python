# claw402

[![PyPI version](https://img.shields.io/pypi/v/claw402.svg)](https://pypi.org/project/claw402/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Typed Python SDK for [claw402.ai](https://claw402.ai) — pay-per-call crypto data APIs via [x402](https://www.x402.org/) micropayments.

**96+ endpoints** covering fund flow, liquidations, ETF flows, AI trading signals, whale tracking, funding rates, open interest, and more. No API key, no signup, no subscription — just a Base wallet with USDC.

## Install

```bash
pip install git+https://github.com/NoFxAiOS/claw402-python.git
```

## Quick Start

```python
from claw402 import Claw402

client = Claw402(private_key="0xYourPrivateKey")

# Fund flow — $0.001 per call
flow = client.coinank.fund.realtime(product_type="SWAP")
print(flow)

# AI trading signals
signals = client.nofxos.netflow.top_ranking(limit=20, duration="1h")
print(signals)

# Fear & Greed Index
sentiment = client.coinank.indicator.fear_greed()
print(sentiment)
```

## Features

- **Typed methods** — every endpoint has a dedicated Python method with keyword arguments
- **Automatic x402 payment** — signs EIP-3009 USDC transfers locally, never sends your key
- **Two resource groups** — `client.coinank.*` (market data) and `client.nofxos.*` (AI signals)
- **Context manager** — `with Claw402(...) as client:` for automatic cleanup
- **Zero config** — just a private key, no API keys or registration
- **Base mainnet** — pays $0.001 USDC per call on Coinbase L2

## API Overview

### Coinank (Market Data)

| Resource | Methods | Description |
|----------|---------|-------------|
| `coinank.fund` | `realtime`, `history` | Real-time & historical fund flow |
| `coinank.oi` | `all`, `agg_chart`, `symbol_chart`, `kline`, ... | Open interest data |
| `coinank.liquidation` | `orders`, `intervals`, `agg_history`, `liq_map`, `heat_map`, ... | Liquidation tracking |
| `coinank.funding_rate` | `current`, `accumulated`, `hist`, `weighted`, `heatmap`, ... | Funding rate analytics |
| `coinank.longshort` | `realtime`, `buy_sell`, `person`, `position`, ... | Long/short ratios |
| `coinank.hyper` | `top_position`, `top_action` | HyperLiquid whale tracking |
| `coinank.etf` | `us_btc`, `us_eth`, `us_btc_inflow`, `us_eth_inflow`, `hk_inflow` | ETF flow data |
| `coinank.indicator` | `fear_greed`, `altcoin_season`, `btc_multiplier`, `ahr999`, ... | Market cycle indicators |
| `coinank.market_order` | `cvd`, `agg_cvd`, `buy_sell_value`, ... | Taker flow / CVD |
| `coinank.kline` | `lists` | OHLCV candlestick data |
| `coinank.price` | `last` | Real-time price |
| `coinank.rank` | `screener`, `oi`, `volume`, `price`, `liquidation`, ... | Rankings & screeners |
| `coinank.news` | `list`, `detail` | Crypto news & alerts |

### Nofxos (AI Signals)

| Resource | Methods | Description |
|----------|---------|-------------|
| `nofxos.ai500` | `list`, `stats` | AI500 high-potential coin signals |
| `nofxos.ai300` | `list`, `stats` | AI300 quant model rankings |
| `nofxos.netflow` | `top_ranking`, `low_ranking` | Net capital flow rankings |
| `nofxos.oi` | `top_ranking`, `low_ranking` | OI change rankings |
| `nofxos.funding_rate` | `top`, `low` | Extreme funding rate coins |
| `nofxos.price` | `ranking` | Price change rankings |
| `nofxos.upbit` | `hot`, `netflow_top_ranking`, `netflow_low_ranking` | Korean market data |

## Configuration

```python
# Custom base URL
client = Claw402(
    private_key="0x...",
    base_url="https://custom.gateway",
)
```

## How Payment Works

1. SDK sends a GET request to the endpoint
2. Server responds with `402 Payment Required` + payment details in header
3. SDK signs an EIP-3009 `TransferWithAuthorization` for USDC on Base
4. SDK retries the request with the `PAYMENT-SIGNATURE` header
5. Server verifies payment on-chain and returns the data

Your private key **never leaves your machine** — it only signs the payment locally.

## Requirements

- Python 3.9+
- A wallet with USDC on [Base mainnet](https://base.org)
- Get USDC on Base: [bridge.base.org](https://bridge.base.org)

## License

MIT
