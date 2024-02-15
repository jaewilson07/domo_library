# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/client/95_DomoAuth.ipynb.

# %% auto 0
__all__ = [
    "DomoAuth",
    "DomoFullAuth",
    "test_is_full_auth",
    "DomoTokenAuth",
    "DomoDeveloperAuth",
    "DomoJupyterAuth",
    "DomoJupyterFullAuth",
    "DomoJupyterTokenAuth",
    "test_is_jupyter_auth",
]

# %% ../../nbs/client/95_DomoAuth.ipynb 3
from dataclasses import dataclass, field
from typing import Optional, Union
from urllib.parse import urlparse


import httpx

import domolibrary.client.ResponseGetData as rgd
import domolibrary.client.Logger as lg
import domolibrary.client.DomoError as de

import domolibrary.routes.auth as auth_routes

# %% ../../nbs/client/95_DomoAuth.ipynb 4
from domolibrary.routes.auth import (
    AccountLockedError,
    InvalidAuthTypeError,
    InvalidCredentialsError,
    InvalidInstanceError,
    NoAccessTokenReturned,
)


# %% ../../nbs/client/95_DomoAuth.ipynb 7
@dataclass
class _DomoAuth_Required:
    """required parameters for all Domo Auth classes"""

    domo_instance: str

    def __post_init__(self):
        if self.domo_instance:
            self.set_manual_login()

    def set_manual_login(self):
        self.url_manual_login = (
            f"https://{self.domo_instance}.domo.com/auth/index?domoManualLogin=true"
        )
        return self.url_manual_login

    async def who_am_i(
        self, debug_api: bool = False, session: httpx.AsyncClient = None
    ):

        auth_header = self.auth_header or await self.generate_auth_header()

        res = await auth_routes.who_am_i(
            domo_instance=self.domo_instance,
            auth_header=auth_header,
            parent_class=self.__class__.__name__,
        )

        return res

    async def print_is_token(self, token_name=None) -> None:

        if not self.token:
            await self.get_auth_token()

        self.token_name = token_name or self.token_name
        token_str = f"{self.token_name} " or ""

        if not self.token:
            print(f"🚧 failed to retrieve {token_str}token from {self.domo_instance}")
            return False

        print(f"🎉 {token_str }token retrieved from {self.domo_instance} ⚙️")
        return True


@dataclass
class _DomoAuth_Optional:
    """parameters are defined after initialization"""

    token: str = field(default=None, repr=False)
    token_name: str = field(default=None)
    user_id: str = field(default=None, repr=False)
    auth_header: dict = field(default=None, repr=False)

    is_valid_token: bool = None

    url_manual_login: Optional[str] = None

    async def get_auth_token(self) -> Union[str, None]:
        """placeholder method"""
        pass

    async def generate_auth_header(self) -> Union[dict, None]:
        """returns auth header appropriate for this authentication method"""
        pass


# %% ../../nbs/client/95_DomoAuth.ipynb 8
@dataclass
class DomoAuth(_DomoAuth_Optional, _DomoAuth_Required):
    """abstract DomoAuth class"""


# %% ../../nbs/client/95_DomoAuth.ipynb 12
@dataclass
class _DomoFullAuth_Required:
    """mix requied parameters for DomoFullAuth"""

    domo_username: str
    domo_password: str = field(repr=False)


# %% ../../nbs/client/95_DomoAuth.ipynb 13
@dataclass
class DomoFullAuth(_DomoAuth_Optional, _DomoFullAuth_Required, _DomoAuth_Required):
    """use for full authentication token"""

    async def generate_auth_header(self, token: str = None) -> dict:
        token = token or self.token or await self.get_auth_token()

        self.token = token

        self.auth_header = {"x-domo-authentication": token}

        return self.auth_header

    async def get_auth_token(
        self,
        session: Optional[httpx.AsyncClient] = None,
        return_raw: bool = False,
        debug_api: bool = False,
    ) -> str:
        """returns `token` if valid credentials provided else raises Exception and returns None"""

        res = await auth_routes.get_full_auth(
            domo_instance=self.domo_instance,
            domo_username=self.domo_username,
            domo_password=self.domo_password,
            session=session,
            debug_api=debug_api,
            parent_class=self.__class__.__name__,
        )

        if return_raw:
            return res

        self.is_valid_token = True

        token = str(res.response.get("sessionToken"))
        self.token = token
        self.user_id = str(res.response.get("userId"))

        await self.generate_auth_header()

        self.token_name = self.token_name or "full_auth"

        return self.token


