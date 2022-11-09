from dataclasses import dataclass, field
import datetime as dt

import importlib

from Library.utils.DictDot import DictDot

from Library.DomoClasses.routes import publish_routes

import Library.DomoClasses.DomoDataset as dmda
import Library.DomoClasses.DomoLineage as dmdl

importlib.reload(dmdl)

# class InvalidUrl

@dataclass
class DomoPublication_Subscription:
    subscription_id :str
    domain : str
    created_dt : dt.datetime
    
@dataclass
class DomoPublication_Content:
    content_id: str
    entity_type: str
    entity_id :str
    content_domain : str
    
@dataclass
class DomoPublication:
    id: str
    name: str
    description:str
    is_v2 : bool
    created_dt : dt.datetime
    full_auth: dmda.DomoFullAuth = field(default = None, repr = False)
    
    subscription_authorizations : [DomoPublication_Subscription] = field(default_factory = list)
    content_entity_ls : [DomoPublication_Content] = field(default_factory = list)
    
    content_page_id_ls : [str] = None
    content_dataset_id_ls : [str] = None
    
    lineage : dmdl.DomoLineage = None
    
    def __post_init__(self):
        self.lineage = dmdl.DomoLineage(id = self.id,
                                        parent = self)
    
    @classmethod
    def _from_json(cls, obj, full_auth : dmda.DomoFullAuth = None):
        dd = DictDot(obj)
        
        domo_pub = cls(
            id = dd.id,
            name = dd.name,
            description = dd.description,
            created_dt = dt.datetime.fromtimestamp(dd.created/1000) if dd.created else None,
            is_v2 = dd.isV2,
            full_auth = full_auth
        )
        
        if dd.subscription_authorizations and len(dd.subscription_authorizations) > 0 : 
            domo_pub.subscription_authorizations = [DomoPublication_Subscription(subscription_id = sub.id,
                                                                                 domain = sub.domain, 
                                                                                 created_dt = dt.datetime.fromtimestamp(sub.created/1000) 
                                                                                     if sub.created else None
                                                                                ) 
                                                    for sub in dd.subscription_authorizations]
            
        ## publish only supports sharing pages and datasets        
        if dd.children and len(dd.children) >0 :
            for child in dd.children:
                dmpc = DomoPublication_Content(
                    content_id = child.id,
                    entity_type = child.content.type,
                    entity_id = child.content.domoObjectId,
                    content_domain = child.content.domain)

                if not domo_pub.content_entity_ls:
                    domo_pub.content_entity_ls = []

                domo_pub.content_entity_ls.append( dmpc)

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
    async def get_from_id(cls, publication_id = None, full_auth:dmda.DomoFullAuth = None):
        
        full_auth = full_auth or cls.full_auth
        
        publication_id = publication_id or cls.publication_id
        
        res = await publish_routes.get_publication_by_id(full_auth = full_auth, publication_id = publication_id)
        
        if res.status != 200:
            print(res)
            return None
        
        return cls._from_json(obj = res.response, full_auth = full_auth)
    
    
    def convert_lineage_to_dataframe(self, return_raw:bool = False ):
        import pandas as pd
        import re
        
        flat_lineage_ls = self.lineage._flatten_lineage()        
        
        output_ls = [{'plubication_id' : self.id,
                   'publication_name' : self.name,
                   'is_v2' : self.is_v2,
                   'publish_created_dt' : self.created_dt,
                   'entity_type' : row.get('entity_type'),
                   'entity_id' : row.get('entity_id') 
                  } for row in flat_lineage_ls ]
        
        if return_raw:
            return output_ls
        
        return pd.DataFrame(output_ls)
    
    
               