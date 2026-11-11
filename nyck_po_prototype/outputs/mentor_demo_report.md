# Nyck PO Guardrail Validator — Demo Results

Synthetic data; not connected to Nyck. Read-only validation.

| PO | Status | Order value | Findings |
|---|---|---:|---|
| PO-001-PASS | PASS | $400.00 | None |
| PO-002-ITEM-MOQ | FAIL | $120.00 | ITEM_MOQ |
| PO-003-PACK | FAIL | $240.00 | PACK_MULTIPLE |
| PO-004-SUPPLIER-MIN | FAIL | $480.00 | SUPPLIER_MIN_VALUE |
| PO-005-REVIEW | REVIEW | $300.00 | PRICE_INCREASE; SPEND_INCREASE |
| PO-006-INVALID-UNIT | ERROR | N/A | INVALID_INPUT |

## Finding details

### PO-001-PASS — PASS
- No findings

### PO-002-ITEM-MOQ — FAIL
- **ITEM_MOQ**: B: ordered 20, minimum 50

### PO-003-PACK — FAIL
- **PACK_MULTIPLE**: C: ordered 60, must be multiple of 25

### PO-004-SUPPLIER-MIN — FAIL
- **SUPPLIER_MIN_VALUE**: Order $480.00 is below supplier minimum $500.00

### PO-005-REVIEW — REVIEW
- **PRICE_INCREASE**: F: price increase 20.00% exceeds 10%
- **SPEND_INCREASE**: Spend increase 50.00% exceeds 15%

### PO-006-INVALID-UNIT — ERROR
- **INVALID_INPUT**: G: demo supports only ea units

## Limitations
- Demo supplier minimum is an order value in USD, not a pack-count MOQ.
- Supports only whole units (`ea`), one currency, and read-only checks.
- The 15% spend and 10% price thresholds are illustrative, not Nyck policy.
- No forecasts, inventory optimization, Claude API, NeMo, or ERP integration.
