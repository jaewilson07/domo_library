import datetime as dt


def convert_epoch_millisecond_to_datetime(epoch: int):
    '''convert Epoch time with miliseconds to Date time'''
    return dt.datetime.fromtimestamp(epoch / 1000.0)


def convert_datetime_to_epoch_millisecond(datetime: dt.datetime):
    '''convert DateTime to Epoch time with Miliseconds'''
    return int(datetime.timestamp() * 1000)


def convert_snake_to_pascal(str):
    clean_str = str.replace("_", " ").title().replace(" ", "")
    return clean_str[0].lower()+clean_str[1:]
