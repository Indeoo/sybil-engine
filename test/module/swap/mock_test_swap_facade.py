from sybil_engine.domain.generic_swap_facade import GenericSwapFacade
from test.module.swap.mock_dex import MockFailDex


class MockTestSwapFacade(GenericSwapFacade):
    def __init__(self, dex_classes, swap_apps):
        super().__init__(dex_classes, swap_apps)

    def get_dex_classes(self, pair):
        return {
            MockFailDex.dex_name: (MockFailDex, {})
        }


swap_facade = MockTestSwapFacade(
    {
        MockFailDex.dex_name: (MockFailDex, {})
    },
    {
        MockFailDex: ['ZKSYNC', 'LINEA']
    }
)
