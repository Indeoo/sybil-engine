from sybil_engine.utils.utils import AccountException
from _decimal import Decimal, ROUND_DOWN


class Balance:
    max_number = 1000000000000000000000

    def __init__(self, wei_balance, chain, token):
        self.wei = wei_balance
        self.chain = chain
        self.token = token

    def readable(self):
        raise Exception("not supported")

    def log_line(self):
        if self.readable() < Balance.max_number:
            factor = Decimal('1e{}'.format(-6))
            return str(self.readable().quantize(factor, rounding=ROUND_DOWN)) + ' ' + self.token
        else:
            return self.readable()

    def wei_compare(self):
        pass

    def minus(self, balance):
        if self.chain != balance.chain and balance.chain is not None:
            raise BalanceException(f'Trying to minus wrong chain {self.chain} - {balance.chain}')

        if self.token != balance.token and self.token is not None:
            raise BalanceException(f'Trying to minus wrong token {self.token} - {balance.token}')

        if self.wei <= balance.wei:
            raise BalanceException(f'Result of minus cant be less than 0 {self.wei} - {balance.wei}')

        return self.__class__(
            self.wei - balance.wei,
            self.chain,
            self.token
        )


class NativeBalance(Balance):
    def __init__(self, wei_balance, chain, token):
        super().__init__(wei_balance, chain, token)

    def wei_compare(self):
        return self.wei

    def readable(self):
        from sybil_engine.domain.balance.balance_utils import from_wei_to_eth

        return Decimal(from_wei_to_eth(self.wei))


class Erc20Balance(Balance):
    def __init__(self, wei_balance, chain, token):
        super().__init__(wei_balance, chain, token)

    def wei_compare(self):
        if self.chain == 'BSC':
            return self.wei / 10 ** 12
        else:
            return self.wei

    def readable(self):
        if self.chain == 'BSC':
            return Decimal(self.wei / 10 ** 18)
        else:
            return Decimal(self.wei / 10 ** 6)


class WETHBalance(Balance):
    def __init__(self, wei_balance, chain):
        super().__init__(wei_balance, chain, 'WETH')

    def wei_compare(self):
        return self.wei

    def readable(self):
        return Decimal(self.wei / 10 ** 18)


class BalanceException(AccountException):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class NotEnoughERC20Balance(AccountException):
    def __init__(self, message, chain=None):
        self.message = message
        self.chain = chain
        super().__init__(self.message)


class NotEnoughNativeBalance(AccountException):
    def __init__(self, message, chain=None):
        self.message = message
        self.chain = chain
        super().__init__(self.message)
