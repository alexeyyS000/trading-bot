from datetime import datetime, timedelta


def datetime_to_microtimestamp(datetome_obj: datetime, timedela_obj: timedelta = None):
    return int((datetome_obj + timedela_obj).timestamp() * 1000)
