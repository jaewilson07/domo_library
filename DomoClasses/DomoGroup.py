import aiohttp

from dataclasses import dataclass, field
from typing import List

from .DomoAuth import DomoFullAuth
from .routes import group_routes
from ..utils.Base import Base
from ..utils.DictDot import DictDot


class GroupMembership:
    def __init__(self, group):
        self.group = group
        self.group_members_ids = self.set_group_member_ids()

    def set_group_member_ids(self):
        return [member.id for member in self.group.group_members]

    async def _update_group_access(self, full_auth: DomoFullAuth, body,
                                   log_results: bool = False, debug: bool = False):

        res = await group_routes.update_group_membership(full_auth=full_auth, body=body,
                                                         log_results=log_results,
                                                         debug=debug)

        if debug:
            res.print(is_pretty=True)

        if res.status == 200:
            if log_results:
                if self.group_members:
                    print(
                        f'Group Membership includes {len(self.group_members)}')

        return res

    async def set_membership(self, user_ids_list,
                             full_auth: DomoFullAuth = None,
                             log_results: bool = False, debug: bool = False):

        full_auth = full_auth or self.group.full_auth

        add_user_arr = [str(uid) for uid in user_ids_list]
        remove_user_arr = [
            str(uid) for uid in self.group_members_ids if str(uid) not in add_user_arr]

        body = group_routes.generate_body_update_group_membership(group_id=self.group.id,
                                                                  add_user_arr=add_user_arr,
                                                                  remove_user_arr=remove_user_arr)

        return await self._update_group_access(full_auth=full_auth, body=body, log_results=log_results, debug=debug)

    async def alter_owner(self, full_auth: DomoFullAuth, add_owner_ids_list=None, remove_owner_ids_arr=None,
                          log_results: bool = False, debug: bool = False):

        body = group_routes.generate_body_update_group_membership(group_id=self.group.id,
                                                                  add_owner_user_arr=add_owner_ids_list,
                                                                  remove_owner_user_arr=remove_owner_ids_arr)

        return await self._update_group_access(full_auth=full_auth, body=body, log_results=log_results, debug=debug)

    async def alter_membership(self, full_auth: DomoFullAuth, add_user_ids_list, remove_users_ids_list,
                               log_results: bool = False, debug: bool = False):

        body = group_routes.generate_body_update_group_membership(group_id=self.group.id,
                                                                  add_user_arr=add_user_ids_list,
                                                                  remove_user_arr=remove_users_ids_list)

        return await self._update_group_access(full_auth=full_auth, body=body, log_results=log_results, debug=debug)


class DomoGroups:
    def __init__(self, user):
        self.user = user

    def _groups_to_domo_group(json_list, full_auth: DomoFullAuth):

        return [DomoGroup._from_search_json(full_auth=full_auth, json_obj=json_obj) for json_obj in json_list]

    @classmethod
    async def all_groups(cls, full_auth: DomoFullAuth, debug: bool = False, log_results: bool = False, session: aiohttp.ClientSession = None):

        res = await group_routes.get_all_groups(full_auth=full_auth, debug=debug, log_results=log_results, session=session)

        if res.status != 200:
            return None

        if len(res.response) > 0:
            json_list = res.response

            return cls._groups_to_domo_group(json_list=json_list, full_auth=full_auth)

        else:
            return []


@dataclass
class DomoGroup(Base):
    domo_instance: str = None
    full_auth: DomoFullAuth = None
    id: str = None
    name: str = None
    type: str = None
    description: str = None
    group_members: list = field(repr=False, default_factory=list)
    owner_members: list = field(repr=False, default_factory=list)

    def __post_init__(self):
        self.domo_instance = self.domo_instance or full_auth.domo_instance
        self.Membership = GroupMembership(self)
        Base().__init__()

    @classmethod
    def _from_search_json(cls, full_auth: DomoFullAuth, json_obj):
        dd = DictDot(json_obj)

        g = cls(full_auth=full_auth,
                id=dd.id or dd.groupId,
                domo_instance=full_auth.domo_instance,
                description=dd.description
                )

        g.name = dd.name
        g.type = dd.type or dd.groupType
        g.group_members = dd.groupMembers or dd.users
        g.owner_members = dd.owners
        return g
    
    @classmethod
    def _from_groups_API_json(cls, full_auth: DomoFullAuth, json_obj):
        dd = DictDot(json_obj)

        g = cls(full_auth=full_auth,
                id=dd.id or dd.groupId,
                domo_instance=full_auth.domo_instance,
                description=dd.description
                )

        g.name = dd.name
        g.type = dd.type
        g.group_members = dd.userIds
        return g

    @staticmethod
    def _groups_to_domo_group(json_list, full_auth: DomoFullAuth) -> List[dict]:
        domo_groups = []

        for json_obj in json_list:
            group = DomoGroup._from_search_json(
                full_auth=full_auth,
                json_obj=json_obj)
            domo_groups.append(group)

        return domo_groups

    @classmethod
    async def create_from_name(cls, full_auth: DomoFullAuth,
                               group_name: str = None,
                               group_type: str = None,
                               description: str = None,
                               log_results: bool = False, debug: bool = False):

        res = await group_routes.create_group(full_auth=full_auth,
                                              group_name=group_name,
                                              group_type=group_type,
                                              description=description,
                                              log_results=log_results, debug=debug)

        if log_results:
            res.print(is_pretty=True)

        if res.status == 200 and res.response.get('id'):
            domo_group = cls._from_search_json(
                full_auth=full_auth, json_obj=res.response)
            return domo_group
        
    @classmethod
    async def get_by_id(cls, full_auth:DomoFullAuth,
                        group_id: str):
        res = await group_routes.get_group_by_id(full_auth= full_auth, group_id=group_id)
        if res.status == 200:
            return cls._from_groups_API_json(full_auth = full_auth, json_obj = res.response)

    @classmethod
    async def search_by_name(cls, full_auth: DomoFullAuth,
                             group_name: str,
                             create_if_not_exist: bool = True,
                             allow_only_one: bool = True,
                             debug: bool = False, log_results: bool = False):

        res = await group_routes.search_groups_by_name(full_auth=full_auth, search_name=group_name, debug=debug,
                                                       log_results=log_results)

        if res.status == 200:
            json_list = res.response
            domo_groups = cls._groups_to_domo_group(json_list, full_auth)
            domo_groups = [
                group for group in domo_groups if group.name == group_name]

            if debug:
                print('groups after name filter')
                for group in domo_groups:
                    print(group)

            if create_if_not_exist and not domo_groups:
                if debug:
                    print("create if not exist and not domo groups")
                return await DomoGroup.create_from_name(full_auth=full_auth, group_name=group_name, debug=debug)

            elif allow_only_one:
                if debug:
                    print('allow only one')

                    for group in domo_groups:
                        print(group, group.name, group_name)

                return next((group for group in domo_groups if group.name == group_name), None)

            else:
                return domo_groups
        else:
            return None
