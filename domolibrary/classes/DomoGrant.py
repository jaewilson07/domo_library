# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoGrant.ipynb.

# %% auto 0
__all__ = ['DomoGrant', 'DomoGrants']

# %% ../../nbs/classes/50_DomoGrant.ipynb 2
from dataclasses import dataclass, field
from fastcore.basics import patch_to
import httpx

import domolibrary.client.DomoAuth as dmda
import domolibrary.utils.DictDot as util_dd
import domolibrary.routes.grant as grant_routes


# %% ../../nbs/classes/50_DomoGrant.ipynb 3
@dataclass
class DomoGrant:
    id: str
    display_group: str = None
    title: str = None
    depends_on_ls: list[str] = None
    description: str = None
    role_membership_ls: list[str] = field(default=None)

    def __post_init__(self):
        self.id = str(self.id)

    def __eq__(self, other):
        if not isinstance(other, DomoGrant):
            return False

        return self.id == other.id


    @classmethod
    def _from_json(cls, obj):

        dd = obj
        if not isinstance(dd, util_dd.DictDot):
            dd = util_dd.DictDot(obj)

        return cls(id=dd.authority,
                   display_group=dd.authorityUIGroup,
                   depends_on_ls=dd.dependsOnAuthorities,
                   title=dd.title,
                   description=dd.description,
                   role_membership_ls=[str(role) for role in dd.roleIds])


# %% ../../nbs/classes/50_DomoGrant.ipynb 4
@dataclass
class DomoGrants:
    pass



# %% ../../nbs/classes/50_DomoGrant.ipynb 5
@patch_to(DomoGrants, cls_method=True)
async def get_grants(cls: DomoGrants,
                     auth: dmda.DomoAuth,
                     session: httpx.AsyncClient = None, debug_api: bool = False, return_raw: bool = False,
                     ):
    res = await grant_routes.get_grants(auth=auth, debug_api = debug_api, session = session)

    if return_raw or not res.is_success: 
        return res
    
    return [DomoGrant._from_json(row) for index, row in enumerate(res.response)]

