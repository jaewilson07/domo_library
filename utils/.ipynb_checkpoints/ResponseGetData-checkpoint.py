from dataclasses import dataclass, field

from .Base import Base


@dataclass
class ResponseGetData(Base):
    status: int
    response: any
    is_success: bool
    auth: dict = field(default=None)

    def __post_init__(self):
        super().__init__()
