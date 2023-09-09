# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoGroup.ipynb.

# %% auto 0
__all__ = ['UpdateGroupMembership', 'GroupMembership', 'DomoGroup', 'DomoGroups']

# %% ../../nbs/classes/50_DomoGroup.ipynb 2
from dataclasses import dataclass, field
from typing import List, Union

import httpx
import asyncio

from fastcore.basics import patch_to


import domolibrary.utils.chunk_execution as ce

import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de
import domolibrary.utils.DictDot as util_dd

import domolibrary.routes.group as group_routes

# import domolibrary.routes.publish as publish_routes

import domolibrary.classes.DomoUser as dmu


# %% ../../nbs/classes/50_DomoGroup.ipynb 3
from ..routes.group import GroupType_Enum, SearchGroups_Error


# %% ../../nbs/classes/50_DomoGroup.ipynb 5
class UpdateGroupMembership(de.DomoError):
    def __init__(self, member_name, group_name, domo_instance):
        super().__init__(domo_instance=domo_instance,
                         message=f"unable to add {member_name} to {group_name}")


class GroupMembership:
    _add_member_ls: list[str]
    _remove_group_ls: list[str]

    _add_owners_ls: list[str]
    _remove_owner_ls: list[str]

    _current_member_ls: list[str]
    _current_owner_ls: list[str]

    group = None

    def __init__(self, group):
        self.group = group

        self._add_member_ls: [dict] = []
        self._remove_member_ls: [dict] = []

        self._add_owner_ls: [dict] = []
        self._remove_owner_ls: [dict] = []

        self._current_member_ls = []
        self._current_owner_ls = []

    def _add_to_list(self, member, list_to_update, debug_prn: bool = False):

        import domolibrary.classes.DomoUser as dmu

        match_obj = next((user_obj for user_obj in list_to_update if user_obj.get(
            'id') == member.id), None)
        if match_obj:
            print(f"➡️ {member}  of type {type(member).__name__} already in ls")
            return list_to_update

        if debug_prn:
            print(
                f"➡️ adding {member.id}  of type {type(member).__name__} to {self.group.name}")

        if isinstance(member, dmu.DomoUser):
            list_to_update.append({'id': str(member.id), 'type': 'USER'})

            return list_to_update

        if isinstance(member, DomoGroup):
            list_to_update.append({'id': str(member.id), 'type': 'GROUP'})

            return list_to_update

        member_name = getattr(member, 'name', None) or getattr(
            member, 'display_name', None) or "name not provided"

        raise UpdateGroupMembership(domo_instance=self.group.auth.domo_instance,
                                    group_name=self.group.name,
                                    member_name=member_name)

    def _add_member(self, member, debug_prn: bool = False):
        return self._add_to_list(member, self._add_member_ls, debug_prn)

    def _remove_member(self, member, debug_prn: bool = False):
        if type(member).__name__ == 'DomoGroup' and member.type == 'system':
            if debug_prn:
                print(f"remove_owner - skipping {member.name} type is {member.type}")
            return
        return self._add_to_list(member, self._remove_member_ls, debug_prn)

    def _add_owner(self, member, debug_prn: bool = False):
        return self._add_to_list(member, self._add_owner_ls, debug_prn)

    def _remove_owner(self, member, debug_prn: bool = False):
        if type(member).__name__ == 'DomoGroup' and member.type == 'system':
            if debug_prn:
                print(f"remove_owner - skipping {member.name} type is {member.type}")
            return
            
        return self._add_to_list(member, self._remove_owner_ls, debug_prn)

    def _reset_obj(self):
        self._add_member_ls = []
        self._remove_member_ls = []

        self._add_owner_ls = []
        self._remove_owner_ls = []

    async def _update_group_access(self,
                                   debug_api: bool = False, session: httpx.AsyncClient = None,
                                   ):

        res = await group_routes.update_group_membership(auth=self.group.auth,
                                                         group_id=self.group.id,
                                                         add_member_arr=self._add_member_ls,
                                                         remove_member_arr=self._remove_member_ls,
                                                         add_owner_arr=self._add_owner_ls,
                                                         remove_owner_arr=self._remove_owner_ls,
                                                         debug_api=debug_api,
                                                         session=session)
        self._reset_obj()

        # add
        # remove
        # set


