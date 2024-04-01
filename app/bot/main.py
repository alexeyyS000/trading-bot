# from bot.service import FutureService
# from db.client import get_session
# from bot.client import get_client
# import datetime

# client = get_client()

# #date = datetime.datetime()
# data = client.futures_klines(symbol = 'BTCUSDT',interval = '1m', start_str = datetime.datetime(2024, 3, 30, 11, ).timestamp()*1000)

# for i in data:
#     k = datetime.datetime.utcfromtimestamp(int(i[6])/ 1000).strftime('%Y-%m-%d %H:%M:%S')
#     print(k, 'timestamp:', datetime.datetime.utcfromtimestamp(int(i[0])/ 1000).strftime('%Y-%m-%d %H:%M:%S'), 'close:',i[4])


# from binance.client import Client
# from datetime import datetime

# client = Client()

# start_time = datetime(2024, 3, 30, 11,)
# end_time = datetime(2024, 3, 30, 11, 30)

# klines = client.futures_klines(symbol='BTCUSDT', interval='1m', startTime=start_time.strftime('%Y-%m-%d %H:%M:%S'), endTime=end_time.strftime('%Y-%m-%d %H:%M:%S'))

# for i in klines:
#     k = datetime.utcfromtimestamp(int(i[6])/ 1000).strftime('%Y-%m-%d %H:%M:%S')
#     print(k, 'timestamp:', datetime.utcfromtimestamp(int(i[0])/ 1000).strftime('%Y-%m-%d %H:%M:%S'), 'close:',i[4])


from binance.client import Client
from datetime import datetime, timedelta, timezone

api_key = "YOUR_API_KEY"
api_secret = "YOUR_API_SECRET"

client = Client(api_key, api_secret)

start_time = datetime(
    2024,
    3,
    30,
    10,
    tzinfo=timezone.utc
)
end_time = datetime(2024, 3, 30, 10, 10, tzinfo=timezone.utc)

print(end_time.tzinfo)


# print(start_time, datetime.utcfromtimestamp(start_timestamp/ 1000).strftime('%Y-%m-%d %H:%M:%S'))
candles = client.futures_klines(
    symbol="BTCUSDT",
    interval="1m",
    startTime=int((start_time + timedelta(minutes=0)).timestamp()),
    endTime=int((end_time + timedelta(minutes=0)).timestamp()),
)


for i in candles:
    k = datetime.utcfromtimestamp(int(i[6]) / 1000).strftime("%Y-%m-%d %H:%M:%S")
    print(
        "timestamp:",
        datetime.utcfromtimestamp(int(i[0]) / 1000).strftime("%Y-%m-%d %H:%M:%S"),
        "closetime",
        k,
        "close:",
        i[4],
    )


# candles = client.futures_klines(
#     symbol="BTCUSDT",
#     interval="1m",
#     startTime=int((start_time + timedelta(hours=5, minutes=11)).timestamp() * 1000),
#     endTime=int((end_time + timedelta(hours=5, minutes=11)).timestamp() * 1000),
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


# print("------")

# candles = client.futures_klines(
#     symbol="BTCUSDT",
#     interval="1m",
#     startTime=int((start_time + timedelta(hours=5, minutes=11)).timestamp() * 1000),
#     endTime=int((end_time + timedelta(hours=5, minutes=2)).timestamp() * 1000),
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


# print("+++====+++++")
# start_time = datetime(2024, 3, 30, 20, 45)
# end_time = datetime(2024, 3, 30, 20, 55)
# candles = client.futures_klines(
#     symbol="BTCUSDT",
#     interval="1m",
#     startTime=int(
#         (
#             start_time
#             + timedelta(
#                 hours=5,
#             )
#         ).timestamp()
#         * 1000
#     ),
#     endTime=int(
#         (
#             end_time
#             + timedelta(
#                 hours=5,
#             )
#         ).timestamp()
#         * 1000
#     ),
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


# ВРЕМЕННОЙ CДВИГ
