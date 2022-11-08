from dataclasses import dataclass,field
import aiohttp
import asyncio
import datetime as dt

from pprint import pprint

import Library.DomoClasses.DomoAuth as dmda
import Library.DomoClasses.DomoDatacenter as dmdc
from Library.utils.DictDot import DictDot

from Library.DomoClasses.routes import sandbox_routes


@dataclass
class DomoRepository:
    id: str
    name: str
    last_updated_dt: dt.datetime
    commit_dt: dt.datetime
    commit_version: str
    full_auth : dmda.DomoAuth = None
    content_page_id_ls :list[str] = None
    content_card_id_ls :list[str] = None
    content_dataflow_id_ls :list[str] = None
    content_view_id_ls :list[str] = None
    content_dataset_id_ls :list[str] = None

    @classmethod
    def _from_json(cls, obj, full_auth = None):
        dd = DictDot(obj)
    
        return cls(
            id = dd.id,
            full_auth = full_auth,
            name = dd.name,
            content_page_id_ls = dd.repositoryContent.pageIds,
            content_card_id_ls = dd.repositoryContent.cardIds,
            content_dataflow_id_ls = dd.repositoryContent.dataflowIds,
            content_view_id_ls = dd.repositoryContent.viewIds,
            last_updated_dt = dd.updated,
            commit_dt = dd.lastCommit.completed,
            commit_version = dd.lastCommit.commitName
        )
    
    async def _get_page_card_ids(self, full_auth = None):
        import Library.DomoClasses.DomoPage as dmpg
        
        page_card_ls = await asyncio.gather( *[dmpg.DomoPage.get_cards(page_id = page_id, 
                                                                     full_auth = full_auth or self.full_auth) for page_id in self.content_page_id_ls])
        if not page_card_ls or len(page_card_ls) == 0 :
            return
        
        for page in page_card_ls:
            if page and len(page) > 0:
                for card in page:
                    if card.id not in self.content_card_id_ls:
                        if not self.content_card_id_ls:
                            self.content_card_id_ls = []
                        
                        self.content_card_id_ls.append(card.id)
                
        return self.content_card_id_ls

    async def _get_entity_lineage(self, entity_id, full_auth, entity_type, debug:bool = False, debug_prn = False):
        entity_lineage = await dmdc.DomoDatacenter.get_lineage_upstream(full_auth = full_auth,
                                                                        entity_type = entity_type,
                                                                        entity_id = entity_id,
                                                                        debug = debug)
        for entity in entity_lineage:
            if entity.__class__.__name__ == 'DomoDataset':
                if not self.content_dataset_id_ls:
                    self.content_dataset_id_ls = []

                if entity.id not in self.content_dataset_id_ls:
                    self.content_dataset_id_ls.append(entity.id)

            if entity.__class__.__name__ == 'DomoDataflow':
                if not self.content_dataflow_id_ls:
                    self.content_dataflow_id_ls = []

                if entity.id not in self.content_dataflow_id_ls:
                    self.content_dataflow_id_ls.append(entity.id)

    async def _get_repo_entity_ls_lineage(self,
                                          domo_entity: dmdc.DomoEntity,
                                          full_auth = None,
                                          debug:bool = False, debug_prn : bool = False):
        full_auth = full_auth or self.full_auth
        
        entity_attribute = f"content_{domo_entity.name.lower()}_id_ls"
        
        
        return await asyncio.gather(*[ self._get_entity_lineage(full_auth=full_auth, 
                                                                entity_id = entity_id,
                                                                entity_type = domo_entity.value,
                                                               debug = debug, debug_prn = debug_prn) for entity_id in getattr(self, entity_attribute)])    

    @classmethod
    async def get_from_id(cls, repository_id: str, full_auth :dmda.DomoFullAuth):
        res = await sandbox_routes.get_repo_from_id(repository_id = repository_id, full_auth = full_auth)
        
        if res.status != 200:
            return None
            
        return cls._from_json(res.response, full_auth = full_auth)
        
        
        
    async def get_lineage(self, full_auth = None, debug_prn:bool = False, debug: bool = False):
        full_auth = full_auth or self.full_auth
        
        if self.content_page_id_ls and len(self.content_page_id_ls) > 0 :
            await self._get_page_card_ids(full_auth)
                
        if self.content_card_id_ls and len(self.content_card_id_ls) >0 :
            if debug_prn:
                print(f'🏁 getting card lineage for repo {self.id}')       
            await self._get_repo_entity_ls_lineage(domo_entity = dmdc.DomoEntity.CARD,
                                                   full_auth = full_auth, 
                                                   debug_prn = debug_prn, debug = debug)
            
        if self. content_dataflow_id_ls and len(self.content_dataflow_id_ls) >0 :
            if debug_prn:
                print(f'🏁 getting dataflow lineage for repo {self.id}')
                
            await self._get_repo_entity_ls_lineage(domo_entity = dmdc.DomoEntity.DATAFLOW,
                                                   full_auth =full_auth, 
                                                   debug_prn = debug_prn, debug = debug)
            
        if self.content_dataset_id_ls and len(self.content_dataset_id_ls)>0:
            if debug_prn:
                print(f'🏁 getting dataset lineage for repo {self.id}')
                
            await self._get_repo_entity_ls_lineage(domo_entity = dmdc.DomoEntity.DATASET,
                                                   full_auth = full_auth,
                                                   debug_prn = debug_prn, debug = debug)
        
        return {
            'dataset_id_ls': self.content_dataset_id_ls,
            'dataflow_id_ls': self.content_dataflow_id_ls,
            'page_id_ls': self.content_page_id_ls,
            'card_id_ls': self.content_card_id_ls}
    
    def convert_lineage_to_dataframe(self, is_return_obj_ls:bool = False ):
        import pandas as pd
        import re
        
        attribute_ls = [ attribute for attribute in dir(self) if  re.match('.*_id_ls$', attribute) and re.match('^content_.*', attribute)]
        
        output_ls = []
        for attribute in attribute_ls:
            if getattr(self,attribute) and len(getattr(self,attribute)) > 0:
                
                entity_type = dmdc.DomoEntity[attribute.replace('content_', '').replace('_id_ls','').upper()].value
                
                row_ls = [{ 'sandbox_id' : self.id,
                           'sandbox_name' : self.name,
                           'version' : self.commit_version,
                           'commit_dt' : self.commit_dt,
                           'last_updated_dt' : self.last_updated_dt,
                       'entity_type' : entity_type,
                       'entity_id' : row} for row in getattr(self,attribute)]
                output_ls += row_ls
        
        if is_return_obj_ls:
            return output_ls
        
        return pd.DataFrame(output_ls)

@dataclass
class DomoSandbox:
    
    @classmethod
    async def get_repositories(cls, full_auth):
        res =  await sandbox_routes.get_shared_repos( full_auth)
        
        if res.status != 200:
            return None
        
        domo_repos =[DomoRepository._from_json(obj, full_auth = full_auth) for obj in res.response.get('repositories')]

        return domo_repos