# %% ../../nbs/classes/50_DomoGroup.ipynb 7
@patch_to(GroupMembership)
async def get_owners(
    self: GroupMembership,
    auth: dmda.DomoAuth = None,
    return_raw: bool = False,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):
    import domolibrary.classes.DomoUser as dmu

    auth = auth or self.group.auth

    self._current_owner_ls = []

    res = await group_routes.get_group_owners(group_id=self.group.id, auth=self.group.auth)
    if return_raw:
        return res
    
    group_ids = [obj.get('id') for obj in res.response if obj.get('type') == 'GROUP']
    if group_ids:
        domo_groups = await ce.gather_with_concurrency(n = 60, * [DomoGroup.get_by_id(group_id=group_id, auth=auth) for group_id in group_ids])
        self._current_owner_ls += domo_groups
    
    user_ids = [obj.get('id') for obj in res.response if obj.get('type') == 'USER']
    if user_ids:
        domo_users = await dmu.DomoUsers.by_id(user_ids=user_ids, auth=auth, only_allow_one = False)
        self._current_owner_ls += domo_users
        
    self.group.owner_id_ls = group_ids + user_ids
    self.group.owner_ls = self._current_owner_ls 

    return self._current_owner_ls
    # return domo_users


# %% ../../nbs/classes/50_DomoGroup.ipynb 8
@patch_to(GroupMembership)
async def get_members(
    self: GroupMembership,
    auth: dmda.DomoAuth = None,
    return_raw: bool = False,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):
    import domolibrary.classes.DomoUser as dmu

    auth = auth or self.group.auth

    self._current_member_ls = []

    res = await group_routes.get_group_membership(group_id=self.group.id, auth=self.group.auth)
    if return_raw:
        return res
    
    user_ids = [obj.get('userId') for obj in res.response ]
    if user_ids:
        domo_users = await dmu.DomoUsers.by_id(user_ids=user_ids, auth=auth, only_allow_one = False)
        self._current_member_ls += domo_users

    self.group.members_id_ls = user_ids
    self.group.members_ls = self._current_member_ls

    return self.group.members_ls


# %% ../../nbs/classes/50_DomoGroup.ipynb 10
@patch_to(GroupMembership)
async def add_members(
    self: GroupMembership,
    add_user_ls: list[dmu.DomoUser],
    return_raw: bool = False,
    debug_api: bool = False, 
    debug_prn: bool = False,
    session: httpx.AsyncClient = None,
):
    self._reset_obj()

    [self._add_member(domo_user, debug_prn) for domo_user in add_user_ls]

    res = await self._update_group_access(debug_api=debug_api, session=session)

    if return_raw:
        return res

    return await self.get_members()


@patch_to(GroupMembership)
async def remove_members(
    self: GroupMembership,
    remove_user_ls: list[dmu.DomoUser],
    return_raw: bool = False,
    debug_api: bool = False, debug_prn: bool = False, session: httpx.AsyncClient = None,
):
    self._reset_obj()

    [self._remove_member(domo_user, debug_prn) for domo_user in remove_user_ls]

    res = await self._update_group_access(debug_api=debug_api, session=session)

    if return_raw:
        return res

    return await self.get_members()


@patch_to(GroupMembership)
async def set_members(
    self: GroupMembership,
    user_ls: list[dmu.DomoUser],
    return_raw: bool = False,
    debug_api: bool = False, debug_prn:bool = False ,session: httpx.AsyncClient = None,
):
    self._reset_obj()

    domo_users = await self.get_members()

    if debug_prn:
        print({'domo_users': domo_users, 'user_ls': user_ls})

    [self._add_member(domo_user, debug_prn) for domo_user in user_ls]
    [self._remove_member(domo_user, debug_prn) for domo_user in domo_users if domo_user not in user_ls]


    res= await self._update_group_access(debug_api=debug_api, session=session)

    if return_raw:
        return res

    return await self.get_members()


# %% ../../nbs/classes/50_DomoGroup.ipynb 11
@patch_to(GroupMembership)
async def add_owners(
    self: GroupMembership,
    add_owner_ls,
    return_raw: bool = False,
    debug_api: bool = False,
    debug_prn: bool = False,
    session: httpx.AsyncClient = None,
):
    self._reset_obj()

    [self._add_owner(domo_user, debug_prn) for domo_user in add_owner_ls]

    res = await self._update_group_access(debug_api=debug_api, session=session)

    if return_raw:
        return res

    return await self.get_owners()


