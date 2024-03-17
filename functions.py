from tabulate import tabulate

from core import *


async def auto(acc: Account) -> None:
    await Stakeland(acc).unstake()
    await sleep(10, 15) # ожидание анстейка
    await Stakeland(acc).transfer_meme()

async def unstake(acc: Account) -> None:
    await Stakeland(acc).unstake()

async def trasnfer(acc: Account) -> None:
    await Stakeland(acc).transfer_meme()

async def checker_module(accs: list[Account]) -> None:
    result: list[dict] = await Checker(accs).run()
    result.sort(key=lambda x: x['№'])
    print(tabulate(result, headers="keys", tablefmt="rounded_grid"))
