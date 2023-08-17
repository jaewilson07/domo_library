from dataclasses import dataclass, field
import aiohttp
import asyncio
import datetime as dt

from pprint import pprint

import Library.DomoClasses.DomoAuth as dmda
import Library.DomoClasses.DomoLineage as dmdl
from Library.utils.DictDot import DictDot


from Library.DomoClasses.routes import sandbox_routes


class InvalidRepositoryError(Exception):
    pass


@dataclass
class DomoRepository:
    id: str
    name: str
    last_updated_dt: dt.datetime
    commit_dt: dt.datetime
    commit_version: str
    full_auth: dmda.DomoAuth = None
    content_page_id_ls: list[str] = None
    content_card_id_ls: list[str] = None
    content_dataflow_id_ls: list[str] = None
    content_view_id_ls: list[str] = None

    def __post_init__(self):
        self.lineage = dmdl.DomoLineage(id=self.id,
                                        parent=self)

    @classmethod
    def _from_json(cls, obj, full_auth=None):

        import dateutil.parser as dtut

        dd = DictDot(obj)

        return cls(
            id=dd.id,
            full_auth=full_auth,
            name=dd.name,
            content_page_id_ls=dd.repositoryContent.pageIds,
            content_card_id_ls=dd.repositoryContent.cardIds,
            content_dataflow_id_ls=dd.repositoryContent.dataflowIds,
            content_view_id_ls=dd.repositoryContent.viewIds,
            last_updated_dt=dtut.parse(dd.updated).replace(tzinfo=None),
            commit_dt=dtut.parse(dd.lastCommit.completed).replace(tzinfo=None),
            commit_version=dd.lastCommit.commitName
        )

    @classmethod
    async def get_from_id(cls, repository_id: str, full_auth: dmda.DomoFullAuth):
        res = await sandbox_routes.get_repo_from_id(repository_id=repository_id, full_auth=full_auth)

        if res.status == 404:
            raise InvalidRepositoryError

        return cls._from_json(res.response, full_auth=full_auth)

    def convert_lineage_to_dataframe(self, return_raw: bool = False):
        import pandas as pd
        import re

        flat_lineage_ls = self.lineage._flatten_lineage()

        output_ls = [{'sandbox_id': self.id,
                      'sandbox_name': self.name,
                      'version': self.commit_version,
                      'commit_dt': self.commit_dt,
                      'last_updated_dt': self.last_updated_dt,
                      'entity_type': row.get('entity_type'),
                      'entity_id': row.get('entity_id')
                      } for row in flat_lineage_ls]

        if return_raw:
            return output_ls

        return pd.DataFrame(output_ls)


@dataclass
class DomoSandbox:

    @classmethod
    async def get_repositories(cls, full_auth):
        res = await sandbox_routes.get_shared_repos(full_auth)

        if res.status != 200:
            return None

        domo_repos = [DomoRepository._from_json(
            obj, full_auth=full_auth) for obj in res.response.get('repositories')]

        return domo_repos
