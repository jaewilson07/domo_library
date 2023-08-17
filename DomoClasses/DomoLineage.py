import aiohttp
import asyncio
from enum import Enum

from dataclasses import dataclass, field

import Library.DomoClasses.DomoAuth as dmda
import Library.DomoClasses.DomoDatacenter as dmdc

from .routes import datacenter_routes


def get_content_list_ls(cls_obj, regex_pattern_ls=None):
    import re

    regex_pattern_ls = regex_pattern_ls or ['.*_id_ls$', '^content_.*']

    content_list_ls = [content_list for content_list in dir(cls_obj)
                       if all([re.match(pattern, content_list) for pattern in regex_pattern_ls])]

    result = []
    for content_name in content_list_ls:
        if not getattr(cls_obj, content_name) or len(getattr(cls_obj, content_name)) == 0:
            continue

        base_name = content_name
        [base_name := re.sub(regex_pattern.replace('.*', ''), '', base_name)
         for regex_pattern in regex_pattern_ls]

        result.append({'list_name': content_name,
                       'entity_name': base_name,
                       'regex_pattern_ls': regex_pattern_ls
                       })
    return result


@dataclass
class DomoLineage:
    id: str
    parent: any = field(default=None, repr=False)
    page_id_ls: [str] = None
    card_id_ls: [str] = None
    dataflow_id_ls: [str] = None
    dataset_id_ls: [str] = None

    entity_ls: [any] = None

    async def _get_page_card_ids(self):

        import Library.DomoClasses.DomoPage as dmpg

        if not self.parent.content_page_id_ls or len(self.parent.content_page_id_ls) == 0:
            return None

        page_card_ls = await asyncio.gather(*[dmpg.DomoPage.get_cards(page_id=page_id,
                                                                      full_auth=self.parent.full_auth)
                                              for page_id in self.parent.content_page_id_ls])

        if not page_card_ls or len(page_card_ls) == 0:
            return

        if not self.card_id_ls:
            self.card_id_ls = []

        for page in page_card_ls:
            if page and len(page) > 0:
                for card in page:
                    if card.id not in self.card_id_ls:
                        self.card_id_ls.append(card.id)

        return self.card_id_ls

    async def get_entity_lineage_upstream(self,
                                          entity_id,
                                          entity_type,
                                          full_auth: dmda.DomoFullAuth = None,
                                          session: aiohttp.ClientSession = None,
                                          debug: bool = False,
                                          debug_prn: bool = False):

        import Library.DomoClasses.DomoDataflow as dmdf
        import Library.DomoClasses.DomoDataset as dmds

        try:
            full_auth = full_auth or self.parent.full_auth

            if not session:
                is_close_session = True
            session = session or aiohttp.ClientSession()

            res = await datacenter_routes.get_lineage_upstream(full_auth=full_auth,
                                                               entity_type=entity_type,
                                                               entity_id=entity_id,
                                                               session=session, debug=debug)
            if res.status != 200:
                return None

            obj = res.response

            domo_obj_ls = []

            for key, item in obj.items():
                entity_type = item.get('type')
                entity_id = item .get('id')

                if not self.entity_ls:
                    self.entity_ls = []

                if entity_type == 'DATA_SOURCE':
                    if not self.dataset_id_ls:
                        self.dataset_id_ls = []

                    if entity_id not in self.dataset_id_ls:
                        self.dataset_id_ls.append(entity_id)

                        do = await dmds.DomoDataset.get_from_id(full_auth=full_auth, id=entity_id)
                        domo_obj_ls.append(do)
                        self.entity_ls.append(do)

                if entity_type == 'DATAFLOW':
                    if not self.dataflow_id_ls:
                        self.dataflow_id_ls = []

                    if entity_id not in self.dataflow_id_ls:
                        self.dataflow_id_ls.append(entity_id)

                        do = await dmdf.DomoDataflow.get_from_id(full_auth=full_auth, id=entity_id)
                        domo_obj_ls.append(do)
                        self.entity_ls.append(do)

            return domo_obj_ls

        finally:
            if is_close_session:
                await session.close()

    async def _get_entity_ls_lineage(self,
                                     domo_entity: dmdc.DomoEntity,
                                     full_auth=None,
                                     session: dmda.DomoFullAuth = None,
                                     debug: bool = False, debug_prn: bool = False):
        full_auth = full_auth or self.full_auth

        entity_attribute = f"{domo_entity.name.lower()}_id_ls"

        return await asyncio.gather(*[self.get_entity_lineage_upstream(full_auth=full_auth,
                                                                       entity_id=entity_id,
                                                                       entity_type=domo_entity.value,
                                                                       session=session,
                                                                       debug=debug, debug_prn=debug_prn)
                                      for entity_id in getattr(self, entity_attribute)])

    def _reset_lineage_and_sync_parent(self):

        content_list = get_content_list_ls(self.parent)

        for content_obj in content_list:

            parent_content = getattr(self.parent, content_obj.get('list_name'))

            lineage_content_name = f"{content_obj.get('entity_name')}_id_ls"

            setattr(self,
                    lineage_content_name,
                    parent_content
                    )
        return self

    async def get(self,
                  debug_prn: bool = False, debug: bool = False,
                  full_auth: dmda.DomoFullAuth = None,
                  session=None):

        full_auth = full_auth or self.parent.full_auth

        self._reset_lineage_and_sync_parent()

        if self.page_id_ls:
            await self._get_page_card_ids()

        if self.card_id_ls and len(self.card_id_ls) > 0:
            if debug_prn:
                print(f'🏁 getting card lineage for repo {self.id}')
            await self._get_entity_ls_lineage(domo_entity=dmdc.DomoEntity.CARD,
                                              full_auth=full_auth,
                                              debug_prn=debug_prn, debug=debug, session=session)

        if self.dataflow_id_ls and len(self.dataflow_id_ls) > 0:
            if debug_prn:
                print(f'🏁 getting dataflow lineage for repo {self.id}')

            await self._get_entity_ls_lineage(domo_entity=dmdc.DomoEntity.DATAFLOW,
                                              full_auth=full_auth,
                                              debug_prn=debug_prn, debug=debug, session=session)

        if self.dataset_id_ls and len(self.dataset_id_ls) > 0:
            if debug_prn:
                print(f'🏁 getting dataset lineage for repo {self.id}')

            await self._get_entity_ls_lineage(domo_entity=dmdc.DomoEntity.DATASET,
                                              full_auth=full_auth,
                                              debug_prn=debug_prn, debug=debug, session=session)

        return self

    def _flatten_lineage(self):
        attribute_ls = get_content_list_ls(self, ['.*_id_ls$'])

        output_ls = []

        for attribute in attribute_ls:
            ls_name = attribute.get('list_name')
            entity_name = attribute.get('entity_name')
            entity_type = dmdc.DomoEntity[entity_name.upper()].value

            row_ls = [{'entity_type': entity_type,
                       'entity_id': row} for row in getattr(self, ls_name)]
            output_ls += row_ls

        return output_ls
