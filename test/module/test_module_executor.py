import unittest

from sybil_engine.module.module_executor import execute_modules
from sybil_engine.utils.utils import AccountException
from test import zksync_test_account
from test.module.mock_module import MockModule
from test.module.mock_not_enoguth_native_module import MockNotEnoughNativeModule


class TestModuleExecutor(unittest.TestCase):

    def test_execute_module(self):
        okx_secret = None
        sleep_interval = {'from': 0, 'to': 0}
        account = zksync_test_account
        modules = [(MockModule, {}), (MockModule, {}), (MockModule, {})]
        okx_config = None
        min_native_balance = {'from': 0.001, 'to': 0.001}
        execute_modules(okx_secret, sleep_interval, modules, account, okx_config, min_native_balance)

    def test_shouldThrowNotEnoughNativeBalance(self):
        okx_secret = None
        sleep_interval = {'from': 0, 'to': 0}
        account = zksync_test_account
        modules = [(MockModule, {}), (MockModule, {}), (MockNotEnoughNativeModule, {})]
        okx_config = None, False, None
        min_native_balance = {'from': 0.001, 'to': 0.001}

        with self.assertRaises(AccountException):
            execute_modules(okx_secret, sleep_interval, modules, account, okx_config, min_native_balance)
