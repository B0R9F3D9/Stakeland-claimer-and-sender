import asyncio, aiohttp

from .account import Account
from config import MEME_CONTRACT, ERC20_ABI


class Checker:
    def __init__(self, accs: list[Account]) -> None:
        self.accs = accs
        self.meme_contract = accs[0].w3.eth.contract(address=MEME_CONTRACT, abi=ERC20_ABI)
        self.session = None
        self.eth_price = 0
        self.meme_price = 0
            
    async def _get_token_price(self, token: str) -> float:
        async with self.session.get(f'https://api.binance.com/api/v3/ticker/price?symbol={token}USDT') as resp:
            return float((await resp.json())['price'])
    
    async def check_wallet(self, acc: Account) -> dict:
        eth_balance = (await acc.w3.eth.get_balance(acc.address)) / 10**18
        eth_balance_usd = eth_balance * self.eth_price

        meme_balance = (await self.meme_contract.functions.balanceOf(acc.address).call()) / 10**18
        meme_balance_usd = meme_balance * self.meme_price

        async with self.session.get(f'https://memestaking-api.stakeland.com/wallet/info/{acc.address}', proxy=acc.proxy) as resp:
            data = await resp.json()
        smeme_balance = int(data['rewards'][0]['amount']) / 10**18
        smeme_balance_usd = smeme_balance * self.meme_price

        return {
            '№': acc.id,
            'Адрес': acc.addr,
            'Прокси': acc.prox,
            'Адреса для вывода': acc.withdr_addr,
            'Баланс $ETH': f'{eth_balance:.5f} ETH (${eth_balance_usd:.2f})',
            'Баланс $MEME': f'{meme_balance:.1f} MEME (${meme_balance_usd:.2f})',
            'Застейкано $MEME': f'{smeme_balance:.1f} MEME (${smeme_balance_usd:.2f})'
        }

    async def run(self) -> list[dict]:
        self.session = aiohttp.ClientSession()
        self.eth_price = await self._get_token_price('ETH')
        self.meme_price = await self._get_token_price('MEME')
        tasks = [self.check_wallet(acc) for acc in self.accs]
        result = await asyncio.gather(*tasks)
        await self.session.close()
        return result
    