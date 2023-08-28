import json
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class Config(Enum):
    PGSQL = {
        "type": "CONNECTOR",
        "description": "com.domo.connector.postgre.data",
        "version": "2",
        "dataProvider_key": "postgresql"
    }
    PGSQL_PARTITION = {
        "type": "CONNECTOR",
        "description": "com.domo.connector.postgresql.partition",
        "version": "0",
        "dataProvider_key": "postgresql-partition"
    }

    ATHENA_HIGHBANDWIDTH = {
        "type": "CONNECTOR",
        "description": "com.domo.connector.amazonathena.highbandwidth",
        "version": "0",
        "dataProvider_key": "amazon-athena-high-bandwidth"
    }

    SNOWFLAKE_UNLOADv2 = {
        "type": "CONNECTOR",
        "description": "com.domo.connector.snowflakeunloadv2",
        "version": "1",
        "dataProvider_key": "snowflake-unload-v2"
    }


class UpdateMethod(Enum):
    REPLACE = 'REPLACE'
    APPEND = 'APPEND'


@dataclass
class Transport:
    type: str
    description: str
    version: str


class ConfigurationParam_Category(Enum):
    METADATA = 'METADATA'


@dataclass
class ConfigurationParam:
    name: str
    value: Any
    type: str = 'string'
    category: ConfigurationParam_Category = ConfigurationParam_Category.METADATA.value


@dataclass
class Account:
    id: int


@dataclass
class Datasource:
    name: str
    description: str


class Schedule_Type(Enum):
    DAY = 'DAY'
    MANUAL = 'MANUAL'


@dataclass
class Schedule:
    type: Schedule_Type
    at: str = None
    timezone: str = 'UTC'

    def to_dict(self):
        return asdict(self)


@dataclass
class DataProvider:
    key: str


@dataclass
class Configuration:
    transport: Transport
    configuration: list[ConfigurationParam]
    account: Account
    updateMethod: UpdateMethod
    dataProvider: DataProvider
    dataSource: Datasource
    advancedScheduleJson: Schedule

    def __post_init__(self):
        if not self.advancedScheduleJson:
            self.advancedScheduleJson = Schedule(
                type=Schedule_Type.MANUAL.value)

    def to_dict(self):
        clean_self = self

        advancedSchedule = clean_self.advancedScheduleJson.to_dict()

        if advancedSchedule.get('at') is None:
            del advancedSchedule['at']

        clean_self.advancedScheduleJson = json.dumps(advancedSchedule)
        return asdict(clean_self)
