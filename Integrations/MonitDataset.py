from dataclasses import dataclass, field
import pandas as pd
import datetime as dt
import decimal

from Library.DomoClasses import DomoDataset as dcds
from Library.DomoClasses import DomoStream as dcdstr


@dataclass
class MonitDataset_Record:
    id: str = None
    stream_account_id: int = None
    stream_account_userid: int = None
    nb_partitions: int = 0
    name: str = None
    data_provider_type: str = None
    display_type: str = None
    stream_id: str = None
    stream_config_tables: str = None
    stream_config_query: str = None
    instance: str = None
    owner: str = None
    row_count: int = None
    url: str = None
    report_date: dt.datetime = dt.datetime.now()
    tags: list = field(default=None)
    is_certified: int = 0
    certification_name: str = None
    connector_version: decimal.Decimal(2) = None
    update_method: str = None
    connector_id: str = None


@dataclass
class MonitDataset_Data:
    ds: dcds.DomoDataset = None
    stream_ds: dcdstr.DomoStream = None
    partition_ls: list = None
