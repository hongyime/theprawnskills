"""Validate a synthetic wire contract; run with Python from any working directory."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator
from provider import order_wire

SCHEMA = json.loads(Path(__file__).with_name('order.schema.json').read_text(encoding='utf-8'))
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA)


class ContractTests(unittest.TestCase):
    def test_real_serialization_preserves_consumer_fields_and_large_id(self):
        body = json.loads(order_wire())
        VALIDATOR.validate(body)
        self.assertEqual(body['data']['id'], '9007199254740993')
        self.assertEqual(body['data']['label'], 'Sample order')
        self.assertIsNone(body['data']['assignedTo'])

    def test_documented_error_has_its_own_shape(self):
        body = json.loads(order_wire(False))
        VALIDATOR.validate(body)
        self.assertEqual(body['status'], 404)
        self.assertEqual(body['error']['code'], 'NOT_FOUND')

    def test_wrong_type_renamed_required_field_and_wrong_nullability_fail(self):
        original = json.loads(order_wire())
        for value in [9007199254740993, 9007199254740992.0, None]:
            changed = deepcopy(original)
            changed['data']['id'] = value
            self.assertFalse(VALIDATOR.is_valid(changed))
        renamed = deepcopy(original)
        renamed['data']['title'] = renamed['data'].pop('label')
        self.assertFalse(VALIDATOR.is_valid(renamed))
        omitted = deepcopy(original)
        del omitted['data']['assignedTo']
        self.assertFalse(VALIDATOR.is_valid(omitted))
        wrong = deepcopy(original)
        wrong['data']['assignedTo'] = 12
        self.assertFalse(VALIDATOR.is_valid(wrong))

    def test_compatible_addition_is_accepted_by_this_tolerant_consumer(self):
        changed = json.loads(order_wire())
        changed['data']['optionalNote'] = 'New provider field'
        VALIDATOR.validate(changed)
        self.assertEqual(changed['data']['label'], 'Sample order')

    def test_undocumented_error_shape_fails(self):
        self.assertFalse(VALIDATOR.is_valid({'status': 404, 'data': None}))
        self.assertFalse(VALIDATOR.is_valid({'status': 404, 'error': 'missing'}))
        self.assertFalse(VALIDATOR.is_valid({'status': 200, 'data': []}))


if __name__ == '__main__':
    unittest.main(verbosity=2)