@patch_to(GroupMembership)
async def remove_owners(
    self: GroupMembership,
    remove_owner_ls,
    return_raw: bool = False,
    debug_api: bool = False, debug_prn: bool = False, session: httpx.AsyncClient = None,
):
    self._reset_obj()

    [self._remove_owner(domo_user, debug_prn) for domo_user in remove_owner_ls]

    res = await self._update_group_access(debug_api=debug_api, session=session)

    if return_raw:
        return res

    return await self.get_owners()


@patch_to(GroupMembership)
async def set_owners(
    self: GroupMembership,
    owner_ls,
    return_raw: bool = False,
    debug_api: bool = False, debug_prn: bool = False, session: httpx.AsyncClient = None,
):
    self._reset_obj()

    domo_users = await self.get_owners()

    if debug_prn:
        print({'domo_users': domo_users, 'user_ls': owner_ls})

    [self._add_owner(domo_user, debug_prn) for domo_user in owner_ls]
    [self._remove_owner(domo_user, debug_prn)
     for domo_user in domo_users if domo_user not in owner_ls]

    res = await self._update_group_access(debug_api=debug_api, session=session)

    if return_raw:
        return res

    return await self.get_owners()


# %% ../../nbs/classes/50_DomoGroup.ipynb 13
@dataclass
class DomoGroup:
    auth: dmda.DomoAuth = field(repr=False, default=None)
    id: str = None
    name: str = None
    type: str = None
    description: str = None
    members_id_ls: list[str] = field(repr=False, default_factory=list)
    owner_id_ls: list[str] = field(repr=False, default_factory=list)
    
    members_ls: list[dict] = field(repr=False, default_factory=list)
    owner_ls : list[dict]= field(repr = False, default_factory = list)

    def __post_init__(self):
        # self.domo_instance = self.domo_instance or auth.domo_instance
        self.Membership = GroupMembership(self)

    @classmethod
    def _from_group_json(cls, auth: dmda.DomoAuth, json_obj):
        dd = json_obj

        if not isinstance(json_obj, util_dd.DictDot):
            dd = util_dd.DictDot(json_obj)

        return cls(
            auth=auth,
            id=dd.id or dd.groupId,
            name=dd.name,
            description=dd.description,
            type=dd.type or dd.groupType,
            members_id_ls=dd.userIds,
            owner_ls=dd.owners,
        )

    @classmethod
    def _from_grouplist_json(cls, auth: dmda.DomoAuth, json_obj):
        dd = json_obj

        if not isinstance(json_obj, util_dd.DictDot):
            dd = util_dd.DictDot(json_obj)

        return cls(
            auth=auth,
            id=dd.groupId,
            name=dd.name,
            description=dd.description,
            type=dd.groupType,
            owner_ls = dd.owners,
            owner_id_ls = [owner.id for owner in dd.owners],
            
            members_ls=dd.groupMembers,
            members_id_ls= [member.id for member in dd.members]
        )


    @staticmethod
    def _groups_to_domo_group(json_list, auth: dmda.DomoAuth) -> List[dict]:
        domo_groups = [
            DomoGroup._from_group_json(auth=auth, json_obj=json_obj)
            for json_obj in json_list
        ]

        return domo_groups

# %% ../../nbs/classes/50_DomoGroup.ipynb 15
@patch_to(DomoGroup, cls_method=True)
async def get_by_id(
    cls,
    auth: dmda.DomoAuth,
    group_id: str,
    return_raw: bool = False,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):

    res = await group_routes.get_group_by_id(
        auth=auth, group_id=group_id, debug_api=debug_api, session=session
    )
    if return_raw:
        return res

    if res.status != 200:
        raise Exception()

    dg = cls._from_group_json(auth=auth, json_obj=res.response)

    # await dg.Membership.get_owners()
    # await dg.Membership.get_members() # disabled because causes recursion
    return dg


# %% ../../nbs/classes/50_DomoGroup.ipynb 18
@patch_to(DomoGroup, cls_method=True)
async def search_by_name(
    cls,
    auth: dmda.DomoAuth,
    group_name: str,
    is_exact_match: bool = True,
    return_raw: bool = False,
    debug_api: bool = False,
    debug_prn: bool = False,
    session: httpx.AsyncClient = None,
):
    
    res = await group_routes.search_groups_by_name(
        auth=auth,
        search_name=group_name,
        debug_api=debug_api,
        is_exact_match=is_exact_match,
        session=session,
    )

    if return_raw:
        return res

    if isinstance(res.response, list):
        return cls._groups_to_domo_group(res.response, auth)

    return cls._from_group_json(auth=auth, json_obj=res.response)

