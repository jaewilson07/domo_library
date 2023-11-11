# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoCard.ipynb.

# %% auto 0
__all__ = ['DomoCard']

# %% ../../nbs/classes/50_DomoCard.ipynb 2
from dataclasses import dataclass, field

import asyncio
import httpx
from fastcore.basics import patch_to

import domolibrary.utils.DictDot as util_dd
import domolibrary.utils.chunk_execution as ce

import domolibrary.routes.card as card_routes

import domolibrary.client.DomoAuth as dmda

# %% ../../nbs/classes/50_DomoCard.ipynb 3
@dataclass
class DomoCard:
    id: str
    auth: dmda.DomoAuth = field(repr=False)
    title: str = None
    description: str = None
    type: str = None
    urn: str = None
    chart_type: str = None
    dataset_id: str = None

    certification: field(default_factory=dict) = None
    owners: field(default_factory=list) = None

    def __post_init__(self):
        # self.Definition = CardDefinition(self)
        pass

    def display_url(self) -> str:
        return f"https://{self.auth.domo_instance}.domo.com/kpis/details/{self.id}"

    @classmethod
    async def _from_json(cls, card_obj, auth: dmda.DomoAuth):
        import domolibrary.classes.DomoUser as dmu
        import domolibrary.classes.DomoGroup as dmg

        dd = card_obj
        if isinstance(card_obj, dict):
            dd = util_dd.DictDot(card_obj)

        card = cls(
            auth=auth,
            id=dd.id,
            title=dd.title,
            description=dd.description,
            type=dd.type,
            urn=dd.urn,
            certification=dd.certification,
            chart_type=dd.metadata and dd.metadata.chartType,
            dataset_id=dd.datasources[0].dataSourceId if dd.datasources else None,
        )

        tasks = []
        for user in dd.owners:
            if user.type == "USER":
                tasks.append(dmu.DomoUser.get_by_id(user_id=user.id, auth=auth))
            if user.type == "GROUP":
                tasks.append(dmg.DomoGroup.get_by_id(group_id=user.id, auth=auth))

        card.owners = await ce.gather_with_concurrency(n=60, *tasks)

        return card

# %% ../../nbs/classes/50_DomoCard.ipynb 4
@patch_to(DomoCard, cls_method=True)
async def get_by_id(
    cls: DomoCard,
    card_id: str,
    auth: dmda.DomoAuth,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):
    res = await card_routes.get_card_metadata(
        auth=auth, card_id=card_id, debug_api=debug_api, session=session
    )

    if not res.is_success:
        raise Exception("unable to retrieve card {card_id}")

    domo_card = await cls._from_json(res.response, auth)

    return domo_card

# %% ../../nbs/classes/50_DomoCard.ipynb 6
@patch_to(DomoCard)
async def share(
    self: DomoCard,
    auth: dmda.DomoAuth = None,
    domo_users: list = None,  # DomoUsers to share card with,
    domo_groups: list = None,  # DomoGroups to share card with
    message: str = None,  # message for automated email
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):
    import domolibrary.routes.datacenter as datacenter_routes

    if domo_groups:
        domo_groups = domo_groups if isinstance(domo_groups, list) else [domo_groups]
    if domo_users:
        domo_users = domo_users if isinstance(domo_users, list) else [domo_users]

    res = await datacenter_routes.share_resource(
        auth=auth or self.auth,
        resource_ids=[self.id],
        resource_type=datacenter_routes.ShareResource_Enum.CARD,
        group_ids=[group.id for group in domo_groups] if domo_groups else None,
        user_ids=[user.id for user in domo_users] if domo_users else None,
        message=message,
        debug_api=debug_api,
        session=session,
    )

    return res
