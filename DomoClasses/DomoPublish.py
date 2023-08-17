from dataclasses import dataclass, field
import datetime as dt
import asyncio
import importlib
import json
import uuid
import time
from Library.utils.DictDot import DictDot

from Library.DomoClasses.routes import publish_routes

import Library.DomoClasses.DomoDataset as dmda
import Library.DomoClasses.DomoLineage as dmdl

importlib.reload(dmdl)

# class InvalidUrl


@dataclass
class DomoPublication_Subscription:
    subscription_id: str
    domain: str
    created_dt: dt.datetime

@dataclass
class DomoPublication_Content:
    content_id: str
    entity_type: str
    entity_id: str
    content_domain: str
    
    def to_json (self):
        temp_dict = {'domain': self.content_domain,
                 'domoObjectId': self.entity_id,
                 'customerId': self.content_domain,
                 'type': self.entity_type}
        return temp_dict


@dataclass
class DomoPublication:
    id: str
    name: str
    description: str
    is_v2: bool
    created_dt: dt.datetime
    full_auth: dmda.DomoFullAuth = field(default=None, repr=False)

    subscription_authorizations: [
        DomoPublication_Subscription] = field(default_factory=list)
    content_entity_ls: [DomoPublication_Content] = field(default_factory=list)

    content_page_id_ls: [str] = None
    content_dataset_id_ls: [str] = None

    lineage: dmdl.DomoLineage = None

    def __post_init__(self):
        self.lineage = dmdl.DomoLineage(id=self.id,
                                        parent=self)

    @classmethod
    def _from_json(cls, obj, full_auth: dmda.DomoFullAuth = None):
        dd = DictDot(obj)

        domo_pub = cls(
            id=dd.id,
            name=dd.name,
            description=dd.description,
            created_dt=dt.datetime.fromtimestamp(
                dd.created/1000) if dd.created else None,
            is_v2=dd.isV2,
            full_auth=full_auth
        )

        if dd.subscription_authorizations and len(dd.subscription_authorizations) > 0:
            domo_pub.subscription_authorizations = [DomoPublication_Subscription(subscription_id=sub.id,
                                                                                 domain=sub.domain,
                                                                                 created_dt=dt.datetime.fromtimestamp(
                                                                                     sub.created/1000)
                                                                                 if sub.created else None
                                                                                 )
                                                    for sub in dd.subscription_authorizations]

        # publish only supports sharing pages and datasets
        if dd.children and len(dd.children) > 0:
            for child in dd.children:
                dmpc = DomoPublication_Content(
                    content_id=child.id,
                    entity_type=child.content.type,
                    entity_id=child.content.domoObjectId,
                    content_domain=child.content.domain)

                if not domo_pub.content_entity_ls:
                    domo_pub.content_entity_ls = []

                domo_pub.content_entity_ls.append(dmpc)

                if dmpc.entity_type == 'PAGE':
                    if not domo_pub.content_page_id_ls:
                        domo_pub.content_page_id_ls = []
                    domo_pub.content_page_id_ls.append(dmpc.entity_id)

                if dmpc.entity_type == 'DATASET':
                    if not domo_pub.content_dataset_id_ls:
                        domo_pub.content_dataset_id_ls = []
                    domo_pub.content_dataset_id_ls.append(dmpc.entity_id)

        return domo_pub

    @classmethod
    async def get_from_id(cls, publication_id=None, full_auth: dmda.DomoFullAuth = None):

        full_auth = full_auth or cls.full_auth

        publication_id = publication_id or cls.publication_id

        res = await publish_routes.get_publication_by_id(full_auth=full_auth, publication_id=publication_id)

        if res.status != 200:
            print(res)
            return None

        return cls._from_json(obj=res.response, full_auth=full_auth)

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
    
    @classmethod
    async def create_publication(cls, 
                                 name : str, 
                                 content_ls : [DomoPublication_Content], 
                                 subscription_ls : [DomoPublication_Subscription],
                                 unique_id : str = None,
                                 description: str = None,
                                 full_auth: dmda.DomoFullAuth = None,
                                 debug: bool = False):
        
        if not isinstance(subscription_ls, list) :
            subscription_ls = [subscription_ls]

        full_auth = full_auth or cls.full_auth
        domain_ls =[]
        content_json_ls =[]
        for sub in subscription_ls:
            domain_ls.append(sub.domain)
        for content_item in content_ls:
            content_json_ls.append(content_item.to_json())
        
        if not unique_id:
            unique_id = str(uuid.uuid4())
        if not description:
            description =''
          
        body = publish_routes.generate_publish_body(url = f'{full_auth.domo_instance}.domo.com',
                                                    sub_domain_ls= domain_ls,
                                                    content_ls = content_json_ls,
                                                    name = name,
                                                    unique_id=unique_id,
                                                    description= description,
                                                    is_new  = True)
        
        res = await publish_routes.create_publish_job(full_auth = full_auth, body=body)
        if debug:
            print('Create the new Publish job')
        if res.status != 200:
            print(res)
            await asyncio.sleep(2) 
            res = await publish_routes.get_publication_by_id(full_auth=full_auth, publication_id=unique_id)
            if res.status != 200:
                return None
            else:
                return cls._from_json(obj=res.response, full_auth=full_auth)

        return cls._from_json(obj=res.response, full_auth=full_auth)

    
    @classmethod
    async def update_publication(cls, 
                                 name : str, 
                                 content_ls : [DomoPublication_Content], 
                                 subscription_ls : [DomoPublication_Subscription],
                                 publication_id : str,
                                 description: str = None, 
                                 full_auth: dmda.DomoFullAuth = None,
                                 debug: bool = False):
        
        if not isinstance(subscription_ls, list) :
            subscription_ls = [subscription_ls]

        full_auth = full_auth or cls.full_auth
        domain_ls =[]
        content_json_ls =[]
        for sub in subscription_ls:
            domain_ls.append(sub.domain)
        for content_item in content_ls:
            content_json_ls.append(content_item.to_json())

        if not description:
            description =''
        body = publish_routes.generate_publish_body(url = f'{full_auth.domo_instance}.domo.com',
                                                    sub_domain_ls= domain_ls,
                                                    content_ls = content_json_ls,
                                                    name = name,
                                                    unique_id=publication_id,
                                                    description= description,
                                                    is_new  = False)
        
        res = await publish_routes.udpate_publish_job(full_auth = full_auth, 
                                                      publication_id = publication_id,
                                                      body = body)
        if debug:
            print('Update Publish job by id')
        if res.status != 200:
            print(res)
            await asyncio.sleep(2) 
            res = await publish_routes.get_publication_by_id(full_auth=full_auth, publication_id=publication_id)
            if res.status != 200:
                return None
            else:
                return cls._from_json(obj=res.response, full_auth=full_auth)

        return cls._from_json(obj=res.response, full_auth=full_auth)
    
    @classmethod
    async def get_subscription_invites_list(cls, full_auth: dmda.DomoFullAuth,
                                            debug: bool = False):
        
        res = await publish_routes.get_subscription_invites_list(full_auth=full_auth,
                                                       debug=debug)
        if debug:
            print('Getting Publish subscription invites')

        if res.status == 200:
            return res.response
    
    @classmethod
    async def accept_invite_by_id(cls,
                                    full_auth: dmda.DomoFullAuth, 
                                    subscription_id : str,
                                    debug: bool = False):
        
        res = await publish_routes.accept_invite_by_id(full_auth=full_auth,
                                                        subscription_id=subscription_id,
                                                       debug=debug)
        if debug:
            print(f'Accept invite by id {subscription_id}')

        if res.status == 200:
            return res.response
    