import json
import unittest
from copy import deepcopy
from pathlib import Path
from src.validator import validate_po

ROOT=Path(__file__).resolve().parents[1]
POLICY=json.loads((ROOT/'config/policy.json').read_text())
POS=json.loads((ROOT/'data/sample_pos.json').read_text())

class TestValidator(unittest.TestCase):
    def test_six_scenarios(self):
        expected=['PASS','FAIL','FAIL','FAIL','REVIEW','ERROR']
        self.assertEqual([validate_po(p,POLICY)['status'] for p in POS],expected)
    def test_specific_violations(self):
        codes=[{f['code'] for f in validate_po(p,POLICY)['findings']} for p in POS]
        for i, code in [(1,'ITEM_MOQ'),(2,'PACK_MULTIPLE'),(3,'SUPPLIER_MIN_VALUE'),(4,'PRICE_INCREASE'),(4,'SPEND_INCREASE'),(5,'INVALID_INPUT')]:
            self.assertIn(code,codes[i])
    def test_zero_quantity_does_not_trigger_item_moq(self):
        p=deepcopy(POS[0]);p['lines'][0]['quantity']=0;p['supplier_min_order_value']=0;p['baseline_order_value']=0
        codes={f['code'] for f in validate_po(p,POLICY)['findings']}
        self.assertNotIn('ITEM_MOQ',codes)
    def test_missing_data_is_error(self):
        p=deepcopy(POS[0]);del p['lines'][0]['pack_multiple']
        self.assertEqual(validate_po(p,POLICY)['status'],'ERROR')
    def test_negative_quantity_is_error(self):
        p=deepcopy(POS[0]);p['lines'][0]['quantity']=-25
        self.assertEqual(validate_po(p,POLICY)['status'],'ERROR')
    def test_duplicate_item_is_error(self):
        p=deepcopy(POS[0]);p['lines'].append(deepcopy(p['lines'][0]))
        self.assertEqual(validate_po(p,POLICY)['status'],'ERROR')
    def test_price_threshold_boundary(self):
        p=deepcopy(POS[0]);p['lines'][0]['unit_price']='4.4';p['lines'][0]['previous_unit_price']='4';p['baseline_order_value']='440'
        self.assertNotIn('PRICE_INCREASE',{f['code'] for f in validate_po(p,POLICY)['findings']})
    def test_spend_threshold_boundary(self):
        p=deepcopy(POS[0]);p['baseline_order_value']=str(Decimal('400')/Decimal('1.15'))
        self.assertNotIn('SPEND_INCREASE',{f['code'] for f in validate_po(p,POLICY)['findings']})
    def test_invalid_decimal_nan(self):
        p=deepcopy(POS[0]);p['lines'][0]['quantity']='NaN'
        self.assertEqual(validate_po(p,POLICY)['status'],'ERROR')
    def test_read_only(self):
        p=deepcopy(POS[0]);before=deepcopy(p)
        self.assertTrue(validate_po(p,POLICY)['read_only'])
        self.assertEqual(p,before)

from decimal import Decimal
if __name__=='__main__':unittest.main()
