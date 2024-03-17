import json

with open("data/wallets.txt", "r") as file:
    KEY_MNEMONICS = [x.strip() for x in file.readlines()]

with open('data/proxies.txt', 'r') as file:
    PROXIES = {i: x.strip() for i, x in enumerate(file.readlines(), 1)}

with open('data/withdraw_addresses.txt', 'r') as file:
    WITHDRAW_ADDRESSES = {i: x.strip() for i, x in enumerate(file.readlines(), 1)}

with open('data/abi/erc20.json', 'r') as file:
    ERC20_ABI = json.load(file)

STAKELAND_CONTRACT: str = '0xC059A531B4234D05E9ef4ac51028F7E6156E2CCe'
MEME_CONTRACT: str = '0xb131f4A55907B10d1F0A50d8ab8FA09EC342cd74'
