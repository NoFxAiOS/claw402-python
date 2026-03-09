import base64
import json
import secrets
import time

import requests
from eth_account import Account

from .errors import Claw402Error
from .generated.alpaca import AlpacaResource
from .generated.alphavantage import AlphavantageResource
from .generated.anthropic import AnthropicResource
from .generated.coinank import CoinankResource
from .generated.deepseek import DeepseekResource
from .generated.gemini import GeminiResource
from .generated.grok import GrokResource
from .generated.kimi import KimiResource
from .generated.nofxos import NofxosResource
from .generated.openai import OpenaiResource
from .generated.polygon import PolygonResource
from .generated.qwen import QwenResource
from .generated.rootdata import RootdataResource
from .generated.tushare import TushareResource
from .generated.twelvedata import TwelvedataResource

# Base chain ID (Coinbase L2)
BASE_CHAIN_ID = 8453

# EIP-3009 TransferWithAuthorization typed data types
TRANSFER_WITH_AUTHORIZATION_TYPES = {
    "TransferWithAuthorization": [
        {"name": "from", "type": "address"},
        {"name": "to", "type": "address"},
        {"name": "value", "type": "uint256"},
        {"name": "validAfter", "type": "uint256"},
        {"name": "validBefore", "type": "uint256"},
        {"name": "nonce", "type": "bytes32"},
    ],
}

# Default HTTP timeout in seconds
DEFAULT_TIMEOUT = 30


