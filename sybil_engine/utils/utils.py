import time

from tqdm import tqdm
import random


def int_to_decimal(qty, decimal):
    return int(qty * int("".join(["1"] + ["0"] * decimal)))


def randomized_sleeping(sleep_interval):
    x = random.randint(sleep_interval['from'], sleep_interval['to'])

    if x == 0:
        return

    for i in tqdm(range(x), desc='sleep ', bar_format='{desc}: {n_fmt}/{total_fmt}'):
        time.sleep(1)


def interval_to_int(interval):
    return int(random.randint(interval['from'], interval['to']))


def interval_to_round(interval):
    return round(random.uniform(interval['from'], interval['to']), 6)


class AccountException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


# class TransactionExecutionException(AccountException):
#     def __init__(self, message):
#         self.message = message
#         super().__init__(self.message)


class ConfigurationException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ModuleException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class SwapException(AccountException):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
