# claw402

[![PyPI version](https://img.shields.io/pypi/v/claw402.svg)](https://pypi.org/project/claw402/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Typed Python SDK for [claw402.ai](https://claw402.ai) — pay-per-call data APIs via [x402](https://www.x402.org/) micropayments.

**200+ endpoints** covering crypto market data, US stocks, China A-shares, forex, global time-series, and AI (OpenAI/Anthropic). No API key, no signup, no subscription — just a Base wallet with USDC.

## Install

```bash
pip install git+https://github.com/NoFxAiOS/claw402-python.git
```

## Quick Start

```python
from claw402 import Claw402

client = Claw402(private_key="0xYourPrivateKey")

# Crypto: Fund flow — $0.001/call
flow = client.coinank.fund.realtime(product_type="SWAP")
print(flow)

# US Stocks: Latest quote — $0.001/call
quote = client.alpaca.quotes.latest(symbols="AAPL,TSLA")
print(quote)

# US Stocks: Market snapshot — $0.002/call
snap = client.polygon.snapshot.all(tickers="AAPL")
print(snap)

# China A-shares — $0.001/call
stocks = client.tushare.cn.stock_basic(list_status="L")
print(stocks)

# Forex time-series — $0.001/call
ts = client.twelvedata.get_time_series(symbol="EUR/USD", interval="1h")
print(ts)

# AI: OpenAI chat — $0.01/call
resp = client.openai.openai.chat({"messages": [{"role": "user", "content": "Hello"}]})
print(resp)

# AI: Anthropic Claude — $0.015/call
resp = client.anthropic.anthropic.messages({"messages": [{"role": "user", "content": "Hello"}]})
print(resp)
```

## Features

- **Typed methods** — every endpoint has a dedicated Python method with keyword arguments
- **Automatic x402 payment** — signs EIP-3009 USDC transfers locally, never sends your key
- **9 provider groups** — crypto, US stocks, China stocks, forex, global data, and AI
- **Context manager** — `with Claw402(...) as client:` for automatic cleanup
- **Zero config** — just a private key, no API keys or registration
- **Base mainnet** — pays USDC per call on Coinbase L2

## API Overview

### Crypto Market Data

#### Coinank

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

#### Nofxos (AI Signals)

| Resource | Methods | Description |
|----------|---------|-------------|
| `nofxos.ai500` | `list`, `stats` | AI500 high-potential coin signals |
| `nofxos.ai300` | `list`, `stats` | AI300 quant model rankings |
| `nofxos.netflow` | `top_ranking`, `low_ranking` | Net capital flow rankings |
| `nofxos.oi` | `top_ranking`, `low_ranking` | OI change rankings |
| `nofxos.funding_rate` | `top`, `low` | Extreme funding rate coins |
| `nofxos.price` | `ranking` | Price change rankings |
| `nofxos.upbit` | `hot`, `netflow_top_ranking`, `netflow_low_ranking` | Korean market data |

### US Stock & Options Market

#### Alpaca

| Resource | Methods | Description |
|----------|---------|-------------|
| `alpaca.quotes` | `latest`, `history` | Real-time & historical quotes — $0.001–0.002/call |
| `alpaca.bars` | `latest` | Latest OHLCV bar — $0.001/call |
| `alpaca.trades` | `latest`, `history` | Real-time & historical trades — $0.001–0.002/call |
| `alpaca.options` | `bars`, `quotes_latest`, `snapshots` | Options chain data — $0.003/call |
| `alpaca` | `get_bars`, `snapshots`, `snapshot`, `movers`, `most_actives`, `news`, `corporate_actions` | Direct market endpoints — $0.001–0.002/call |

```python
# Latest quotes for multiple symbols
q = client.alpaca.quotes.latest(symbols="AAPL,MSFT,TSLA")

# Historical bars
bars = client.alpaca.get_bars(symbols="AAPL", timeframe="1Day", start="2024-01-01")

# Top market movers
movers = client.alpaca.movers(top=10, market_type="stocks")

# Options snapshots
opts = client.alpaca.options.snapshots(symbols="AAPL240119C00150000")
```

#### Polygon

| Resource | Methods | Description |
|----------|---------|-------------|
| `polygon.aggs` | `aggs`, `grouped_daily`, `daily_open_close`, `previous_close` | Aggregates / OHLCV bars — $0.001/call |
| `polygon.snapshots` | `all_tickers`, `single_ticker`, `gainers_losers`, `universal_snapshot`, `options_chain` | Full market snapshots — $0.002/call |
| `polygon.trades` | `trades`, `last_trade`, `quotes`, `last_quote` | Trade & quote tick data — $0.002/call |
| `polygon` | `ticker_details`, `market_status`, `ticker_types`, `exchanges`, `conditions`, `sma`, `ema`, `rsi`, `macd` | Reference & technical indicators — $0.001–0.003/call |

```python
# OHLCV bars
bars = client.polygon.aggs.aggs(
    stocksTicker="AAPL", multiplier=1, timespan="day",
    from_="2024-01-01", to="2024-12-31"
)

# RSI indicator
rsi = client.polygon.rsi(stocksTicker="AAPL", timespan="day", window=14)

# Options chain
chain = client.polygon.snapshots.options_chain(underlyingAsset="AAPL")
```

#### Alpha Vantage

| Resource | Methods | Description |
|----------|---------|-------------|
| `alphavantage.us` | `quote`, `search`, `daily`, `daily_adjusted`, `intraday`, `weekly`, `monthly`, `overview`, `earnings`, `income`, `balance_sheet`, `cash_flow`, `movers`, `news`, `rsi`, `macd`, `bbands`, `sma`, `ema` | Comprehensive financial data — $0.001–0.003/call |

```python
# Real-time quote
quote = client.alphavantage.us.quote(symbol="AAPL")

# Daily OHLCV
daily = client.alphavantage.us.daily(symbol="AAPL", outputsize="compact")

# Top movers (no params)
movers = client.alphavantage.us.movers()

# News sentiment
news = client.alphavantage.us.news(tickers="AAPL")
```

### China A-Shares

#### Tushare

| Resource | Methods | Description |
|----------|---------|-------------|
| `tushare.cn` | `stock_basic`, `daily`, `weekly`, `monthly`, `daily_basic`, `trade_cal`, `income`, `balance_sheet`, `cash_flow`, `dividend`, `northbound`, `moneyflow`, `margin`, `margin_detail`, `top_list`, `top_inst` | China A-share market data — $0.001–0.003/call |

```python
# Stock list
stocks = client.tushare.cn.stock_basic(list_status="L")

# Daily OHLCV
daily = client.tushare.cn.daily(ts_code="000001.SZ", start_date="20240101", end_date="20240131")

# Money flow
flow = client.tushare.cn.moneyflow(ts_code="000001.SZ", start_date="20240101")

# Northbound capital
north = client.tushare.cn.northbound(trade_date="20240101")
```

### Global Time-Series & Forex

#### Twelve Data

| Resource | Methods | Description |
|----------|---------|-------------|
| `twelvedata.time_series` | `complex` (POST) | Complex multi-symbol/indicator query — $0.005/call |
| `twelvedata.indicator` | `sma`, `ema`, `rsi`, `macd`, `bbands`, `atr` | Technical indicators — $0.002/call |
| `twelvedata.metals` | `price`, `time_series` | Precious metals prices — $0.001/call |
| `twelvedata.indices` | `list_`, `quote` | Global index data — $0.001/call |
| `twelvedata` | `get_time_series`, `price`, `quote`, `eod`, `exchange_rate`, `forex_pairs`, `economic_calendar` | Direct endpoints — $0.001/call |

```python
# Time series (use get_time_series, NOT time_series — time_series is the sub-resource)
ts = client.twelvedata.get_time_series(symbol="EUR/USD", interval="1h", outputsize=3)

# Technical indicators
rsi = client.twelvedata.indicator.rsi(symbol="AAPL", interval="1day", time_period=14, outputsize=3)

# Real-time price
price = client.twelvedata.price(symbol="BTC/USD")

# Metals
gold = client.twelvedata.metals.price(symbol="XAU/USD")
```

### AI Providers

#### OpenAI

| Resource | Methods | Description |
|----------|---------|-------------|
| `openai.openai` | `chat`, `chat_mini`, `embeddings`, `embeddings_large`, `images`, `models` | OpenAI API — $0.001–0.05/call |

```python
# Chat (GPT-4o)
resp = client.openai.openai.chat({
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Analyze AAPL stock trend"}]
})

# Embeddings
emb = client.openai.openai.embeddings({
    "input": "crypto market sentiment",
    "model": "text-embedding-3-small"
})
```

#### Anthropic

| Resource | Methods | Description |
|----------|---------|-------------|
| `anthropic.anthropic` | `messages`, `messages_extended`, `count_tokens` | Anthropic Claude API — $0.01–0.015/call |

```python
# Claude messages
resp = client.anthropic.anthropic.messages({
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Summarize this earnings report: ..."}]
})
```

## Configuration

```python
# Custom base URL
client = Claw402(
    private_key="0x...",
    base_url="https://custom.gateway",
)
```

## How Payment Works

1. SDK sends a GET/POST request to the endpoint
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