# %% ../../nbs/classes/50_DomoGroup.ipynb 40
class DomoGroups:
    def __init__(self):
        pass

    @staticmethod
    def _groups_to_domo_group(json_list, auth: dmda.DomoAuth):

        return [
            DomoGroup._from_group_json(auth=auth, json_obj=json_obj)
            for json_obj in json_list
        ]

# %% ../../nbs/classes/50_DomoGroup.ipynb 42
@patch_to(DomoGroups, cls_method=True)
async def get_all_groups(
    cls: DomoGroups,
    auth: dmda.DomoAuth,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):

    res = await group_routes.get_all_groups(
        auth=auth, debug_api=debug_api, session=session
    )

    if len(res.response) > 0:
        json_list = res.response

        return cls._groups_to_domo_group(json_list=json_list, auth=auth)

    else:
        return []


# %% ../../nbs/classes/50_DomoGroup.ipynb 46
@patch_to(DomoGroups, cls_method=True)
async def toggle_system_group_visibility(cls: DomoGroups,auth: dmda.DomoAuth,
                                         is_hide_system_groups: bool,
                                         debug_api: bool = False):

    return await group_routes.toggle_system_group_visibility(auth=auth,
                                                is_hide_system_groups=is_hide_system_groups,
                                                debug_api=debug_api)


# %% ../../nbs/classes/50_DomoGroup.ipynb 50
@patch_to(GroupMembership)
async def add_owner_manage_groups_role(self : GroupMembership):
    
    await DomoGroups.toggle_system_group_visibility(auth = self.group.auth, is_hide_system_groups=False)
    
    grant_group = await DomoGroup.search_by_name(auth =self.group.auth , group_name = 'Grant: Manage all groups')
       
    await self.add_owners(add_owner_ls = [grant_group])

    await DomoGroups.toggle_system_group_visibility(auth = self.group.auth, is_hide_system_groups=True)

# %% ../../nbs/classes/50_DomoGroup.ipynb 52
@patch_to(DomoGroup, cls_method=True)
async def create_from_name(
    cls: DomoGroup,
    auth: dmda.DomoAuth,
    group_name: str = None,
    group_type: str = "open",  # use GroupType_Enum
    description: str = None,
    is_include_manage_groups_role: bool = True,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):

    res = await group_routes.create_group(
        auth=auth,
        group_name=group_name,
        group_type=group_type,
        description=description,
        debug_api=debug_api,
    )

    
    domo_group = cls._from_group_json(auth=auth, json_obj=res.response)

    await domo_group.Membership.add_owner_manage_groups_role()

    return domo_group


# %% ../../nbs/classes/50_DomoGroup.ipynb 56
@patch_to(DomoGroup)
async def update_metadata(
    self: DomoGroup,
    auth: dmda.DomoAuth = None,

    group_name: str = None,
    group_type: str = None,  # use GroupType_Enum
    description: str = None,
    debug_api: bool = False,
    return_raw: bool = False,
    session: httpx.AsyncClient = None,
):
    auth = auth or self.auth
    
    res = await group_routes.update_group(
        auth=auth,
        group_id = self.id,
        group_name = group_name,
        group_type = group_type,
        description = description,
        debug_api = debug_api,
        session = session)

    if return_raw:
        return res
    
    updated_group = await DomoGroup.get_by_id(auth = auth, group_id = self.id )
    

    self.name = updated_group.name or self.name
    self.description = updated_group.description or self.description
    self.type = updated_group.type or self.type

    return self

# %% ../../nbs/classes/50_DomoGroup.ipynb 61
@patch_to(DomoGroup, cls_method=True)
async def upsert(
    cls: DomoGroup,
    auth: dmda.DomoAuth,
    group_name: str,
    group_type: str = None, # if create_group, use routes.class.GroupType_Enum
    description: str = None,
    debug_api: bool = False,
    debug_prn: bool = False,
    session: httpx.AsyncClient = None,
):

    try:
        res = await group_routes.search_groups_by_name(
            auth=auth,
            search_name=group_name,
            debug_api=debug_api,
            is_exact_match=True,
            session=session,
        )

        domo_group = cls._from_group_json(auth=auth, json_obj=res.response)
        
        return await domo_group.update_metadata(
            group_type = group_type,
            description = description,
            debug_api = debug_api)

    except group_routes.SearchGroups_Error as e:
        
        return await DomoGroup.create_from_name(
                auth=auth, 
                group_name=group_name, 
                group_type = group_type,
                description = description,
                debug_api=debug_api, session=session)

        return e
