from sybil_engine.domain.generic_swap_facade import GenericSwapFacade
from test.module.swap.mock_dex import MockFailDex


class MockTestSwapFacade(GenericSwapFacade):

    def get_dex_classes(self, pair):
        return {
            MockFailDex.dex_name: (MockFailDex, {})
        }

    def get_all_swap_apps(self):
        return {
            MockFailDex: ['ZKSYNC', 'LINEA']
        }


swap_facade = MockTestSwapFacade()
