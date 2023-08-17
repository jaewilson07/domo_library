from dataclasses import dataclass, field

import aiohttp

from ..utils import Exceptions as ex
from ..utils import ResponseGetData as gd
from .routes import auth_routes


class Error(Exception):
    """Base class for other exceptions"""
    pass


class InvalidCredentialsError(Exception):
    def __init__(self, status, message="invalid credentials", domo_instance=None):

        instance_str = f" at {domo_instance}" if domo_instance else None
        self.message = f"Status {status} - {message}{instance_str or ''}" or message
        super().__init__(self.message)


@dataclass
class _DA_Base:
    domo_instance: str


@dataclass
class _DA_Default:
    token: str = field(default=None, repr=False)
    token_name: str = field(default=None)
    user_id: str = field(default=None, repr=False)
    auth_header: dict = field(default_factory=dict, repr=False)

    url_manual_login: str = None

    async def print_is_token(self, token_name=None) -> None:
        self.token_name = token_name
        if not self.token:
            await self.get_auth_token()

        token_str = f"{token_name} "

        if not self.token:
            print(
                f"🚧 failed to retrieve {token_str if token_name else ''}token from {self.domo_instance}")
            return False

        print(
            f"🎉 {token_str if token_name else ''}token retrieved from {self.domo_instance} ⚙️")
        return True


@dataclass
class DomoAuth(_DA_Default, _DA_Base):
    def _init__():
        super().__init__()


@dataclass
class _DFA_Base(_DA_Base):
    domo_username: str
    domo_password: str = field(default=None, repr=False)


@dataclass
class DomoFullAuth(_DA_Default, _DFA_Base):
    """use for full authentication token"""

    def __post_init__(self):
        self.url_manual_login = f"https://{self.domo_instance}.domo.com/auth/index?domoManualLogin=true"

    def generate_auth_header(self, token: str) -> dict:
        self.auth_header = {'x-domo-authentication': token}
        return self.auth_header

    async def get_auth_token(self, domo_instance=None,
                             domo_username=None, domo_password=None,
                             debug: bool = False,
                             session: aiohttp.ClientSession = None) -> gd.ResponseGetData:

        self.domo_username = domo_username or self.domo_username
        self.domo_password = domo_password or self.domo_password
        self.domo_instance = domo_instance or self.domo_instance

        res = await auth_routes.get_full_auth(domo_instance=self.domo_instance,
                                              domo_username=self.domo_username,
                                              domo_password=self.domo_password,
                                              session=session)
        if debug:
            print(res)

        if res.is_success == True:
            self.token = res.response.get('sessionToken')
            self.user_id = res.response.get('userId')

            self.auth_header = self.generate_auth_header(token=self.token)

            return self.token

        elif res.status == 200 and not res.is_success:
            raise InvalidCredentialsError(status=res.status,
                                          message=res.response.get("reason"),
                                          domo_instance=self.domo_instance)

        else:
            raise ex.InvalidInstanceError(
                message=f'invalid instance {self.domo_instance}')


@dataclass(init=False)
class DomoDeveloperAuth(DomoAuth):
    """use for developer authentication token"""
    domo_client_id: str
    domo_client_secret: str
    auth_header: str

    def __init__(self, domo_client_id, domo_client_secret, domo_instance=None):
        self.domo_client_id = domo_client_id
        self.domo_client_secret = domo_client_secret
        super().__init__(domo_instance)

    def generate_auth_header(self, token: str) -> dict:
        self.auth_header = {'Authorization': f'bearer {token}'}
        return self.auth_header

    def generate_auth_header_private(self, token: str) -> dict:
        self.auth_header = {'X-domo-developer-token': f'bearer {token}'}
        return self.auth_header

    async def get_auth_token(self,
                             domo_client_id=None,
                             domo_client_secret=None) -> gd.ResponseGetData:

        self.domo_client_id = domo_client_id or self.domo_client_id
        self.domo_client_secret = domo_client_secret or self.domo_client_secret

        res = await auth_routes.get_developer_auth(domo_client_id=self.domo_client_id,
                                                   domo_client_secret=self.domo_client_secret)

        if res.status == 200 and res.response.get('access_token'):
            self.token = res.response.get('access_token')
            self.user_id = res.response.get('userId')

            self.auth_header = self.generate_auth_header(token=self.token)

            return res

        elif res.status == 200:
            raise InvalidCredentialsError(
                status=res.status, message=res.response.get("reason"))
