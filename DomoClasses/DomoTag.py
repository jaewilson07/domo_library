from dataclasses import dataclass

import aiohttp

from . import DomoAuth as dmda
from .routes import get_data


async def _set_dataset_tags(full_auth: dmda.DomoFullAuth,
                            tag_ls: [str],
                            dataset_id: str,
                            debug: bool = False,
                            session: aiohttp.ClientSession = None,
                            log_results: bool = False
                            ):
    url = f"https://{full_auth.domo_instance}.domo.com/api/data/ui/v3/datasources/{dataset_id}/tags"

    if debug:
        print(url)

    return await get_data(
        auth=full_auth,
        url=url,
        method='POST',
        log_results=log_results,
        debug=debug,
        body=tag_ls,
        session=session
    )


@dataclass
class Dataset_Tags:
    dataset: any
    tag_ls: [str] = None

    async def set(self,
                  tag_ls: [str],
                  full_auth: dmda.DomoFullAuth = None,
                  debug: bool = False, log_results: bool = False,
                  session: aiohttp.ClientSession = None):

        full_auth = full_auth or self.dataset.full_auth

        res = await _set_dataset_tags(full_auth=full_auth,
                                      tag_ls=list(set(tag_ls)),
                                      dataset_id=self.dataset.id,
                                      debug=debug,
                                      session=session,
                                      log_results=log_results)

        if res.status != 200:
            print('invalid response')
            return None

        new_ds = await self.dataset.get_from_id(id=self.dataset.id,
                                                full_auth=self.dataset.full_auth)

        self.tag_ls = new_ds.tags.tag_ls

        return self.tag_ls

    async def add(self,
                  add_tag_ls: [str],
                  full_auth: dmda.DomoFullAuth = None,
                  debug: bool = False, log_results: bool = False, session: aiohttp.ClientSession = None
                  ):

        full_auth = full_auth or self.dataset.full_auth

        existing_tag_ls = self.tag_ls or []
        add_tag_ls += existing_tag_ls

        return await self.set(full_auth=full_auth,
                              tag_ls=list(set(add_tag_ls)),
                              debug=debug, session=session, log_results=log_results)

    async def remove(self,
                     remove_tag_ls: [str],
                     full_auth: dmda.DomoFullAuth = None,
                     debug: bool = False, log_results: bool = False, session: aiohttp.ClientSession = None
                     ):
        full_auth = full_auth or self.dataset.full_auth

        existing_tag_ls = self.tag_ls or []
        existing_tag_ls = [
            ex for ex in existing_tag_ls if ex not in remove_tag_ls]

        return await self.set(full_auth=full_auth,
                              tag_ls=list(set(existing_tag_ls)),
                              debug=debug, session=session, log_results=log_results)
