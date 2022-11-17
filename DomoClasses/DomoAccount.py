from dataclasses import dataclass, field
from enum import Enum
import datetime as dt

import Library.DomoClasses.DomoAuth as dmda
import Library.DomoClasses.routes.account_routes as account_routes
import Library.utils.DictDot as dcd


@dataclass
class DomoAccount:
    id : int
    name : str
    data_provider_type: str
    created_dt : dt.datetime
    modified_dt: dt.datetime
    full_auth: dmda.DomoFullAuth  = field(repr = False, default = None)
    
    @classmethod
    def _from_json(cls, obj: dict, full_auth:dmda.DomoFullAuth = None):
        dd = dcd.DictDot(obj)
        
        return cls(id = dd.id,
            name = dd.name,
            data_provider_type = dd.dataProviderType,
            created_dt = dd.createdAt,
            modified_dt = dd.modifiedAt,
                  full_auth = full_auth)
            
    
    @classmethod
    async def get_from_id(cls, full_auth :dmda.DomoFullAuth, account_id:int):
        res = await account_routes.get_account_from_id(full_auth = full_auth, account_id = account_id)
        
        if res.status != 200 :
            return None
        
        obj = res.response
        return cls._from_json(obj, full_auth)
    
    