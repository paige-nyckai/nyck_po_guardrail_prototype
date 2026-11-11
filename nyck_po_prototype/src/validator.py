"""Deterministic, read-only purchasing guardrail validator. Standard library only."""
from decimal import Decimal, InvalidOperation


def dec(value, name):
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{name} must be a number")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{name} must be a number") from None
    if not result.is_finite():
        raise ValueError(f"{name} must be finite")
    return result


def validate_po(po, policy):
    """Return structured findings. FAIL=hard violation, REVIEW=warning, PASS=clean."""
    po_id = str(po.get("po_id", "UNKNOWN"))
    findings = []
    def finding(severity, code, message, item_id=None):
        entry = {"severity": severity, "code": code, "message": message}
        if item_id is not None:
            entry["item_id"] = item_id
        findings.append(entry)

    try:
        if not isinstance(po.get("lines"), list) or not po["lines"]:
            raise ValueError("lines must be a nonempty list")
        if not po.get("supplier_id"):
            raise ValueError("supplier_id is required")
        if po.get("currency") != policy.get("currency"):
            raise ValueError("currency does not match policy")
        minimum = dec(po["supplier_min_order_value"], "supplier_min_order_value")
        baseline = dec(po["baseline_order_value"], "baseline_order_value")
        spend_limit = dec(policy["max_spend_increase_pct"], "max_spend_increase_pct")
        price_limit = dec(policy["max_price_increase_pct"], "max_price_increase_pct")
        if min(minimum, baseline, spend_limit, price_limit) < 0:
            raise ValueError("minimums, baseline and thresholds cannot be negative")
        total = Decimal(0)
        seen = set()
        for line in po["lines"]:
            item = str(line["item_id"])
            if item in seen:
                raise ValueError(f"duplicate item_id {item}")
            seen.add(item)
            if line.get("uom") != "ea":
                raise ValueError(f"{item}: demo supports only ea units")
            qty = dec(line["quantity"], f"{item}.quantity")
            moq = dec(line["item_moq"], f"{item}.item_moq")
            pack = dec(line["pack_multiple"], f"{item}.pack_multiple")
            price = dec(line["unit_price"], f"{item}.unit_price")
            old_price = dec(line["previous_unit_price"], f"{item}.previous_unit_price")
            if min(qty, moq, price, old_price) < 0 or pack <= 0:
                raise ValueError(f"{item}: invalid negative value or nonpositive pack")
            if qty != qty.to_integral_value() or pack != pack.to_integral_value():
                raise ValueError(f"{item}: quantities and pack multiples must be whole units")
            total += qty * price
            if qty > 0 and qty < moq:
                finding("FAIL", "ITEM_MOQ", f"{item}: ordered {qty}, minimum {moq}", item)
            if qty > 0 and qty % pack != 0:
                finding("FAIL", "PACK_MULTIPLE", f"{item}: ordered {qty}, must be multiple of {pack}", item)
            if qty > 0 and old_price > 0:
                change = (price / old_price - 1) * 100
                if change > price_limit:
                    finding("REVIEW", "PRICE_INCREASE", f"{item}: price increase {change:.2f}% exceeds {price_limit}%", item)
            elif qty > 0 and old_price == 0:
                finding("REVIEW", "NO_PRICE_BASELINE", f"{item}: previous price is zero; change cannot be calculated", item)
        if total < minimum:
            finding("FAIL", "SUPPLIER_MIN_VALUE", f"Order ${total:.2f} is below supplier minimum ${minimum:.2f}")
        if baseline > 0:
            change = (total / baseline - 1) * 100
            if change > spend_limit:
                finding("REVIEW", "SPEND_INCREASE", f"Spend increase {change:.2f}% exceeds {spend_limit}%")
        else:
            finding("REVIEW", "NO_SPEND_BASELINE", "Baseline order value is zero; spend change cannot be calculated")
        status = "FAIL" if any(f["severity"] == "FAIL" for f in findings) else ("REVIEW" if findings else "PASS")
        return {"po_id": po_id, "status": status, "order_value": str(total.quantize(Decimal('0.01'))), "currency": po["currency"], "findings": findings, "policy_id": policy["policy_id"], "read_only": True}
    except (ValueError, KeyError, TypeError, ArithmeticError) as exc:
        return {"po_id": po_id, "status": "ERROR", "order_value": None, "currency": po.get("currency"), "findings": [{"severity":"FAIL", "code":"INVALID_INPUT", "message":str(exc)}], "policy_id": policy.get("policy_id"), "read_only": True}
