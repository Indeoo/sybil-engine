import unittest

from sybil_engine.config.app_config import set_okx_config
from sybil_engine.module.module_executor import execute_modules
from sybil_engine.utils.utils import AccountException
from test import zksync_test_account
from test.module.mock_module import MockModule
from test.module.mock_not_enoguth_native_module import MockNotEnoughNativeModule


class TestModuleExecutor(unittest.TestCase):

    def test_execute_module(self):
        sleep_interval = {'from': 0, 'to': 0}
        account = zksync_test_account
        modules = [(MockModule, {}), (MockModule, {}), (MockModule, {})]
        min_native_balance = {'from': 0.001, 'to': 0.001}
        execute_modules(sleep_interval, modules, account, min_native_balance)

    def test_shouldThrowNotEnoughNativeBalance(self):
        sleep_interval = {'from': 0, 'to': 0}
        account = zksync_test_account
        modules = [(MockModule, {}), (MockModule, {}), (MockNotEnoughNativeModule, {})]
        min_native_balance = {'from': 0.001, 'to': 0.001}

        with self.assertRaises(AccountException):
            execute_modules(sleep_interval, modules, account, min_native_balance)
