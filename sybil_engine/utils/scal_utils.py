import requests
from web3 import Web3


def find_interacted_contracts(wallet_address, api_url, api_key):
    api_url = f"{api_url}/api?module=account&action=txlist&address={wallet_address}&startblock=0&endblock=latest&sort=asc&apikey={api_key}"

    response = requests.get(api_url)
    data = response.json()

    contracts = set()  # Use a set to avoid duplicates

    if data['status'] == '1' and data['message'] == 'OK':
        for tx in data['result']:
            if tx['to']:  # Assuming non-empty 'to' indicates potential contract interaction
                contracts.add(Web3.to_checksum_address(tx['to']))

    return contracts


def get_wallet_transactions(wallet_address, rpc_url, max_transactions=20):
    headers = {'Content-Type': 'application/json'}
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_blockNumber",
        "params": [],
        "id": 1,
    }

    # Fetch the latest block number
    response = requests.post(rpc_url, json=payload, headers=headers)
    latest_block = int(response.json()['result'], 16)

    transactions = []

    # Iterate over blocks, starting from the latest
    for block_num in range(latest_block, latest_block - 10000, -1):  # Adjust range as needed
        if len(transactions) >= max_transactions:
            break

        # Convert block number to hex format
        hex_block = hex(block_num)

        # Fetch block by number
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getBlockByNumber",
            "params": [hex_block, True],
            "id": 1,
        }

        block_response = requests.post(rpc_url, json=payload, headers=headers).json()
        block_transactions = block_response['result']['transactions']

        # Filter transactions
        for tx in block_transactions:
            if tx['from'].lower() == wallet_address.lower() or tx['to'].lower() == wallet_address.lower():
                transactions.append(tx)
                if len(transactions) >= max_transactions:
                    break

    return transactions[:max_transactions]


if __name__ == '__main__':
    trans = get_wallet_transactions('0xb98308D11E2B578858Fbe65b793e71C7a0CAa43e', 'https://rpc.linea.build/')

    print(trans)