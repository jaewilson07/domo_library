# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/client/99_ResponseGetData.ipynb.

# %% auto 0
__all__ = ['API_Response', 'ResponseGetData']

# %% ../../nbs/client/99_ResponseGetData.ipynb 2
# pylint: disable=no-member
from dataclasses import dataclass, field
from typing import Optional

import asyncio
import requests
import aiohttp

from fastcore.utils import patch_to, patch

# %% ../../nbs/client/99_ResponseGetData.ipynb 4
API_Response = any


@dataclass
class ResponseGetData:
    """preferred response class for all API Requests"""

    status: int
    response: API_Response
    is_success: bool
    auth: dict = field(repr = False, default=None)

    def set_response(self, response):
        self.response = response

# %% ../../nbs/client/99_ResponseGetData.ipynb 8
@patch_to(ResponseGetData, cls_method=True)
def _from_requests_response(
    cls, res: requests.Response  # requests response object
) -> ResponseGetData:
    """returns ResponseGetData"""

    # JSON responses
    if res.ok and "application/json" in res.headers.get("Content-Type", {}):
        return cls(status=res.status_code, response=res.json(), is_success=True)

    # default text responses
    elif res.ok:
        return cls(status=res.status_code, response=res.text, is_success=True)

    # errors
    return cls(status=res.status_code, response=res.reason, is_success=False)

# %% ../../nbs/client/99_ResponseGetData.ipynb 12
@patch(cls_method=True)
async def _from_aiohttp_response(
    cls: ResponseGetData, 
    res: aiohttp.ClientResponse,  # requests response object
    auth : Optional[any] = None
) -> ResponseGetData:

    """async method returns ResponseGetData"""

    if res.ok and "application/json" in res.headers.get("Content-Type", {}):
        try:
            return cls(status=res.status, response=await res.json(), is_success=True, auth = auth)

        # handle if unable to decode json()
        except asyncio.TimeoutError as e:
            print(e)
            print("response included json, but defaulted to backup decode method")

            return cls(status=res.status, response=await res.read(), is_success=True, auth = auth)

        # response is text
    elif res.ok:
        return cls(status=res.status, response=await res.text(), is_success=True, auth = auth)

    # response is error
    else:
        return cls(status=res.status, response=res.reason, is_success=False, auth = auth)

# %% ../../nbs/client/99_ResponseGetData.ipynb 16
@patch(cls_method=True)
async def _from_looper(cls: ResponseGetData,
                       res: ResponseGetData,  # requests response object
                       array: list
                       ) -> ResponseGetData:

    """async method returns ResponseGetData"""

    if res.is_success:
        res.response = array
        return res

    # response is error
    else:
        return res

