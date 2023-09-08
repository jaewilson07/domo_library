# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoBootstrap.ipynb.

# %% auto 0
__all__ = ['DomoBootstrap_Feature', 'DomoBootstrap', 'Bootstrap_RetrievalError']

# %% ../../nbs/classes/50_DomoBootstrap.ipynb 2
from dataclasses import dataclass, field
from fastcore.basics import patch_to
import httpx
import asyncio

import domolibrary.classes.DomoPage as dmpg

import domolibrary.utils.DictDot as util_dd
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de
import domolibrary.routes.bootstrap as bootstrap_routes


# %% ../../nbs/classes/50_DomoBootstrap.ipynb 3
@dataclass
class DomoBootstrap_Feature:
    id: int
    name: str
    label: str
    type: str
    purchased: bool
    enabled: bool

    @classmethod
    def _from_json_bootstrap(cls, json_obj: dict):
        dd = util_dd.DictDot(json_obj)

        bsf = cls(
            id=dd.id,
            name=dd.name,
            label=dd.label,
            type=dd.type,
            purchased=dd.purchased,
            enabled=dd.enabled,
        )
        return bsf


# %% ../../nbs/classes/50_DomoBootstrap.ipynb 4
@dataclass
class DomoBootstrap:
    auth: dmda.DomoAuth = field(repr=False)
    bootstrap: dict = field(default=None)
    customer_id: str = None
    page_ls: list[dmpg.DomoPage] = field(default=None)
    feature_ls: list[DomoBootstrap_Feature] = field(default=None)

# %% ../../nbs/classes/50_DomoBootstrap.ipynb 5
class Bootstrap_RetrievalError(de.DomoError):
    def __init__(self, status, response, domo_instance):
        super().__init__(status=status, response=response, domo_instance=domo_instance)


@patch_to(DomoBootstrap)
async def get_all(
    self: DomoBootstrap, auth: dmda.DomoAuth = None, debug_api: bool = False
):
    auth = auth or self.auth

    res = await bootstrap_routes.get_bootstrap(auth=auth, debug_api=debug_api)

    if not res.is_success:
        raise Bootstrap_RetrievalError(
            status=res.status, response=res.response, domo_instance=auth.domo_instance
        )

    self.bootstrap = res.response

    return res.response


# %% ../../nbs/classes/50_DomoBootstrap.ipynb 8
@patch_to(
    DomoBootstrap,
)
async def get_customer_id(self: DomoBootstrap, auth: dmda.DomoFullAuth = None):
    await self.get_all(auth=auth or self.auth)

    self.customer_id = self.bootstrap["currentUser"]["USER_GROUP"]
    return self.customer_id

# %% ../../nbs/classes/50_DomoBootstrap.ipynb 11
@patch_to(DomoBootstrap)
async def get_pages(
    self: DomoBootstrap,
    auth: dmda.DomoFullAuth = None,
    return_raw: bool = False,
    debug_api: bool = False,
) -> list[dmpg.DomoPage]:
    auth = auth or self.auth

    res = await bootstrap_routes.get_bootstrap_pages(auth=auth, debug_api=debug_api)

    if return_raw:
        return res.response

    if not res.is_success:
        return None

    page_ls = res.response

    self.page_ls = await asyncio.gather(
        *[dmpg.DomoPage._from_bootstrap(page_obj, auth=auth) for page_obj in page_ls]
    )

    return self.page_ls


# %% ../../nbs/classes/50_DomoBootstrap.ipynb 14
@patch_to(DomoBootstrap)
async def get_features(
    self: DomoBootstrap,
    auth: dmda.DomoAuth = None,
    debug_api: bool = False,
    return_raw: bool = False,
    session: httpx.AsyncClient = None,
):
    auth = auth or self.auth

    res = await bootstrap_routes.get_bootstrap_features(
        auth=auth, session=session, debug_api=debug_api, return_raw=return_raw
    )

    if return_raw:
        return res

    feature_list = [
        DomoBootstrap_Feature._from_json_bootstrap(json_obj)
        for json_obj in res.response
    ]

    return feature_list


# %% ../../nbs/classes/50_DomoBootstrap.ipynb 16
@patch_to(DomoBootstrap)
async def is_group_ownership_beta(self, return_raw: bool = False):
    domo_feature_ls = await self.get_features(return_raw=return_raw)

    if return_raw:
        return domo_feature_ls

    match_accounts_v2 = next(
        (
            domo_feature
            for domo_feature in domo_feature_ls
            if domo_feature.name == "accounts-v2"
        ),
        None,
    )

    return True if match_accounts_v2 else False

