#!python3
import time

from .binance_api_manager import BinanceAPIManager
from .config import Config
from .database import Database
from .logger import Logger
from .scheduler import SafeScheduler
from .strategies import get_strategy


def main():
    logger = Logger()
    logger.info("Starting")
    #Config principal
    config = Config()
    db = Database(logger, config)
    # Inicializamos El BinanceAPI
    # Creamos el WebSocket y Cargamos el Buffer
    manager = BinanceAPIManager(config, db, logger)
    # check if we can access API feature that require valid config
    try:
        _ = manager.get_account()
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Couldn't access Binance API - API keys may be wrong or lack sufficient permissions")
        logger.error(e)
        return
    # Cargamos la estrategia
    #
    strategy = get_strategy(config.STRATEGY)
    if strategy is None:
        logger.error("Invalid strategy name")
        return
    trader = strategy(manager, db, logger, config)
    logger.info(f"Chosen strategy: {config.STRATEGY}")

    logger.info("Creating database schema if it doesn't already exist")
    ## Retrieve all coin pairs
    # exchange_info = manager.binance_client.get_exchange_info()
    # for s in exchange_info['symbols']:
    #     print(s['symbol'])
    db.create_database()

    db.set_coins(config.SUPPORTED_COIN_LIST)
    db.migrate_old_state()

    # Añadimos la current coin en db (Sino la especificamos coge una random)
    # Añadimos los valores pair from/to coin
    trader.initialize()

    schedule = SafeScheduler(logger)
    #Empezamos el scouting
    schedule.every(config.SCOUT_SLEEP_TIME).seconds.do(trader.scout).tag("scouting")
    schedule.every(1).minutes.do(trader.update_values).tag("updating value history")
    schedule.every(1).minutes.do(db.prune_scout_history).tag("pruning scout history")
    schedule.every(1).hours.do(db.prune_value_history).tag("pruning value history")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    finally:
        manager.stream_manager.close()
