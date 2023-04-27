# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoCard.ipynb.

# %% auto 0
__all__ = ['DomoCard']

# %% ../../nbs/classes/50_DomoCard.ipynb 2
from dataclasses import dataclass, field

import asyncio
from fastcore.basics import patch_to

import domolibrary.routes.card as card_routes

import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de
import domolibrary.utils.DictDot as util_dd

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
        return f'https://{self.domo_instance}.domo.com/kpis/details/{self.id}'

    @classmethod
    async def _from_json(cls,
                  card_obj,
                   auth: dmda.DomoAuth):

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
            chart_type=dd.metadata.chartType,
            dataset_id = dd.datasources[0].dataSourceId if dd.datasources else None
        )

        tasks = []
        for user in dd.owners:
            if user.type =='USER':
                tasks.append(dmu.DomoUser.get_by_id(user_id=user.id, auth=auth))
            if user.type == 'GROUP':
                tasks.append(dmg.DomoGroup.get_by_id(group_id=group.get('id'), auth=auth))

        card.owners = await asyncio.gather( *tasks)

        return card

