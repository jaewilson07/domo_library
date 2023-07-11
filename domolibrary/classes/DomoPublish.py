# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoPublish.ipynb.

# %% auto 0
__all__ = ['DomoPublication_Subscription', 'DomoPublication_Content', 'DomoPublication_UnexpectedContentType', 'DomoPublication',
           'DomoPublications', 'convert_content_to_dataframe', 'convert_lineage_to_dataframe']

# %% ../../nbs/classes/50_DomoPublish.ipynb 2
from dataclasses import dataclass, field

from typing import Optional
import datetime as dt
import asyncio
import httpx
import uuid
from fastcore.basics import patch_to

# import importlib
# import json
# import uuid
# import time

import domolibrary.utils.DictDot as util_dd
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de
import domolibrary.routes.publish as publish_routes

# import Library.DomoClasses.DomoDataset as dmda
import domolibrary.classes.DomoLineage as dmdl

# %% ../../nbs/classes/50_DomoPublish.ipynb 4
@dataclass
class DomoPublication_Subscription:
    subscription_id: str
    publication_id: str
    domain: str
    created_dt: Optional[dt.datetime] = None

    @classmethod
    def _from_json(cls, json):

        dd = json
        if not isinstance(dd, util_dd.DictDot):
            dd = util_dd.DictDot(json)

        return cls(
            subscription_id=dd.id,
            publication_id=dd.publicationId,
            domain=dd.domain,
            created_dt=dt.datetime.fromtimestamp(dd.created / 1000)
            if dd.created
            else None,
        )




# %% ../../nbs/classes/50_DomoPublish.ipynb 6
@dataclass
class DomoPublication_Content:
    content_id: str
    entity_type: str
    entity_id: str
    entity_domain: str
    is_v2: bool
    is_direct_content: bool

    @classmethod
    def _from_json(cls, obj: dict):

        dd = obj
        if not isinstance(dd, util_dd.DictDot):
            dd = util_dd.DictDot(obj)

        dmpc = cls(
            content_id=dd.id,
            entity_type=dd.content.type,
            entity_id=dd.content.domoObjectId,
            entity_domain=dd.content.domain,
            is_v2=dd.isV2,
            is_direct_content=dd.useDirectContent,
        )

        return dmpc

    def to_api_json(self):
        temp_dict = {
            "domain": self.entity_domain,
            "domoObjectId": self.entity_id,
            "customerId": self.entity_domain,
            "type": self.entity_type,
        }
        return temp_dict


# %% ../../nbs/classes/50_DomoPublish.ipynb 8
class DomoPublication_UnexpectedContentType(Exception):
    def __init__(self, publication_id, content_type, domo_instance):
        super().__init__(f"DomoPublication_Instantiation: Unexpected content type {content_type} in publication {publication_id} in {domo_instance}")

# %% ../../nbs/classes/50_DomoPublish.ipynb 9
@dataclass
class DomoPublication:
    id: str
    name: str
    description: str
    is_v2: bool
    created_dt: dt.datetime

    auth: dmda.DomoAuth = field(default=None, repr=False)

    subscription_authorizations: [DomoPublication_Subscription] = field(
        default_factory=list
    )
    content: [DomoPublication_Content] = field(default_factory=list)

    content_page_id_ls: [str] = field(default_factory=list)
    content_dataset_id_ls: [str] = field(default_factory=list)

    lineage: dmdl.DomoLineage = None

    def __post_init__(self):
        self.lineage = dmdl.DomoLineage(parent=self)

    @classmethod
    def _from_json(cls, obj, auth: dmda.DomoAuth = None):

        dd = util_dd.DictDot(obj)

        domo_pub = cls(
            id=dd.id,
            name=dd.name,
            description=dd.description,
            created_dt=dt.datetime.fromtimestamp(dd.created / 1000)
            if dd.created
            else None,
            is_v2=dd.isV2,
            auth=auth,
        )

        if dd.subscriptionAuthorizations and len(dd.subscriptionAuthorizations) > 0:
            domo_pub.subscription_authorizations = [
                DomoPublication_Subscription._from_json(sub)
                for sub in dd.subscriptionAuthorizations
            ]

        # publish only supports sharing pages and datasets
        if dd.children and len(dd.children) > 0:
            for child in dd.children:

                dmpc = DomoPublication_Content._from_json(child)
                domo_pub.content.append(dmpc)

                if dmpc.entity_type == "PAGE":
                    domo_pub.content_page_id_ls.append(dmpc.entity_id)

                elif dmpc.entity_type == "DATASET":
                    domo_pub.content_dataset_id_ls.append(dmpc.entity_id)

                else:
                    raise DomoPublication_UnexpectedContentType(
                        publication_id=domo_pub.id, 
                        content_type=dmpc.entity_type, 
                        domo_instance=auth.domo_instance)

        return domo_pub