class Claw402:
    """Typed client for claw402.ai — pay-per-call data APIs via x402.

    All API calls cost micro-amounts of USDC on Base mainnet (Coinbase L2).
    No API key, no account, no subscription needed — just a wallet with USDC.

    Usage::

        from claw402 import Claw402

        client = Claw402(private_key="0xYourPrivateKey")

        # Crypto market data (CoinAnk)
        data = client.coinank.fund.realtime(product_type="SWAP")
        signals = client.nofxos.netflow.top_ranking(limit=20)

        # US stocks (Alpha Vantage)
        quote = client.alphavantage.stocks_us.quote(symbol="AAPL")
        daily = client.alphavantage.stocks_us.daily(symbol="TSLA", outputsize="compact")

        # A-share stocks (Tushare)
        cn = client.tushare.stocks_cn.daily(ts_code="000001.SZ", trade_date="20240101")

        # Forex & metals (Twelve Data)
        fx = client.twelvedata.price.price(symbol="EUR/USD")
        gold = client.twelvedata.metals.price(symbol="XAU/USD")

        # AI models (OpenAI)
        resp = client.openai.chat.chat({"model": "gpt-4o", "messages": [...]})

        # AI models (Anthropic)
        resp = client.anthropic.messages.messages({"model": "claude-3-5-sonnet-20241022", ...})

        # Polygon.io tick data
        snap = client.polygon.snapshots.ticker(stocksTicker="AAPL")

        # Alpaca market data
        bars = client.alpaca.bars.bars(symbols="AAPL,TSLA", timeframe="1Day")

    Context manager (auto-closes session)::

        with Claw402(private_key="0x...") as client:
            data = client.coinank.indicator.fear_greed()
    """

    def __init__(self, private_key: str, base_url: str = "https://claw402.ai"):
        if not private_key.startswith("0x"):
            raise ValueError("private_key must be a hex string starting with 0x")
        self._account = Account.from_key(private_key)
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        # Crypto data providers
        self.coinank = CoinankResource(self)
        self.nofxos = NofxosResource(self)
        # US stock market data
        self.alphavantage = AlphavantageResource(self)
        self.polygon = PolygonResource(self)
        self.alpaca = AlpacaResource(self)
        # Chinese A-share market
        self.tushare = TushareResource(self)
        # Forex, metals, indices
        self.twelvedata = TwelvedataResource(self)
        # AI model providers
        self.openai = OpenaiResource(self)
        self.anthropic = AnthropicResource(self)
        self.deepseek = DeepseekResource(self)
        self.qwen = QwenResource(self)
        self.gemini = GeminiResource(self)
        self.grok = GrokResource(self)
        self.kimi = KimiResource(self)
        # Web3 intelligence
        self.rootdata = RootdataResource(self)

    def close(self):
        """Close the underlying HTTP session."""
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _post(self, path: str, body: dict) -> dict:
        """Send a POST request with JSON body, handling x402 payment if required."""
        url = f"{self._base_url}{path}"

        # Step 1: initial request — expect 402
        resp = self._session.post(url, json=body, timeout=DEFAULT_TIMEOUT)

        if resp.ok:
            return resp.json()

        if resp.status_code != 402:
            raise Claw402Error(resp.status_code, resp.text)

        # Step 2: decode Payment-Required header
        header_b64 = resp.headers.get("Payment-Required") or resp.headers.get("PAYMENT-REQUIRED")
        if not header_b64:
            raise Claw402Error(402, "No Payment-Required header in 402 response")

        payment_required = json.loads(base64.b64decode(header_b64))
        req = None
        for accept in payment_required.get("accepts", []):
            if accept.get("scheme") == "exact" and accept.get("network") == f"eip155:{BASE_CHAIN_ID}":
                req = accept
                break

        if req is None:
            networks = [f"{a.get('scheme')}@{a.get('network')}" for a in payment_required.get("accepts", [])]
            raise Claw402Error(402, f"No compatible payment method. Available: {', '.join(networks)}")

        # Step 3: sign EIP-3009 TransferWithAuthorization
        valid_before = int(time.time()) + req["maxTimeoutSeconds"]
        nonce = "0x" + secrets.token_hex(32)

        domain = {
            "name": req["extra"]["name"],
            "version": req["extra"]["version"],
            "chainId": BASE_CHAIN_ID,
            "verifyingContract": req["asset"],
        }

        message = {
            "from": self._account.address,
            "to": req["payTo"],
            "value": int(req["amount"]),
            "validAfter": 0,
            "validBefore": valid_before,
            "nonce": bytes.fromhex(nonce[2:]),
        }

        signed = self._account.sign_typed_data(
            domain_data=domain,
            message_types=TRANSFER_WITH_AUTHORIZATION_TYPES,
            message_data=message,
        )

        sig_hex = signed.signature.hex() if isinstance(signed.signature, bytes) else str(signed.signature)
        if not sig_hex.startswith("0x"):
            sig_hex = "0x" + sig_hex

        # Step 4: build x402 v2 payment payload
        payload = {
            "x402Version": 2,
            "payload": {
                "signature": sig_hex,
                "authorization": {
                    "from": self._account.address,
                    "to": req["payTo"],
                    "value": req["amount"],
                    "validAfter": "0",
                    "validBefore": str(valid_before),
                    "nonce": nonce,
                },
            },
            "accepted": {
                "scheme": "exact",
                "network": req["network"],
                "asset": req["asset"],
                "amount": req["amount"],
                "payTo": req["payTo"],
                "maxTimeoutSeconds": req["maxTimeoutSeconds"],
                "extra": req["extra"],
            },
        }
        payload_b64 = base64.b64encode(json.dumps(payload).encode()).decode()

        # Step 5: retry POST with payment signature
        paid_resp = self._session.post(
            url,
            json=body,
            headers={"PAYMENT-SIGNATURE": payload_b64},
            timeout=DEFAULT_TIMEOUT,
        )

        if not paid_resp.ok:
            err_msg = ""
            err_header = paid_resp.headers.get("Payment-Required") or paid_resp.headers.get("PAYMENT-REQUIRED")
            if err_header:
                try:
                    decoded = json.loads(base64.b64decode(err_header))
                    err_msg = decoded.get("error", "")
                except Exception:
                    pass
            if not err_msg:
                err_msg = paid_resp.text
            raise Claw402Error(paid_resp.status_code, err_msg)

        return paid_resp.json()

    def _get(self, path: str, params: dict = None) -> dict:
        if params is not None:
            params = {k: v for k, v in params.items() if v is not None}
            if not params:
                params = None

        url = f"{self._base_url}{path}"

        # Step 1: initial request — expect 402
        resp = self._session.get(url, params=params, timeout=DEFAULT_TIMEOUT)

        if resp.ok:
            return resp.json()

        if resp.status_code != 402:
            raise Claw402Error(resp.status_code, resp.text)

        # Step 2: decode Payment-Required header
        header_b64 = resp.headers.get("Payment-Required") or resp.headers.get("PAYMENT-REQUIRED")
        if not header_b64:
            raise Claw402Error(402, "No Payment-Required header in 402 response")

        payment_required = json.loads(base64.b64decode(header_b64))
        req = None
        for accept in payment_required.get("accepts", []):
            if accept.get("scheme") == "exact" and accept.get("network") == f"eip155:{BASE_CHAIN_ID}":
                req = accept
                break

        if req is None:
            networks = [f"{a.get('scheme')}@{a.get('network')}" for a in payment_required.get("accepts", [])]
            raise Claw402Error(402, f"No compatible payment method. Available: {', '.join(networks)}")

        # Step 3: sign EIP-3009 TransferWithAuthorization
        valid_before = int(time.time()) + req["maxTimeoutSeconds"]
        nonce = "0x" + secrets.token_hex(32)

        domain = {
            "name": req["extra"]["name"],
            "version": req["extra"]["version"],
            "chainId": BASE_CHAIN_ID,
            "verifyingContract": req["asset"],
        }

        message = {
            "from": self._account.address,
            "to": req["payTo"],
            "value": int(req["amount"]),
            "validAfter": 0,
            "validBefore": valid_before,
            "nonce": bytes.fromhex(nonce[2:]),
        }

        signed = self._account.sign_typed_data(
            domain_data=domain,
            message_types=TRANSFER_WITH_AUTHORIZATION_TYPES,
            message_data=message,
        )

        # Ensure signature has 0x prefix (eth-account may return bytes or hex string)
        sig_hex = signed.signature.hex() if isinstance(signed.signature, bytes) else str(signed.signature)
        if not sig_hex.startswith("0x"):
            sig_hex = "0x" + sig_hex

        # Step 4: build x402 v2 payment payload
        payload = {
            "x402Version": 2,
            "payload": {
                "signature": sig_hex,
                "authorization": {
                    "from": self._account.address,
                    "to": req["payTo"],
                    "value": req["amount"],
                    "validAfter": "0",
                    "validBefore": str(valid_before),
                    "nonce": nonce,
                },
            },
            "accepted": {
                "scheme": "exact",
                "network": req["network"],
                "asset": req["asset"],
                "amount": req["amount"],
                "payTo": req["payTo"],
                "maxTimeoutSeconds": req["maxTimeoutSeconds"],
                "extra": req["extra"],
            },
        }
        payload_b64 = base64.b64encode(json.dumps(payload).encode()).decode()

        # Step 5: retry request with payment signature
        paid_resp = self._session.get(
            url,
            params=params,
            headers={"PAYMENT-SIGNATURE": payload_b64},
            timeout=DEFAULT_TIMEOUT,
        )

        if not paid_resp.ok:
            err_msg = ""
            err_header = paid_resp.headers.get("Payment-Required") or paid_resp.headers.get("PAYMENT-REQUIRED")
            if err_header:
                try:
                    decoded = json.loads(base64.b64decode(err_header))
                    err_msg = decoded.get("error", "")
                except Exception:
                    pass
            if not err_msg:
                err_msg = paid_resp.text
            raise Claw402Error(paid_resp.status_code, err_msg)

        return paid_resp.json()
