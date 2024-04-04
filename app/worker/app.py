import math
from celery import Celery
from celery.schedules import crontab
from .config import WorkerSettings
from bot.service import get_user_service
import datetime
from db.client import get_session
from bot.client import get_client
from db.dal.future import KlineDAL, FutureDAL
from bot.parameters import (
    master_symbol,
    master_bar_limit,
    master_timeframe,
    slave_bar_limit,
    min_dayly_volume_dollar,
    slave_timeframe,
)
from bot.client import get_client
from bot.parameters import slave_bar_limit, master_symbol, master_bar_limit

settings = WorkerSettings()
app = Celery(
    "tasks", backend="redis://localhost:6379/0", broker="redis://localhost:6379/1"
)

app.conf.beat_schedule = {
    "parse": {
        "task": "app.add",
        "schedule": crontab(
            minute="*/300"
        ),  # каждые 5 часов добавляются свечи для пересчета исторической корелляции, которая считается по последним 9000 минутных свечей

        "task": "app.update_liquidity_data",
        "schedule": crontab(
            minute="*/1440"
        ),  # каждые 24 часа обновляютя данные о ликвидности инструментов 
        
    },
    # "sand_massage": {
    #     "task": "app.sand",
    #     "schedule": crontab(minute="*/15"),
    # },
}
# app.conf.timezone = "Europe/Moscow"


@app.task(name="app.add")
def add():
    binance_client = get_client()
    with get_user_service(binance_client) as service:
            tickers = service.get_all_pairs()
            for ticker in tickers:

                last_record = service.get_last_kline(symbol=ticker.symbol)
                if not last_record:
                    since_last_update = datetime.timedelta(hours=5)
                    start_time = datetime.datetime.utcnow() - since_last_update
                else:
                    since_last_update = datetime.datetime.utcnow() - last_record.open_time
                    start_time = last_record.open_time + datetime.timedelta(minutes=1)
                if since_last_update <= datetime.timedelta(hours=4, minutes=50):
                    return
                    
                amount_of_requests = math.ceil(since_last_update.total_seconds() / 60 / 999)#убрать хардкод
                end_time = start_time + datetime.timedelta(minutes=999)
                count = 0
                for i in range(amount_of_requests):
                    start_timestamp = int(
                        (
                            start_time + datetime.timedelta(hours=5, minutes=count)
                        ).timestamp()#вынести в функцию 
                        * 1000
                    )  # приходится всегда добавлять 5 часов, потому что всегда при переводе datetime в timestamp добавляется этот спред
                    end_timestamp = int(
                        (end_time + datetime.timedelta(hours=5, minutes=count)).timestamp()
                        * 1000
                    )
                    
                    klines = service.get_klines(
                            symbol = ticker.symbol,
                            interval=binance_client.KLINE_INTERVAL_1MINUTE,
                            startTime = start_timestamp,
                            endTime = end_timestamp,
                        )
                    service.save_klines(klines, ticker.symbol)# обернуть в транзакцию
                    count += 999
                service.save_corellation(master_symbol, ticker.symbol)



@app.task(name="app.update_liquidity_data")
def update_liquidity_data():
    binance_client = get_client()
    with get_user_service(binance_client) as service:
        for ticker, daily_volume in service.select_liquid_pairs(1000000000):
            ticker, is_created = service.get_or_create_pair(ticker, daily_volume = daily_volume)
            if not is_created:
                service.update_pair(ticker.symbol, daily_volume=daily_volume)
