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
    },
    # "sand_massage": {
    #     "task": "app.sand",
    #     "schedule": crontab(minute="*/15"),
    # },
}
app.conf.timezone = "Europe/Moscow"


@app.task(name="app.add")
def add():
    binance_client = get_client()
    with get_user_service(binance_client) as service:
        for symbol, df in service.select_liquid_pairs():
            symbol = service.get_or_create_symbol(symbol, **df)

            last_record = service.get_last_kline(symbol=symbol)
            if not last_record:
                since_last_update = datetime.timedelta(hours=150)
                start_time = datetime.datetime.utcnow() - since_last_update
            else:
                since_last_update = datetime.datetime.utcnow() - last_record.open_time
                start_time = last_record.open_time + datetime.timedelta(minutes=1)
            if since_last_update <= datetime.timedelta(hours=5):
                return
            
            amount_of_requests = int(since_last_update.total_seconds() / 60) / 1000#убрать хардкод
            end_time = start_time + datetime.timedelta(minutes=1000)
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
                )  # на каждой итерации цикла добавляется count - 1001 минута(1001 минутная свеча) потому что нам приходит массив с включенными обоими границами
                with get_user_service() as service:
                    klines = service.get_klines(
                        symbol,
                        binance_client.KLINE_INTERVAL_1MINUTE,
                        start_timestamp,
                        end_timestamp,
                    )
                    service.save_klines(klines)# обернуть в транзакцию
                count += 1001


# @app.task(name="app.sand")
# def send():
#     with get_session() as session:
#         fundings = FundingDAL(session).all()
#     immediate_fundings = []
#     for i in fundings:
#         if i.date_time - datetime.utcnow() <= timedelta(minutes=10):
#             immediate_fundings.append(i)
#     if immediate_fundings:
#         with get_session() as session:
#             users = UserDAL(session).filter(subscriber=True).all()
#         users_id = []
#         for i in users:
#             users_id.append(i.id)
#         funding_alert(users_id, immediate_fundings)

# Fundings happen every 4 or 8 hours, so the algorithm starts 10 minutes before the funding,
# and then checks the subsequent ones every 4 hours
