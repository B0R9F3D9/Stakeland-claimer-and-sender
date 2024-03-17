# Максимальный GWEI
MAX_GWEI: int = 20

# Использовать прокси
USE_PROXY: bool = False

# Перемешать кошельки
SHUFFLE_WALLETS: bool = False

# Мин, макс время ожидания между аккаунтами
SLEEP_BETWEEN_ACCS: tuple[int, int] = (10, 15)

# Мин, макс процент баланса $sMEME для анстейка
UNSTAKE_PERCENT: tuple[int, int] = (100, 100)

# Мин, макс процент баланса $MEME для перевода
TRANSFER_PERCENT: tuple[int, int] = (100, 100)

# Количество попыток для совершения действий
RETRY_COUNT: int = 1

# Мин, макс мультипликатор газа для транзакций
GAS_MULTIPLIER: tuple[float, float] = (1, 1)

# Прочее
RPC: str = 'https://rpc.ankr.com/eth'
EXPLORER: str = 'https://etherscan.io/tx/'
