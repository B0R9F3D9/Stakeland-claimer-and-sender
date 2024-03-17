import asyncio, time, random
from loguru import logger

from web3 import AsyncWeb3, AsyncHTTPProvider, Account as Web3Account
from web3.exceptions import TransactionNotFound
from web3.middleware import async_geth_poa_middleware
from eth_account import Account as EthereumAccount

from settings import GAS_MULTIPLIER, RPC, EXPLORER

Web3Account.enable_unaudited_hdwallet_features()


class Account:
    def __init__(self, account_id: int, key_mnemonic: str, proxy: str | None = None, withdraw_address: str | None = None) -> None:
        self.explorer = EXPLORER
        self.proxy = f'http://{proxy}' if proxy else None
        self.w3 = AsyncWeb3(
            AsyncHTTPProvider(RPC),
            middlewares=[async_geth_poa_middleware],
            request_kwargs={'proxy': self.proxy}
        )
        if key_mnemonic.startswith('0x'):
            self.private_key = key_mnemonic
        else:
            self.private_key = self.w3.eth.account.from_mnemonic(mnemonic=key_mnemonic).key.hex()
        self.account = EthereumAccount.from_key(self.private_key)
        self.address = AsyncWeb3.to_checksum_address(self.account.address)
        self.withdraw_address = AsyncWeb3.to_checksum_address(withdraw_address) if withdraw_address else None
        
        self.id = account_id
        self.addr = f"{self.address[:5]}...{self.address[-5:]}"
        self.withdr_addr = f"{self.withdraw_address[:5]}...{self.withdraw_address[-5:]}" if withdraw_address else 'Не указан'
        self.prox = self.proxy.split('@')[1] if proxy else 'Не указан'
        self.info = f"[№{self.id} - {self.addr}]"

    async def get_tx_data(self, value: int = 0) -> dict:
        return {
            "from": self.address,
            "value": value,
            "nonce": await self.w3.eth.get_transaction_count(self.address),
            "gasPrice": await self.w3.eth.gas_price,
            "chainId": await self.w3.eth.chain_id
        }

    async def wait_tx(self, hash: str) -> None:
        start_time = time.time()
        while True:
            try:
                receipts: dict = await self.w3.eth.get_transaction_receipt(hash)
                status = receipts.get("status")
                if status == 1:
                    logger.success(f"{self.info} Транзакция успешна! {self.explorer+hash}")
                    return
                elif status is None:
                    await asyncio.sleep(0.5)
                else:
                    raise Exception(f"{self.info} Транзакция не удалась! {self.explorer+hash}")
            except TransactionNotFound:
                if time.time() - start_time > 60:
                    raise Exception(f"{self.info} Транзакция не найдена! {self.explorer+hash}")
                await asyncio.sleep(1)

    async def sign(self, transaction: dict) -> dict:
        gas = await self.w3.eth.estimate_gas(transaction)
        gas = int(gas * random.uniform(*GAS_MULTIPLIER))
        transaction['gas'] = gas
        return self.w3.eth.account.sign_transaction(transaction, self.private_key)
    
    async def send_txn(self, txn) -> str:
        signed_txn = await self.sign(txn)
        txn_hash = (await self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)).hex()
        await self.wait_tx(txn_hash)
        return txn_hash
