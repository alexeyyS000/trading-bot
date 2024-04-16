import datetime
import math

from celery import Celery
from celery.schedules import crontab

from bot.client import get_client
from bot.parameters import StrategySettings
from bot.service import get_future_service
from utils.general import datetime_to_microtimestamp

from .config import WorkerSettings

strategy_settings = StrategySettings()

settings = WorkerSettings()
app = Celery("tasks")

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
        "task": "app.manage_position",
        "schedule": crontab(
            minute="*/15"
        ),  # каждые 15 мин проверяется текущая корреляция и если она расходится с исторической открывается позиция на сведение, если позиция открыта - принимается решение о добавоение или фиксации
    },
}


@app.task(name="app.add")  # обработать ошибки, прописать условия ретрая
def add():
    binance_client = get_client()
    now_datetime = datetime.datetime.utcnow()
    with get_future_service(binance_client) as service:
        tickers = service.get_all_pairs()
        for ticker in tickers:
            last_record = service.get_last_kline(symbol=ticker.symbol)
            if not last_record:
                since_last_update = datetime.timedelta(
                    minutes=strategy_settings.master_bar_limit
                )
                start_time = now_datetime - since_last_update
            else:
                since_last_update = now_datetime - last_record.open_time
                start_time = last_record.open_time + datetime.timedelta(minutes=1)
            if since_last_update <= datetime.timedelta(hours=4):
                continue

            amount_of_requests = math.ceil(
                since_last_update.total_seconds()
                / 60
                / strategy_settings.klines_in_one_query
            )
            end_time = start_time + datetime.timedelta(
                minutes=strategy_settings.klines_in_one_query
            )
            count = 0
            for i in range(amount_of_requests):
                start_timestamp = datetime_to_microtimestamp(
                    start_time, datetime.timedelta(hours=5, minutes=count)
                )  # сделать поле времени в БД с timezoneInfo чтобы не добавлять 5 часов
                end_timestamp = datetime_to_microtimestamp(
                    end_time, datetime.timedelta(hours=5, minutes=count)
                )

                klines = service.get_klines(
                    symbol=ticker.symbol,
                    interval=binance_client.KLINE_INTERVAL_1MINUTE,
                    startTime=start_timestamp,
                    endTime=end_timestamp,
                )

                service.save_klines(
                    klines, ticker.symbol
                )  # обернуть в транзакцию коммитить ее после всех циклов,

                count += strategy_settings.klines_in_one_query

            if ticker.symbol != strategy_settings.master_symbol:
                service.recalculate_corellation(
                    strategy_settings.master_symbol,
                    ticker.symbol,
                    strategy_settings.master_bar_limit,
                )


@app.task(name="app.update_liquidity_data")
def update_liquidity_data():
    binance_client = get_client()
    with get_future_service(binance_client) as service:
        for ticker, daily_volume in service.select_liquid_pairs(
            strategy_settings.min_dayly_volume_dollar
        ):
            ticker, is_created = service.get_or_create_pair(
                ticker, daily_volume=daily_volume
            )
            if not is_created:
                service.update_pair(ticker.symbol, daily_volume=daily_volume)


@app.task(name="app.manage_position")
def manage_position():
    binance_client = get_client()
    with get_future_service(binance_client) as service:
        actual_pairs = service.filter_actual_tickers()
        master_klines_short_term = service.get_klines(# не выбрасывать эти свечи, сохранять к историческим если таймфрейм совпадает
            strategy_settings.master_symbol,
            binance_client.KLINE_INTERVAL_1MINUTE,
            limit=strategy_settings.slave_bar_limit,
        )
        for pair in actual_pairs:
            if pair.symbol == strategy_settings.master_symbol:
                continue
            slave_klines_short_term = service.get_klines(
                pair.symbol,
                binance_client.KLINE_INTERVAL_1MINUTE,
                limit=strategy_settings.slave_bar_limit,
            )
            master_dataframe = service.get_dataframe(master_klines_short_term)
            slave_dataframe = service.get_dataframe(slave_klines_short_term)

            corellation = service.calculate_short_term_correlation(
                master_dataframe["close"].astype(float),
                slave_dataframe["close"].astype(float),
            )
            position = service.get_position(symbol=pair.symbol)
            if corellation <= 0.3 and not position:
                price = service.get_market_price(pair.symbol)
                quantity = service.convert_dollar_to_quantity(
                    strategy_settings.position_volume_in_usd, price
                )
                side = service.calculate_side(slave_klines_short_term)
                try:
                    service.order_future(pair.symbol, quantity, side)
                except:
                    return  # тут тоже не забыть про ретраи
                service.save_position(pair.symbol, quantity, corellation)

                return

            if position and position.last_short_term_corellation - corellation >= 10:
                price = service.get_market_price(pair.symbol)
                quantity = service.convert_dollar_to_quantity(
                    strategy_settings.position_volume_in_usd, price
                )
                side = service.calculate_side(slave_klines_short_term)
                if side := position.side:
                    service.position_close(pair.symbol)
                service.order_future(pair.symbol, quantity, side)
                service.update_position(
                    pair.symbol,
                    current_trade_volume=position.current_trade_volume + quantity,
                    last_short_term_corellation=corellation,
                )

                return

            if position and corellation >= service.get_history_correlation():
                service.position_close(pair.symbol)
