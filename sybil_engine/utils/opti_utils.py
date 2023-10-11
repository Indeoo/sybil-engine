import time


def wait_for_optimism(chain_instance):
    if chain_instance['chain'] == 'OPTIMISM':
        time.sleep(120)