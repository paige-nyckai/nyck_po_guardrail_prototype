# Nyck PO Guardrail Validator — Prototype 1

A **working read-only** proof of concept for item MOQ, supplier minimum order value, pack multiple, and price/spend review thresholds. Uses **synthetic** POs. **Not connected to Nyck, Claude, or NeMo.** Standard Python library only.

## Run in VS Code / terminal

Requires Python 3.9+.

```bash
cd nyck_po_prototype
python run_demo.py
python -m unittest discover -s tests -v
```

Results appear in `outputs/results.json` and `outputs/mentor_demo_report.md`.

## Files
- `src/validator.py`: deterministic rules and fail-closed input validation
- `config/policy.json`: demo thresholds (15% spend increase, 10% price increase)
- `data/sample_pos.json`: six synthetic test orders
- `tests/test_validator.py`: regression tests
- `run_demo.py`: report generation
- `outputs/`: generated results

## Rules
- `PASS`: no findings.
- `REVIEW`: nonblocking warning(s), no hard violations.
- `FAIL`: at least one hard MOQ or pack violation.
- `ERROR`: invalid/missing data; no valid calculation.

The supplier-level minimum in this demo is **minimum order value in USD**, not minimum packs. No optimization is performed; this is a validator, not an optimizer. Real Nyck rules must be confirmed before integration. No purchasing actions are available.

## Demonstration steps
1. Run `python run_demo.py` and show the six PO outcomes.
2. Open `outputs/mentor_demo_report.md` to discuss findings.
3. Change a quantity in `data/sample_pos.json`, rerun, and show how the result changes.
4. Run automated tests.
5. Explain future integration: Claude -> read-only PO retrieval -> deterministic validator -> structured result -> Claude explanation; approval required for future write tools.

## Limitations / next iteration
- Validate the actual Nyck supplier MOQ type (packs, order value, weight, etc.).
- Add pack-level pricing and cross-UOM conversion with explicit conversion factors.
- Add inventory, lead time, forecast inputs and forecast freshness rules.
- Add multi-line optimization and a separate independent verification step.
- Add policy ownership/versioning, access controls, and audit logs.
- Connect to Claude/NeMo only after deterministic tests pass.
