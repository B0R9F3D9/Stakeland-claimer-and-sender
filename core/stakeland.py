import random, aiohttp
from loguru import logger

from .account import Account
from .helpers import retry, check_gas
from settings import UNSTAKE_PERCENT, TRANSFER_PERCENT
from config import STAKELAND_CONTRACT, MEME_CONTRACT, ERC20_ABI


class Stakeland:
    def __init__(self, acc: Account) -> None:
        self.acc = acc
        
    @retry
    @check_gas
    async def unstake(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=f'https://memestaking-api.stakeland.com/wallet/info/{self.acc.address}',
                proxy=self.acc.proxy
            ) as resp:
                data = (await resp.json())['rewards'][0]
        smeme_balance = int(data['amount'])
        amount = int(int(data['amount']) * random.uniform(*UNSTAKE_PERCENT) / 100)
        proofs = [line[2:] for line in data['proof']]

        logger.info(f'{self.acc.info} Делаю анстейк {amount/10**18:.1f} MEME...')

        data = '0xe1c8455d' + '0'*(64-len(hex(amount)[2:])) + hex(amount)[2:] + \
            '0000000000000000000000000000000000000000000000000000000000000040' + \
            '0000000000000000000000000000000000000000000000000000000000000001' + \
            '0000000000000000000000000000000000000000000000000000000000000020' + \
            '0000000000000000000000000000000000000000000000000000000000000001' + \
            '0'*(64-len(hex(smeme_balance)[2:])) + hex(smeme_balance)[2:] + \
            '0000000000000000000000000000000000000000000000000000000000000060' + \
            '0000000000000000000000000000000000000000000000000000000000000012' + \
            ''.join(proofs)
        txn = await self.acc.get_tx_data() | {'to': STAKELAND_CONTRACT, 'data': data}
        await self.acc.send_txn(txn)

    @retry
    @check_gas
    async def transfer_meme(self) -> None:
        if not self.acc.withdraw_address:
            logger.error(f'{self.acc.info} Отправка невозможна! Не указан адрес для вывода')
            return
        
        contract = self.acc.w3.eth.contract(address=MEME_CONTRACT, abi=ERC20_ABI)
        meme_balance = await contract.functions.balanceOf(self.acc.address).call()
        amount = int(meme_balance * random.uniform(*TRANSFER_PERCENT) / 100)

        logger.info(f'{self.acc.info} Перевожу {amount/10**18:.1f} MEME на {self.acc.withdr_addr}')

        data = '0xa9059cbb' + \
            '0'*(64-len(self.acc.withdraw_address[2:])) + self.acc.withdraw_address[2:].lower() + \
            '0'*(64-len(hex(amount)[2:])) + hex(amount)[2:]
        txn = await self.acc.get_tx_data() | {'to': MEME_CONTRACT, 'data': data}
        await self.acc.send_txn(txn)
