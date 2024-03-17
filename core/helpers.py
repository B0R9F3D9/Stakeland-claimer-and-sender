import asyncio, random
from loguru import logger

from web3 import AsyncWeb3, AsyncHTTPProvider
from web3.middleware import async_geth_poa_middleware

from settings import RETRY_COUNT, RPC, MAX_GWEI


async def sleep(sleep_from: int, sleep_to: int):
    delay = random.randint(sleep_from, sleep_to)
    logger.info(f'Спим {delay} секунд...')
    for _ in range(delay):
        await asyncio.sleep(1)

def retry(func):
    async def wrapper(*args, **kwargs):
        for i in range(1, RETRY_COUNT+1):
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f'({i}/{RETRY_COUNT}): {e}')
                if i != RETRY_COUNT: await sleep(20, 30)
    return wrapper

def check_gas(func):
    async def _wrapper(*args, **kwargs):
        w3 = AsyncWeb3(AsyncHTTPProvider(RPC), middlewares=[async_geth_poa_middleware])
        while True:
            gas = (await w3.eth.gas_price) / 10**9
            if gas > MAX_GWEI:
                logger.warning(f'Высокий газ: {gas:.1f} > {MAX_GWEI:.1f} Gwei')
                await sleep(20, 30)
            else:
                logger.success(f"Газ в норме: {gas:.1f} < {MAX_GWEI:.1f} Gwei")
                break
        return await func(*args, **kwargs)
    return _wrapper