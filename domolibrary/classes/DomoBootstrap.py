# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoBootstrap.ipynb.

# %% auto 0
__all__ = ['DomoBootstrap_Feature', 'DomoBootstrap']

# %% ../../nbs/classes/50_DomoBootstrap.ipynb 2
from dataclasses import dataclass, field
from nbdev.showdoc import patch_to
import httpx

import domolibrary.classes.DomoPage as dmpg

import domolibrary.utils.DictDot as util_dd
import domolibrary.client.DomoAuth as dmda
import domolibrary.routes.bootstrap as bootstrap_routes
import domolibrary.utils.chunk_execution as ce

# %% ../../nbs/classes/50_DomoBootstrap.ipynb 3
from ..routes.bootstrap import InvalidAuthTypeError

# %% ../../nbs/classes/50_DomoBootstrap.ipynb 4
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

# %% ../../nbs/classes/50_DomoBootstrap.ipynb 5
@dataclass
class DomoBootstrap:
    auth: dmda.DomoAuth = field(repr=False)
    bootstrap: dict = field(default=None)
    customer_id: str = None
    page_ls: list[dmpg.DomoPage] = field(default=None)
    feature_ls: list[DomoBootstrap_Feature] = field(default=None)

# %% ../../nbs/classes/50_DomoBootstrap.ipynb 6
@patch_to(DomoBootstrap)
async def get_all(
    self: DomoBootstrap,
    auth: dmda.DomoFullAuth = None,
    debug_api: bool = False,
    return_raw: bool = False,
    debug_num_stacks_to_drop=2,
):
    auth = auth or self.auth

    res = await bootstrap_routes.get_bootstrap(
        auth=auth,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=self.__class__.__name__,
    )

    self.bootstrap = res.response

    if return_raw:
        return res

    return res.response

# %% ../../nbs/classes/50_DomoBootstrap.ipynb 9
@patch_to(DomoBootstrap)
async def get_customer_id(
    self: DomoBootstrap,
    auth: dmda.DomoFullAuth = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop=3,
    return_raw: bool = False
):
    res = await bootstrap_routes.get_bootstrap_customerid(
        auth=auth or self.auth,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        return_raw = return_raw,
        parent_class = self.__class__.__name__
    )

    if return_raw:
        return res

    self.customer_id = res.response

    return self.customer_id

# %% ../../nbs/classes/50_DomoBootstrap.ipynb 12
@patch_to(DomoBootstrap)
async def get_pages(
    self: DomoBootstrap,
    auth: dmda.DomoFullAuth = None,
    return_raw: bool = False,
    debug_api: bool = False,
    debug_num_stacks_to_drop=2,
) -> list[dmpg.DomoPage]:
    auth = auth or self.auth

    res = await bootstrap_routes.get_bootstrap_pages(
        auth=auth,
        debug_api=debug_api,
        parent_class=self.__class__.__name__,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        return None

    self.page_ls = await ce.gather_with_concurrency(
        n=60,
        *[
            dmpg.DomoPage._from_bootstrap(page_obj, auth=auth)
            for page_obj in res.response
        ]
    )

    return self.page_ls

# %% ../../nbs/classes/50_DomoBootstrap.ipynb 15
@patch_to(DomoBootstrap)
async def get_features(
    self: DomoBootstrap,
    auth: dmda.DomoAuth = None,
    debug_api: bool = False,
    return_raw: bool = False,
    debug_num_stacks_to_drop=2,
    session: httpx.AsyncClient = None,
):
    auth = auth or self.auth

    res = await bootstrap_routes.get_bootstrap_features(
        auth=auth,
        session=session,
        debug_api=debug_api,
        return_raw=return_raw,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=self.__class__.__name__,
    )

    if return_raw:
        return res

    feature_list = [
        DomoBootstrap_Feature._from_json_bootstrap(json_obj)
        for json_obj in res.response
    ]

    return feature_list

# %% ../../nbs/classes/50_DomoBootstrap.ipynb 18
@patch_to(DomoBootstrap)
async def is_feature_accountsv2_enabled(
    self :DomoBootstrap,
    auth: dmda.DomoAuth = None,
    debug_api: bool = False,
    return_raw: bool = False,
    debug_num_stacks_to_drop=3,
):
    res = await bootstrap_routes.get_bootstrap_features_is_accountsv2_enabled(
        auth=auth or self.auth,
        return_raw=return_raw,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=self.__class__.__name__,
    )

    if return_raw:
        return res

    return res.response
