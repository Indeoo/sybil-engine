import unittest

from sybil_engine.domain.balance.balance_utils import interval_to_eth_balance
from sybil_engine.utils.app_account_utils import create_app_account_with_proxies


class TestCreateAppAccounts(unittest.TestCase):

    def test_create_zksync(self):
        zksync_test_account = create_app_account_with_proxies(
            ['0xb98308D11E2B578858Fbe65b793e71C7a0CAa43e'],
            False,
            'password',
            ['0x7726827caac94a7f9e1b160f7ea819f172f7b6f9d2a97f992c38edeab82d4110'],
            [],
            'RANDOM',
            ['0x6317842385f344acf68561f4e65f0f39e4fb4f1ad104b92bd007361aed39d8'],
        )[0]

        zksync_min_native_balance = interval_to_eth_balance({'from': 1, 'to': 1}, zksync_test_account, None, None)

    def test_create_base_account(self):
        base_test_account = create_app_account_with_proxies(
            ['0xb98308D11E2B578858Fbe65b793e71C7a0CAa43e'],
            False,
            'password',
            ['0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'],
            [],
            'RANDOM',
            ['0x6317842385f344acf68561f4e65f0f39e4fb4f1ad104b92bd007361aed39d8'],
        )[0]

        base_min_native_balance = interval_to_eth_balance({'from': 1, 'to': 1}, base_test_account, None, None)