# %% ../../nbs/classes/50_DomoPublish.ipynb 10
@patch_to(DomoPublication, cls_method=True)
async def get_from_id(cls, publication_id=None, auth: dmda.DomoAuth = None, timeout = 10):

    auth = auth or cls.auth

    publication_id = publication_id or cls.publication_id

    res = await publish_routes.get_publication_by_id(
        auth=auth, publication_id=publication_id
        , timeout = 10
    )

    if not res.is_success:
        return None

    return cls._from_json(obj=res.response, auth=auth)

# %% ../../nbs/classes/50_DomoPublish.ipynb 15
@dataclass
class DomoPublications:

    @classmethod
    async def get_subscription_summaries(cls, 
                                         auth: dmda.DomoAuth,
                                         session: httpx.AsyncClient = None,
                                         return_raw: bool = False,
                                         debug_api: bool = False):
        """get instances subscription summaries"""

        res = await publish_routes.get_subscription_summaries(auth=auth,
                                                              session=session,
                                                              debug_api=debug_api
                                                              )

        if return_raw:
            return res

        if not res.is_success:
            return res

        sub_ls = res.response

        return [ sub for sub in sub_ls]
        
        


# %% ../../nbs/classes/50_DomoPublish.ipynb 18
@patch_to(DomoPublications, cls_method=True)
async def search_publications(cls: DomoPublications,
                              auth = dmda.DomoAuth,
                              search_term: str = None,
                              session: httpx.AsyncClient = None,
                              debug_api: bool = False,
                              return_raw: bool = False):

    res = await publish_routes.search_publications(auth=auth)

    if return_raw:
        return res

    if not res.is_success or (res.is_success and len(res.response) == 0):
        return None

    return [DomoPublication._from_json(sub_obj)for sub_obj in res.response]


# %% ../../nbs/classes/50_DomoPublish.ipynb 20
def convert_content_to_dataframe(self, return_raw: bool = False):

    output_ls = [{'plubication_id': self.id,
                      'publication_name': self.name,
                      'is_v2': self.is_v2,
                      'publish_created_dt': self.created_dt,
                      'entity_type': row.type,
                      'entity_id': row.id
                      } for row in self.content_entity_ls]

    if return_raw:
        return output_ls

    return pd.DataFrame(output_ls)

def convert_lineage_to_dataframe(self, return_raw: bool = False):
    import pandas as pd
    import re

    flat_lineage_ls = self.lineage._flatten_lineage()

    output_ls = [{'plubication_id': self.id,
                      'publication_name': self.name,
                      'is_v2': self.is_v2,
                      'publish_created_dt': self.created_dt,
                      'entity_type': row.get('entity_type'),
                      'entity_id': row.get('entity_id')
                      } for row in flat_lineage_ls]

    if return_raw:
        return output_ls

    return pd.DataFrame(output_ls)


