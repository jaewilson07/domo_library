import datetime as dt


def trello_timestr_to_datetime(date_str) -> dt.datetime:
    # 2022-07-14T13:32:11.159Z
    return dt.datetime.strptime(date_str[: 18], '%Y-%m-%dT%H:%M:%S')


def trello_datetime_to_str(tr_datetime) -> dt.datetime:
    # 2022-07-14T13:32:11.159Z
    return tr_datetime.strftime('%Y-%m-%dT%H:%M:%S')
