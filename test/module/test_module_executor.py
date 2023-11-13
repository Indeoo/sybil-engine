import unittest

from sybil_engine.module.module_executor import ModuleExecutor
from sybil_engine.utils.accumulator import get_value
from sybil_engine.utils.utils import AccountException
from test import zksync_test_account
from test.module.mock_fail_module import MockFailModule
from test.module.mock_module import MockModule
from test.module.mock_not_enoguth_native_module import MockNotEnoughNativeModule
from test.module.repeatable_mock_module import RepeatableMockModule


class TestModuleExecutor(unittest.TestCase):

    def test_execute_module(self):
        sleep_interval = {'from': 0, 'to': 0}
        account = zksync_test_account
        min_native_balance = {'from': 0.001, 'to': 0.001}
        modules = [
            (MockModule(min_native_balance, None, False), {}),
            (MockModule(min_native_balance, None, False), {}),
            (MockModule(min_native_balance, None, False), {})
        ]

        ModuleExecutor(sleep_interval).execute_modules(modules, account)

        self.assertEqual(get_value("Failed accounts: "), None)

    def test_shouldThrowNotEnoughNativeBalance(self):
        sleep_interval = {'from': 0, 'to': 0}
        account = zksync_test_account
        min_native_balance = {'from': 0.001, 'to': 0.001}
        modules = [
            (MockModule(min_native_balance, None, False), {}),
            (MockModule(min_native_balance, None, False), {}),
            (MockNotEnoughNativeModule(min_native_balance, None, False), {})
        ]

        ModuleExecutor(sleep_interval).execute_modules(modules, account)

        self.assertEqual(len(get_value("Failed accounts: ")), 1)

    def test_should_throwAccountExceptionOnModuleException(self):
        sleep_interval = {'from': 0, 'to': 0}
        account = zksync_test_account
        min_native_balance = {'from': 0.001, 'to': 0.001}

        module = MockFailModule(min_native_balance, None, False)

        with self.assertRaises(AccountException):
            ModuleExecutor(sleep_interval).execute_module([], account, module)

    def test_should_throwHandleExceptionOnRepeatableModuleException(self):
        sleep_interval = {'from': 0, 'to': 0}
        account = zksync_test_account
        min_native_balance = {'from': 0.001, 'to': 0.001}

        module = RepeatableMockModule(min_native_balance, None, False, 1)

        ModuleExecutor(sleep_interval).execute_module([], account, module)
