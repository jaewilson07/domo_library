import aiohttp
from abc import abstractmethod, ABC
from dataclasses import dataclass

from .routes import auth_routes
from ..utils import Exceptions
from ..utils.Base import Base
from ..utils.ResponseGetData import ResponseGetData


class TrelloAuth(ABC):
    def __init__(self, consumer_key):
        self.consumer_key = consumer_key

        super().__init__()


@dataclass(init=False)
class TrelloOauth(TrelloAuth):
    consumer_key: str
    consumer_secret: str

    token: str
    token_secret: str

    def __init__(self, consumer_key, consumer_secret):
        self.consumer_secret = consumer_secret

        super().__init__(consumer_key)

    async def get_oauth_token(self):
        token, token_secret = await auth_routes.get_oauth1_token_and_secret(consumer_key=self.consumer_key,
                                                                            consumer_secret=self.consumer_secret)
        self.token = token
        self.token_secret = token_secret


@dataclass(init=False)
class TrelloWebAuth(TrelloAuth):
    token: str
    consumer_key: str

    def __init__(self, consumer_key, token):
        self.token = token

        super().__init__(consumer_key)