# %% ../../nbs/classes/50_DomoPublish.ipynb 21
@patch_to(DomoPublication, cls_method=True)
async def create_publication(cls,
                                 name: str,
                                 content_ls: [DomoPublication_Content],
                                 subscription_ls: [DomoPublication_Subscription],
                                 unique_id: str = None,
                                 description: str = None,
                                 auth: dmda.DomoAuth = None,
                                 debug_api: bool = False):

    if not isinstance(subscription_ls, list):
        subscription_ls = [subscription_ls]

    auth = auth or cls.auth
    domain_ls = []
    content_json_ls = []
    for sub in subscription_ls:
        domain_ls.append(sub.domain)
    for content_item in content_ls:
        content_json_ls.append(content_item.to_api_json())

    if not unique_id:
        unique_id = str(uuid.uuid4())
    if not description:
        description = ''

    body = publish_routes.generate_publish_body(url=f'{auth.domo_instance}.domo.com',
                                                    sub_domain_ls=domain_ls,
                                                    content_ls=content_json_ls,
                                                    name=name,
                                                    unique_id=unique_id,
                                                    description=description,
                                                    is_new=True)

    res = await publish_routes.create_publish_job(auth=auth, body=body)
    if debug_api:
        print('Create the new Publish job')
    if res.status != 200:
        print(res)
        await asyncio.sleep(2)
        res = await publish_routes.get_publication_by_id(auth=auth, publication_id=unique_id)
        if res.status != 200:
            return None
        else:
            return cls._from_json(obj=res.response, auth=auth)

    return cls._from_json(obj=res.response, auth=auth)


# %% ../../nbs/classes/50_DomoPublish.ipynb 23
@patch_to(DomoPublication, cls_method=True)
async def update_publication(cls,
                                 name: str,
                                 content_ls: [DomoPublication_Content],
                                 subscription_ls: [DomoPublication_Subscription],
                                 publication_id: str,
                                 description: str = None,
                                 auth: dmda.DomoAuth = None,
                                 debug_api: bool = False):

    if not isinstance(subscription_ls, list):
        subscription_ls = [subscription_ls]

    auth = auth or cls.auth
    domain_ls = []
    content_json_ls = []
    for sub in subscription_ls:
        domain_ls.append(sub.domain)
    for content_item in content_ls:
        content_json_ls.append(content_item.to_api_json())

    if not description:
        description = ''
    body = publish_routes.generate_publish_body(url=f'{auth.domo_instance}.domo.com',
                                                    sub_domain_ls=domain_ls,
                                                    content_ls=content_json_ls,
                                                    name=name,
                                                    unique_id=publication_id,
                                                    description=description,
                                                    is_new=False)

    res = await publish_routes.udpate_publish_job(auth= auth,
                                                      publication_id=publication_id,
                                                      body=body)
    if debug_api:
        print('Update Publish job by id')
    if res.status != 200:
        print(res)
        await asyncio.sleep(2)
        res = await publish_routes.get_publication_by_id(auth=auth, publication_id=publication_id)
        if res.status != 200:
            return None
        else:
            return cls._from_json(obj=res.response, auth=auth)

    return cls._from_json(obj=res.response, auth=auth)




# %% ../../nbs/classes/50_DomoPublish.ipynb 25
@patch_to(DomoPublication, cls_method=True)
async def get_subscription_invites_list(cls, auth: dmda.DomoAuth,
                                            debug_api: bool = False):

    res = await publish_routes.get_subscription_invititations(auth=auth,
                                                                debug_api=debug_api)
    if debug_api:
        print('Getting Publish subscription invites')

    if res.status == 200:
        return res.response
    else:
        return None

#| export
@patch_to(DomoPublication, cls_method=True)
async def accept_invite_by_id(cls,
                                  auth: dmda.DomoAuth,
                                  subscription_id: str,
                                  debug_api: bool = False):

    res = await publish_routes.accept_invite_by_id(auth=auth,
                                                       subscription_id=subscription_id,
                                                      debug_api=debug_api)
    if debug_api:
        print(f'Accept invite by id {subscription_id}')

    if res.status == 200:
        return res.response
    else:
        return None
