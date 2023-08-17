from .routes import instance_config_routes, role_routes, datacenter_routes, publish_routes, application_routes, grant_routes
import aiohttp
import datetime as dt
import asyncio

import Library.utils.convert as cd

from ..utils.DictDot import DictDot
from dataclasses import dataclass, field
from typing import List

import importlib

from .DomoAuth import DomoFullAuth
from .DomoGrant import DomoGrant
from .DomoRole import DomoRole
from .DomoApplication import DomoApplication

import Library.DomoClasses.DomoPublish as dmpb
importlib.reload(dmpb)


@dataclass
class DomoConnector:
    id: str
    label: str
    title: str
    sub_title: str
    description: str
    create_date: dt.datetime
    last_modified: dt.datetime
    publisher_name: str
    writeback_enabled: bool
    tags: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)

    @classmethod
    def _from_str(cls, obj):
        dd = DictDot(obj)

        return cls(
            id=dd.databaseId,
            label=dd.label,
            title=dd.title,
            sub_title=dd.subTitle,
            description=dd.description,
            create_date=cd.convert_epoch_millisecond_to_datetime(
                dd.createDate),
            last_modified=cd.convert_epoch_millisecond_to_datetime(
                dd.lastModified),
            publisher_name=dd.publisherName,
            writeback_enabled=dd.writebackEnabled,
            tags=dd.tags,
            capabilities=dd.capabilities
        )


@dataclass
class DomoInstanceConfig:
    full_auth: DomoFullAuth

    @classmethod
    def _authorized_domain_from_string(cls, authorized_domain_string):
        if authorized_domain_string == "":
            return []

        # return json.loads(authorized_domain_string)

        return authorized_domain_string.split(',')

    @classmethod
    async def get_whitelist(cls, full_auth: DomoFullAuth, session: aiohttp.ClientSession = None, debug: bool = False) -> List[str]:
        res = await instance_config_routes.get_whitelist(full_auth=full_auth, session=session, debug=debug)

        if res.status == 200:
            return res.response.get('addresses')

    @classmethod
    async def update_whitelist(cls, full_auth: DomoFullAuth, ip_address_list: list[str], debug: bool = False, is_upsert: bool = True, log_results: bool = False):

        res = await instance_config_routes.update_whitelist(full_auth=full_auth,
                                                            ip_address_list=ip_address_list,
                                                            debug=debug, log_results=log_results)

        if debug:
            print(res)

        if res.status == 200:
            return {'status': res.status, 'response': res.response}

    @classmethod
    async def get_roles(cls, full_auth: DomoFullAuth,
                        debug: bool = False,
                        session: aiohttp.ClientSession = None):

        res = await role_routes.get_roles(full_auth=full_auth,
                                          debug=debug,
                                          session=session)

        if res.status == 200:
            json_list = res.response
            return [DomoRole._from_str(id=obj.get('id'),
                                       name=obj.get('name'),
                                       description=obj.get('description'),
                                       full_auth=full_auth
                                       ) for obj in json_list]

    @classmethod
    async def get_grants(cls, full_auth: DomoFullAuth,
                         debug: bool = False,
                         session: aiohttp.ClientSession = None,
                         return_raw: bool = False):

        res = await grant_routes.get_grants(full_auth=full_auth,
                                            debug=debug,
                                            session=session)

        if res.status == 200 and not return_raw:
            json_list = res.response
            return [DomoGrant._from_json(obj) for obj in json_list]

        elif res.status == 200 and return_raw:
            return res.response

    @classmethod
    async def get_authorized_domains(cls, full_auth: DomoFullAuth, debug: bool = False, session: aiohttp.ClientSession = None):
        res = await instance_config_routes.get_authorized_domains(full_auth=full_auth,
                                                                  debug=debug,
                                                                  session=session)

        if res.status == 200:
            str = cls._authorized_domain_from_string(res.response.get('value'))
            return str

    @classmethod
    async def get_connectors(cls, full_auth: DomoFullAuth,
                             session: aiohttp.ClientSession = None,
                             debug: bool = False,
                             limit=100,
                             ):

        is_close_session = False
        if not session:
            is_close_session = True
            session = aiohttp.ClientSession()

        def arr_fn(res):
            # pprint(res.response)
            return res.response.get('searchObjects')

        def alter_maximum_fn(res):
            return res.response.get('totalResultCount')

        body = {
            "count": limit,
            "offset": 0,
            "hideSearchObjects": True,
            "combineResults": False,
            "entities": ["CONNECTOR"],
            "query": "*"}

        obj_list = await datacenter_routes.search_datacenter(
            full_auth=full_auth,
            arr_fn=arr_fn,
            alter_maximum_fn=alter_maximum_fn,
            body=body,
            session=session,
            limit=limit,
            debug=debug)

        if is_close_session:
            await session.close()

        return [DomoConnector._from_str(obj) for obj in obj_list]

    @classmethod
    async def update_authorized_domains(cls, full_auth: DomoFullAuth,
                                        authorized_domain_list: list[str],
                                        is_replace_existing_list: bool = False,
                                        debug: bool = False):

        if not is_replace_existing_list:
            existing_domain_list = await cls.get_authorized_domains(full_auth=full_auth, debug=debug)

            authorized_domain_list.extend(existing_domain_list)

        if debug:
            print(
                f'🌡️ updating authorized domain with {",".join(authorized_domain_list)}')

        res = await instance_config_routes.update_authorized_domains(full_auth=full_auth,
                                                                     authorized_domain_list=authorized_domain_list,
                                                                     debug=debug)

        if debug:
            "update_authorized_domains"
            print(res)

        if res.status == 200 or res.status == 204:
            res = {'authorized_domains': await cls.get_authorized_domains(full_auth=full_auth, debug=debug),
                   'status': 200}

        return res

    @classmethod
    async def get_applications(cls,
                               full_auth: DomoFullAuth,
                               debug: bool = False, session: aiohttp.ClientSession = None, return_raw: bool = False):

        res = await application_routes.get_applications(full_auth=full_auth,
                                                        debug=debug,
                                                        session=session)
        if debug:
            print('Getting Domostats jobs')

        if res.status == 200 and not return_raw:
            return [DomoApplication._from_json(job) for job in res.response]

        if res.status == 200 and return_raw:
            return res.response

    @classmethod
    async def get_publications(cls,
                               full_auth: DomoFullAuth,
                               debug: bool = False, session: aiohttp.ClientSession = None, return_raw: bool = False):

        res = await publish_routes.search_publications(full_auth=full_auth,
                                                       debug=debug,
                                                       session=session)
        if debug:
            print('Getting Publish jobs')

        if res.status == 200 and not return_raw:
            return await asyncio.gather(*[dmpb.DomoPublication.get_from_id(publication_id=job.get('id'),
                                                                           full_auth=full_auth) for job in res.response])

        if res.status == 200 and return_raw:
            return res.response
