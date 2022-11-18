import aiohttp
import asyncio

import pandas as pd
import io

import json
from dataclasses import dataclass, field

from .DomoAuth import DomoDeveloperAuth, DomoFullAuth
from .routes import dataflow_routes
from ..utils import Exceptions as ex
from ..utils import convert as cd
from ..utils.Base import Base
from ..utils.DictDot import DictDot


@dataclass
class DomoDataflow(Base):

    id: str
    name: str

    full_auth: DomoFullAuth = field(repr=False, default_factory=list)
    dev_auth: DomoDeveloperAuth = field(repr=False, default_factory=list)

    owner: str = None
    description: str = None
    domo_instance: str = None
    tags: list = None

    @classmethod
    async def get_from_id(cls,
                          id: str,
                          full_auth: DomoFullAuth = None,
                          debug: bool = False, log_results: bool = False):

        try:
            res = await dataflow_routes.get_dataset_by_id(full_auth=full_auth,
                                                          id=id, debug=debug)

            if debug:
                pprint(res)

            # if res.status == 404:
            #     print("f error retrieving get_from_id {full_auth.domo_instance} - {id} status = 404")
            #     raise ex.InvalidDataset(domo_instance=full_auth.domo_instance, dataset_id=id)

            dd = DictDot(res.response)
            ds = cls(
                domo_instance=full_auth.domo_instance or dev_auth.domo_instance,
                full_auth=full_auth,
                id=dd.id,
                name=dd.name,
                description=dd.description,
                owner=dd.owner,
                tags=dd.tags,
            )

            return ds

        except Exception as e:
            print(e)
            return None