# %% ../../nbs/client/95_DomoAuth.ipynb 18
def test_is_full_auth(
    auth, function_name=None, num_stacks_to_drop=1  # pass q for route pass 2 for class
):

    tb = lg.get_traceback(num_stacks_to_drop=num_stacks_to_drop)

    function_name = function_name or tb.function_name

    if auth.__class__.__name__ != "DomoFullAuth":
        raise InvalidAuthTypeError(
            function_name=function_name,
            domo_instance=auth.domo_instance,
            required_auth_type=DomoFullAuth,
        )


# %% ../../nbs/client/95_DomoAuth.ipynb 20
@dataclass
class _DomoTokenAuth_Required:
    """mix requied parameters for DomoFullAuth"""

    domo_access_token: str = field(repr=False)

    async def who_am_i(
        self, debug_api: bool = False, session: httpx.AsyncClient = None
    ):

        auth_header = self.auth_header or self.generate_auth_header()

        res = await auth_routes.who_am_i(
            domo_instance=self.domo_instance,
            auth_header=auth_header,
            parent_class=self.__class__.__name__,
        )

        return res


# %% ../../nbs/client/95_DomoAuth.ipynb 21
@dataclass
class DomoTokenAuth(_DomoAuth_Optional, _DomoTokenAuth_Required, _DomoAuth_Required):
    """
    use for access_token authentication.
    Tokens are generated in domo > admin > access token
    Necessary in cases where direct sign on is not permitted
    """

    def generate_auth_header(self) -> dict:
        """returns auth_header for validating API requests using access_tokens / developer tokens"""

        "is this being executed as part of get_auth_token chain? if yes, suppress not validated error"
        traceback_details = lg.get_traceback(num_stacks_to_drop=0)
        function_name = traceback_details.function_name
        if len(traceback_details.traceback_stack) >= 3:
            function_name = traceback_details.traceback_stack[-3][2]
        if not function_name == "get_auth_token" and not self.token:
            print(
                "warning this token has not been validated by who_am_i, run get_auth_token first"
            )

        self.auth_header = {
            "x-domo-developer-token": self.token or self.domo_access_token
        }
        return self.auth_header

    async def get_auth_token(
        self, session: Optional[httpx.AsyncClient] = None, debug_api: bool = False
    ) -> str:
        """
        updates internal attributes
        having an access_token assumes pre-authenticaiton
        """

        res = await self.who_am_i()

        assert res.is_success

        self.is_valid_token = True

        self.token = self.domo_access_token
        self.user_id = res.response.get("id")

        self.auth_header = self.generate_auth_header()

        if not self.token_name:
            self.token_name = "token_auth"

        return self.token


# %% ../../nbs/client/95_DomoAuth.ipynb 26
@dataclass
class _DomoDeveloperAuth_Required:
    """mix requied parameters for DomoDeveloperAuth"""

    domo_client_id: str
    domo_client_secret: str = field(repr=False)


@dataclass
class _DomoDeveloperAuth_Optional:
    """mix optional parameters for DomoDeveloperAuth"""

    domo_instance: str = None  # because api.domo.com apis don't require domo_instance


# %% ../../nbs/client/95_DomoAuth.ipynb 27
@dataclass
# (init=False)
class DomoDeveloperAuth(
    _DomoDeveloperAuth_Optional, _DomoAuth_Optional, _DomoDeveloperAuth_Required
):
    """use for full authentication token"""

    # def __init__(self, domo_client_id: str, domo_client_secret: str):
    #     self.domo_client_id = domo_client_id
    #     self.domo_client_secret = domo_client_secret
    #     self.domo_instance = ""

    async def generate_auth_header(self) -> dict:
        token = self.token or await self.get_auth_token()

        self.auth_header = {"Authorization": "bearer " + token}
        return self.auth_header

    async def get_auth_token(
        self, session: Optional[httpx.AsyncClient] = None, debug_api: bool = False
    ) -> str:

        res = await auth_routes.get_developer_auth(
            domo_client_id=self.domo_client_id,
            domo_client_secret=self.domo_client_secret,
            session=session,
            debug_api=debug_api,
            parent_class=self.__class__.__name__,
        )
        assert res.is_success

        self.is_valid_token = True

        self.token = str(res.response.get("access_token"))
        self.user_id = res.response.get("userId")
        self.domo_instance = res.response.get("domain")
        self.set_manual_login()

        self.auth_header = await self.generate_auth_header()

        self.token_name = self.token_name or "developer_auth"

        return self.token


