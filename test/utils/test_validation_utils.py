import unittest

from sybil_engine.config.app_config import set_module_data
from sybil_engine.utils.validation_utils import validate_chain, ValidationException
from test.module.test_modules import TestModules


class TestValidation(unittest.TestCase):

    def test_shouldValidateValidChain(self):
        set_module_data(TestModules())

        try:
            validate_chain('ZKSYNC')
            validate_chain('OPTIMISM')
        except Exception as e:
            self.fail(e)

    def test_shouldFailInInvalidChain(self):
        set_module_data(TestModules())

        with self.assertRaises(Exception):
            ValidationException('INVALID_CHAIN')
