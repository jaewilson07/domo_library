# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoPage.ipynb.

# %% auto 0
__all__ = ['DomoPage']

# %% ../../nbs/classes/50_DomoPage.ipynb 2
from fastcore.basics import patch_to
from dataclasses import dataclass, field

import asyncio
import httpx

import domolibrary.client.DomoAuth as dmda
import domolibrary.classes.DomoUser as dmdu
import domolibrary.utils.DictDot as util_dd

import domolibrary.routes.page as page_routes


# %% ../../nbs/classes/50_DomoPage.ipynb 3
@dataclass
class DomoPage:
    id: str
    title: str = None
    parent_page_id: str = None
    auth: dmda.DomoAuth = field(default = None , repr = False)
    owners: list = field(default_factory=list)
    cards: list = field(default_factory=list)
    collections: list = field(default_factory=list)
    children: list = field(default_factory=list)

    def display_url(self):
        return f"https://{self.auth.domo_instance}.domo.com/page/{self.id}"

# %% ../../nbs/classes/50_DomoPage.ipynb 4
@patch_to(DomoPage, cls_method=True)
def _from_bootstrap(cls: DomoPage, page_obj, auth: dmda.DomoAuth = None):

    dd = page_obj
    if isinstance(page_obj, dict):
        dd = util_dd.DictDot(page_obj)

    domo_page = cls(id=dd.id, title=dd.title, auth=auth)

    if isinstance(dd.owners, list) and len(dd.owners) > 0:
        domo_page.owners = [
            dmdu.DomoUser._from_bootstrap_json(auth=auth, user_obj=user_dd)
            for user_dd in dd.owners
            if user_dd.type == 'USER'
        ]

        [print(other_dd) for other_dd in dd.owners
         if other_dd.type != 'USER']

    if isinstance(dd.children, list) and len(dd.children) > 0:
        domo_page.children = [
            cls._from_bootstrap(page_obj=child_dd, auth=auth)
            for child_dd in dd.children
            if child_dd.type == "page"
        ]

        [print(other_dd) for other_dd in dd.children
            if other_dd.type != "page"]

    return domo_page


# %% ../../nbs/classes/50_DomoPage.ipynb 7
@patch_to(DomoPage, cls_method=True)
async def _from_content_stacks_v3(cls: DomoPage, page_obj, auth: dmda.DomoAuth = None):
    # import domolibrary.classes.DomoCard as dc

    dd = page_obj
    if isinstance(page_obj, dict):
        dd = util_dd.DictDot(page_obj)

    pg = cls(
        id=dd.id,
        title=dd.title,
        parent_page_id=dd.page.parentPageId,
        owners=dd.page.owners,
        collections=dd.collections,
        auth=auth
    )

    # if dd.cards and len(dd.cards) > 0:
    #     pg.cards = await asyncio.gather(
    #         *[dc.DomoCard.get_from_id(id=card.id, auth=auth) for card in dd.cards])

    return pg


@patch_to(DomoPage, cls_method=True)
async def get_by_id(cls: DomoPage,
                    page_id: str,
                    auth: dmda.DomoAuth,
                    return_raw: bool = False, 
                    debug_api: bool = False):

    res = await page_routes.get_page_by_id(auth=auth, page_id=page_id, debug_api=debug_api)

    if return_raw:
        return res
        
    if not res.status == 200:
        return

    pg = await cls._from_content_stacks_v3(page_obj=res.response, auth=auth)

    return pg


# %% ../../nbs/classes/50_DomoPage.ipynb 10
@patch_to(DomoPage)
async def get_accesslist(self,
                         auth: dmda.DomoAuth = None,
                         is_expand_users: bool = False,
                         return_raw: bool = False,
                         debug_api: bool = False):

    auth = auth or self.auth

    res = await page_routes.get_page_access_list(auth=auth,
                                                is_expand_users=is_expand_users,
                                                page_id=self.id,
                                                debug_api=debug_api
                                                )

    if return_raw:
        return res

    if not res.is_success :
        raise Exception('error getting access list')

    import domolibrary.classes.DomoUser as dmu
    import domolibrary.classes.DomoGroup as dmg
    
    tasks = await asyncio.gather( 
        dmu.DomoUsers.by_id(user_ids=[user.get('id') for user in res.response.get('users')], only_allow_one=False, auth=auth),
        * [ dmg.DomoGroup.get_by_id( group_id = group.get('id'), auth = auth) for group in res.response.get('groups')]
    )
    
    res.response.update({'users': tasks[0], 'groups': tasks[1:]})

    return res.response

