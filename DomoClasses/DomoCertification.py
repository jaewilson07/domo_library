import datetime as dt
from dataclasses import dataclass
from enum import Enum

from ..utils import convert as cd
from ..utils.DictDot import DictDot


class DomoCertificationState(Enum):
    CERTIFIED = 'certified'


@dataclass
class DomoCertification:
    certification_state: DomoCertificationState
    last_updated: dt.datetime
    certification_type: str
    certification_name: str

    @classmethod
    def _from_json(cls, dd):
        return cls(certification_state=DomoCertificationState[dd.state].value or dd.state,
                   last_updated=cd.convert_epoch_millisecond_to_datetime(
                       dd.lastUpdated),
                   certification_type=dd.processType,
                   certification_name=dd.processName
                   )
