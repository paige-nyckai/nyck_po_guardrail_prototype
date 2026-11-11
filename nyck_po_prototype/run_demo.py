"""Run sample PO validation and write a JSON and Markdown mentor report."""
import json
from pathlib import Path
from src.validator import validate_po

ROOT = Path(__file__).resolve().parent
policy = json.loads((ROOT/'config/policy.json').read_text())
pos = json.loads((ROOT/'data/sample_pos.json').read_text())
results = [validate_po(po, policy) for po in pos]
out = ROOT/'outputs'
out.mkdir(exist_ok=True)
(out/'results.json').write_text(json.dumps(results, indent=2)+'\n')
lines = ['# Nyck PO Guardrail Validator — Demo Results', '', 'Synthetic data; not connected to Nyck. Read-only validation.', '', '| PO | Status | Order value | Findings |', '|---|---|---:|---|']
for r in results:
    notes = '; '.join(f['code'] for f in r['findings']) or 'None'
    amount = '$'+r['order_value'] if r['order_value'] is not None else 'N/A'
    lines.append(f"| {r['po_id']} | {r['status']} | {amount} | {notes} |")
lines += ['', '## Finding details', '']
for r in results:
    lines.append(f"### {r['po_id']} — {r['status']}")
    lines.extend(f"- **{f['code']}**: {f['message']}" for f in r['findings'])
    if not r['findings']: lines.append('- No findings')
    lines.append('')
lines += ['## Limitations', '- Demo supplier minimum is an order value in USD, not a pack-count MOQ.', '- Supports only whole units (`ea`), one currency, and read-only checks.', '- The 15% spend and 10% price thresholds are illustrative, not Nyck policy.', '- No forecasts, inventory optimization, Claude API, NeMo, or ERP integration.', '']
(out/'mentor_demo_report.md').write_text('\n'.join(lines))
for r in results:
    print(f"{r['po_id']:<27} {r['status']:<7} ${str(r['order_value'] or 'N/A'):<9} {', '.join(f['code'] for f in r['findings']) or 'OK'}")
print('\nReports saved to outputs/')
