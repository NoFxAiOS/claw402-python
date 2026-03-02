# Architecture

## Overview

```
claw402 (pip)
├── claw402/
│   ├── __init__.py        ← Package entry + re-exports
│   ├── client.py          ← Core client: x402 V2 payment flow
│   ├── errors.py          ← Error types
│   └── generated/         ← Auto-generated from providers/*.yaml
│       ├── coinank.py     ← 78 endpoints: market data, ETF, liquidations, etc.
│       └── nofxos.py      ← 18 endpoints: AI signals, rankings, Upbit
└── examples/
    └── basic.py           ← Usage example
```

## Payment Flow (x402 V2)

```
Client                          claw402.ai                    Base L2
  │                                │                            │
  │─── GET /api/v1/... ──────────▶│                            │
  │◀── 402 + Payment-Required ────│                            │
  │                                │                            │
  │  [sign EIP-3009 locally]       │                            │
  │                                │                            │
  │─── GET + PAYMENT-SIGNATURE ──▶│                            │
  │                                │── verify + settle ────────▶│
  │                                │◀── tx confirmed ──────────│
  │◀── 200 + data ────────────────│                            │
```

## Code Generation

The `generated/` directory is produced by `sdks/codegen/` which reads
`providers/*.yaml` (the same YAML files that configure the Go gateway)
and emits typed SDK methods for TypeScript, Python, and Go.

Each YAML route becomes a typed method:

```yaml
# providers/coinank.yaml
- gateway_path: /api/v1/coinank/fund/realtime
  category: Fund
  allowed_params: [sortBy, productType, page, size]
```

Becomes:

```python
# generated/coinank.py
def realtime(self, sort_by=None, product_type=None, page=None, size=None):
    return self._client._get('/api/v1/coinank/fund/realtime', params={
        'sortBy': sort_by, 'productType': product_type, ...
    })
```
