from sybil_engine.utils.app_account_utils import create_app_account_with_proxies

zksync_test_account = create_app_account_with_proxies(
    ['0xb98308D11E2B578858Fbe65b793e71C7a0CAa43e'],
    False,
    'password',
    ['0x7726827caac94a7f9e1b160f7ea819f172f7b6f9d2a97f992c38edeab82d4110'],
    [],
    'RANDOM'
)[0]