import random, asyncio, sys
from datetime import datetime
from loguru import logger
from questionary import Choice, select

from config import *
from core import *
from settings import *
from functions import *


def get_accounts() -> list[Account]:
    accs = []
    for _id, key_mnemonic in enumerate(KEY_MNEMONICS, 1):
        proxy = PROXIES.get(_id) if USE_PROXY else None
        withdraw_address = WITHDRAW_ADDRESSES.get(_id)
        accs.append(Account(_id, key_mnemonic, proxy, withdraw_address))
    return accs

def select_accounts() -> list[Account]:
    if len(ACCOUNTS) == 1:
        return ACCOUNTS
    print('Выберите аккаунты для работы. Формат: \n'
        '1 — для выбора только первого аккаунта\n'
        '1,2,3 — для выбора первого, второго и третьего аккаунта\n'
        '1-3 — для выбора аккаунтов от первого до третьего включительно\n'
        'all — для выбора всех аккаунтов (или нажмите Enter)\n')
    result = input('Введите ваш выбор: ')
    if result == 'all' or result == '':
        return ACCOUNTS
    try:
        if ',' in result:
            return [ACCOUNTS[int(i) - 1] for i in result.split(',')]
        elif '-' in result:
            return ACCOUNTS[int(result.split('-')[0]) - 1:int(result.split('-')[1])]
        elif '-' not in result and ',' not in result:
            return [ACCOUNTS[int(result) - 1]]
    except ValueError:
        raise ValueError('Некорректный выбор аккаунтов!')

async def get_module() -> str:
    return await select(
        message="Выберите модуль для работы: ",
        instruction='(используйте стрелочки для навигации)',
        choices=[
            Choice("🧠 Автоматический маршрут", auto),
            Choice("🎁 Анстейк $MEME", unstake),
            Choice("🛫 Отправка $MEME", trasnfer),
            Choice("📊 Чекер", checker_module),
            Choice("🔙 Вернуться к выбору аккаунтов", 'back'),
            Choice("❌ Выход", "exit"),
        ],
        qmark="\n❓ ",
        pointer="👉 "
    ).ask_async()

async def main(accs: list[Account]) -> None | bool:
    module = await get_module()
    if module == checker_module:
        await checker_module(accs)
        return
    elif module == 'back':
        return True
    elif module == 'exit':
        raise KeyboardInterrupt
    for acc in accs:
        await module(acc)
        if acc != accs[-1]:
            await sleep(*SLEEP_BETWEEN_ACCS)


if __name__ == '__main__':
    logger.remove()
    format='<white>{time:HH:mm:ss}</white> | <bold><level>{level: <7}</level></bold> | <level>{message}</level>'
    logger.add(sink=sys.stderr, format=format)
    logger.add(sink=f'logs/{datetime.today().strftime("%Y-%m-%d")}.log', format=format)

    ACCOUNTS = get_accounts()
    logger.info(f'Найдено: {len(ACCOUNTS)} кошельков, {len(PROXIES)} прокси, {len(WITHDRAW_ADDRESSES)} адресов для вывода')

    if SHUFFLE_WALLETS:
        random.shuffle(ACCOUNTS)
        for id, acc in enumerate(ACCOUNTS, 1):
            acc.id = id
            acc.info = f"[№{acc.id} - {acc.addr}]"
        logger.warning('Кошельки перемешаны!')
    if USE_PROXY:
        logger.warning('Используются прокси!')
    else:
        logger.warning('Прокси не используются!')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(checker_module(ACCOUNTS))
    selected_accs = select_accounts()

    while True:
        try:
            result = loop.run_until_complete(main(selected_accs))
            if result:
                loop.run_until_complete(checker_module(ACCOUNTS))
                selected_accs = select_accounts()
        except KeyboardInterrupt:
            break
        except Exception as e:
           logger.critical(e)
           break

    print('👋👋👋')
