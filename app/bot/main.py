# from binance.client import Client
# from datetime import datetime, timedelta, timezone
# import pytz
# api_key = "YOUR_API_KEY"
# api_secret = "YOUR_API_SECRET"

# client = Client(api_key, api_secret)

# start_time = datetime(
#     2024,
#     3,
#     30,
#     10,
    
# )
# end_time = start_time + timedelta(minutes=8)
# #tzinfo=timezone.utc


# # print(start_time, datetime.utcfromtimestamp(start_timestamp/ 1000).strftime('%Y-%m-%d %H:%M:%S'))
# candles = client.futures_klines(
#     symbol="BTCUSDT",
#     interval="1m",
#     startTime=int((start_time + timedelta(hours=5, minutes=0)).timestamp())*1000,
#     endTime=int((end_time + timedelta(hours=5, minutes=0)).timestamp())*1000,
# )


# for i in candles:
#     k = datetime.utcfromtimestamp(int(i[6]) / 1000).strftime("%Y-%m-%d %H:%M:%S")
#     print(
#         "timestamp:",
#         datetime.utcfromtimestamp(int(i[0]) / 1000).strftime("%Y-%m-%d %H:%M:%S"),
#         "closetime",
#         k,
#         "close:",
#         i[4],
#     )
# print(len(candles))

# candles = client.futures_klines(
#     symbol="BTCUSDT",
#     interval="1m",
#     startTime=int((start_time + timedelta(hours=5, minutes=9)).timestamp() * 1000),
#     endTime=int((end_time + timedelta(hours=5, minutes=9)).timestamp() * 1000),
# )
# print("--------")
# for i in candles:
#     k = datetime.utcfromtimestamp(int(i[6]) / 1000).strftime("%Y-%m-%d %H:%M:%S")
#     print(
#         "timestamp:",
#         datetime.utcfromtimestamp(int(i[0]) / 1000).strftime("%Y-%m-%d %H:%M:%S"),
#         "closetime",
#         k,
#         "close:",
#         i[4],
#     )
# print(len(candles))


# print("------")

# candles = client.futures_klines(
#     symbol="BTCUSDT",
#     interval="1m",
#     startTime=int((start_time + timedelta(hours=5, minutes=18)).timestamp() * 1000),
#     endTime=int((end_time + timedelta(hours=5, minutes=18)).timestamp() * 1000),
# )

# for i in candles:
#     k = datetime.utcfromtimestamp(int(i[6]) / 1000).strftime("%Y-%m-%d %H:%M:%S")
#     print(
#         "timestamp:",
#         datetime.utcfromtimestamp(int(i[0]) / 1000).strftime("%Y-%m-%d %H:%M:%S"),
#         "closetime",
#         k,
#         "close:",
#         i[4],
#     )
# print(len(candles))






import math
from bot.service import get_user_service
import datetime
from bot.client import get_client
from bot.client import get_client
from db.client import get_session
from db.dal.future import KlineDAL

# def add():
#     binance_client = get_client()
#     with get_user_service(binance_client) as service:
#             tickers = service.get_all_pairs()
#             for ticker in tickers:

#                 last_record = service.get_last_kline(symbol=ticker.symbol)
#                 if not last_record:
#                     since_last_update = datetime.timedelta(hours=5)
#                     start_time = datetime.datetime.utcnow() - since_last_update
#                 else:
#                     since_last_update = datetime.datetime.utcnow() - last_record.open_time
#                     start_time = last_record.open_time + datetime.timedelta(minutes=1)
#                 if since_last_update <= datetime.timedelta(hours=4, minutes=50):
#                     return
                    
#                 amount_of_requests = math.ceil(since_last_update.total_seconds() / 60 / 99)#убрать хардкод
#                 end_time = start_time + datetime.timedelta(minutes=99)
#                 count = 0
#                 for i in range(amount_of_requests):
#                     start_timestamp = int(
#                         (
#                             start_time + datetime.timedelta(hours=5, minutes=count)
#                         ).timestamp()#вынести в функцию 
#                         * 1000
#                     )  # приходится всегда добавлять 5 часов, потому что всегда при переводе datetime в timestamp добавляется этот спред
#                     end_timestamp = int(
#                         (end_time + datetime.timedelta(hours=5, minutes=count)).timestamp()
#                         * 1000
#                     )  # на каждой итерации цикла добавляется count - 1001 минута(1001 минутная свеча) потому что нам приходит массив с включенными обоими границами
                    
#                     klines = service.get_klines(
#                             symbol = ticker.symbol,
#                             interval=binance_client.KLINE_INTERVAL_1MINUTE,
#                             startTime = start_timestamp,
#                             endTime = end_timestamp,
#                         )
#                     print(len(klines))
#                     if len(klines) == 3:
#                          print(klines, ticker.symbol)
#                     service.save_klines(klines, ticker.symbol)# обернуть в транзакцию
#                     count += 99
# add()

# with get_session() as session:
#     k = KlineDAL(session).delete_all()

# with get_session() as session:
#     k = KlineDAL(session).get_corellation('BTCUSDT', 'ENAUSDT')
#     print(k)

from db.dal.future import FutureDAL

def update(**kwargs):
    with get_session() as session:
        FutureDAL(session).update_one(kwargs, symbol = 'testr')

update(daily_volume = 88888)