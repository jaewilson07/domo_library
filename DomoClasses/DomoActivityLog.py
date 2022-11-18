import aiohttp
import datetime as dt
import pandas as pd
from pprint import pprint

from .DomoAuth import DomoFullAuth
from .DomoDataset import DomoDataset
from .routes import activity_log_routes
from ..utils import convert
from ..utils.DictDot import DictDot


class DomoActivityLog:

    @classmethod
    async def get_activity_log(cls, full_auth: DomoFullAuth,
                               start_time: dt.datetime,
                               end_time: dt.datetime,
                               maximum: int = 1000000,
                               object_type: str = None,
                               session: aiohttp.ClientSession = None,
                               debug: bool = False,
                               convert_to_class_dictdot: bool = False) -> list[DictDot]:

        start_time_epoch = convert.convert_datetime_to_epoch_millisecond(
            start_time)
        end_time_epoch = convert.convert_datetime_to_epoch_millisecond(
            end_time)

        is_close_session = False

        if not session:
            session = aiohttp.ClientSession()
            is_close_session = True

        res_activity_log = await activity_log_routes.search_activity_log(full_auth=full_auth,
                                                                         start_time=start_time_epoch,
                                                                         end_time=end_time_epoch,
                                                                         maximum=maximum,
                                                                         object_type=object_type,
                                                                         session=session,
                                                                         debug=debug
                                                                         )
        if is_close_session:
            await session.close()

        if res_activity_log:
            if convert_to_class_dictdot:
                return [DictDot(al) for al in res_activity_log]
            else:
                df = pd.DataFrame(res_activity_log)
                df["time_dt"] = df["time"].apply(
                    lambda x: convert.convert_epoch_millisecond_to_datetime(x))
                df["instance"] = f'{full_auth.domo_instance}.domo.com'
                df["date"] = df["time_dt"].apply(lambda x: x.date())

            return df

        return None
