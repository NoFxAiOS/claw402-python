"""
Basic usage of the claw402 Python SDK.

Usage:
    WALLET_PRIVATE_KEY=0x... python examples/basic.py
"""

import os
from claw402 import Claw402

key = os.environ["WALLET_PRIVATE_KEY"]

with Claw402(private_key=key) as client:
    # 1. Fear & Greed Index (no params)
    print("=== Fear & Greed Index ===")
    sentiment = client.coinank.indicator.fear_greed()
    print(sentiment)

    # 2. Fund flow with params
    print("\n=== Fund Flow (SWAP, top 5) ===")
    flow = client.coinank.fund.realtime(product_type="SWAP", size=5)
    print(flow)

    # 3. AI500 signals
    print("\n=== AI500 Top Signals ===")
    ai500 = client.nofxos.ai500.list(limit=10)
    print(ai500)

    # 4. Net capital inflow ranking
    print("\n=== Net Inflow Top 10 (1h) ===")
    inflow = client.nofxos.netflow.top_ranking(limit=10, duration="1h")
    print(inflow)

    # 5. BTC price
    print("\n=== BTC Latest Price ===")
    price = client.coinank.price.last(
        symbol="BTCUSDT", exchange="Binance", product_type="SWAP"
    )
    print(price)
