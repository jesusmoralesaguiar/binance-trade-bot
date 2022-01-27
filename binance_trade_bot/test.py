import threading
import logging

import json
import math
import time
import traceback
from typing import Dict, Optional

from binance_trade_bot.binance_api_manager import BinanceAPIManager
# from .binance_api_manager import BinanceAPIManager
from binance_trade_bot.config import Config
from binance_trade_bot.database import Database
from binance_trade_bot.logger import Logger
# from .config import Config
# from .database import Database
# from .logger import Logger

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s', )


def worker_with(lock, message):
    with lock:
        n = 0
        while n < 10:
            logging.debug(f"Contamos {n}:{message}")
            n += 1


if __name__ == '__main__':
    # lock = threading.Lock()
    # w = threading.Thread(target=worker_with, args=(lock, "tarea1"))
    # nw = threading.Thread(target=worker_with, args=(lock, "tarea2"))
    #
    # w.start()
    # nw.start()
    logger = Logger()
    config = Config()
    db = Database(logger, config)
    manager = BinanceAPIManager(config, db, logger)
    with manager.cache.open_balances() as cache_balances:
        balance = cache_balances.get("ZEN", None)
        print(f"BALANCE: {balance}")
        print(f"Acount balances: {manager.binance_client.get_account()['balances']}")
        cache_balances.clear()
        cache_balances.update(
            {
                currency_balance["asset"]: float(currency_balance["free"])
                for currency_balance in manager.binance_client.get_account()["balances"]
            }
        )
        logger.debug(f"Fetched all balances: {cache_balances}")