# %% ../../nbs/client/95_DomoAuth.ipynb 31
@dataclass
class _DomoJupyter_Optional:
    def __post_init__(self):

        self.jupyter_token = self.jupyter_token or input(
            "jupyter token: # retrieve this by monitoring domo jupyter network traffic.  it is the Authorization header"
        )
        self.service_location = self.service_location or input(
            "service_location:  # retrieve from domo jupyter env"
        )
        self.service_prefix = self.service_prefix or input(
            "service prefix: # retrieve from domo jupyter env"
        )

        self._test_prereq()
        self.set_manual_login()

    def generate_auth_header(self, token: str) -> dict:
        self.auth_header = {
            "x-domo-authentication": token,
            "authorization": f"Token {self.jupyter_token}",
        }

        return self.auth_header


@dataclass
class _DomoJupyter_Required:
    jupyter_token: str
    service_location: str
    service_prefix: str

    def get_jupyter_token_flow(self):
        """stub"""
        print("hello world i am a jupyter_token")

    def _test_prereq(self):
        if not self.jupyter_token:
            raise Exception("DomoJupyterAuth objects must have a jupyter_token")

        if not self.service_location:
            raise Exception("DomoJupyterAuth objects must have a service_location")

        if not self.service_prefix:
            raise Exception("DomoJupyterAuth objects must have a service_prefix")

        if (
            not self.jupyter_token
            or not self.service_location
            or not self.service_prefix
        ):
            raise Exception(
                "DomoJupyterAuth objects must have jupyter_token, service_location and service_prefix"
            )


# %% ../../nbs/client/95_DomoAuth.ipynb 32
@dataclass
class DomoJupyterAuth(_DomoJupyter_Optional, _DomoJupyter_Required):
    """base class"""


# %% ../../nbs/client/95_DomoAuth.ipynb 34
@dataclass
class DomoJupyterFullAuth(_DomoJupyter_Optional, DomoFullAuth, _DomoJupyter_Required):
    @classmethod
    def convert_auth(
        cls, full_auth: DomoFullAuth, jupyter_token, service_location, service_prefix
    ):
        """converts DomoFullAuth to DomoJupyterFullAuth
        i.e. adds DomoJupyter specific auth fields
        eventually can add DomoJupyter specific auth flow for generating auth token
        """
        return cls(
            domo_instance=full_auth.domo_instance,
            domo_username=full_auth.domo_username,
            domo_password=full_auth.domo_password,
            jupyter_token=jupyter_token,
            service_location=service_location,
            service_prefix=service_prefix,
        )


# %% ../../nbs/client/95_DomoAuth.ipynb 38
@dataclass
class DomoJupyterTokenAuth(_DomoJupyter_Optional, DomoTokenAuth, _DomoJupyter_Required):
    @classmethod
    def convert_auth(
        cls, token_auth: DomoTokenAuth, jupyter_token, service_location, service_prefix
    ):
        """converts DomoTokenAuth to DomoJupyterTokenAuth
        i.e. adds DomoJupyter specific auth fields
        eventually can add DomoJupyter specific auth flow for generating auth token
        """
        return cls(
            domo_instance=token_auth.domo_instance,
            domo_access_token=token_auth.domo_access_token,
            jupyter_token=jupyter_token,
            service_location=service_location,
            service_prefix=service_prefix,
        )


# %% ../../nbs/client/95_DomoAuth.ipynb 42
def test_is_jupyter_auth(
    auth: DomoJupyterAuth,
    function_name=None,
    required_auth_type_ls=[DomoJupyterFullAuth, DomoJupyterTokenAuth],
):

    tb = lg.get_traceback()

    if auth.__class__.__name__ not in [
        auth_type.__name__ for auth_type in required_auth_type_ls
    ]:
        raise InvalidAuthTypeError(
            function_name=tb.function_name,
            domo_instance=auth.domo_instance,
            required_auth_type_ls=required_auth_type_ls,
        )
