# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoRole.ipynb.

# %% auto 0
__all__ = ['DomoRole', 'SetRoleGrants_MissingGrants', 'AddUser_Error', 'DeleteRole_Error', 'DomoRoles', 'SearchRole_NotFound',
           'CreateRole_Error']

# %% ../../nbs/classes/50_DomoRole.ipynb 2
from dataclasses import dataclass, field
import httpx
import asyncio

from nbdev.showdoc import patch_to

import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de

import domolibrary.utils.DictDot as util_dd
import domolibrary.routes.role as role_routes

import domolibrary.classes.DomoUser as dmu
import domolibrary.classes.DomoGrant as dmg

# %% ../../nbs/classes/50_DomoRole.ipynb 3
@dataclass
class DomoRole:
    auth: dmda.DomoAuth = field(repr=False)

    id: str
    name: str = None
    description: str = None
    is_system_role: bool = False
    is_default_role: bool = False

    grant_ls: [dmg.DomoGrant] = field(default_factory=list)
    membership_ls: list = field(default_factory=list)

    def __post_init__(self):
        self.is_system_role = True if self.id <= 5 else 0

        if self.grant_ls:
            self.grant_ls = self._valid_grant_ls(self.grant_ls)

    @staticmethod
    def _valid_grant_ls(grant_ls) -> [dmg.DomoGrant]:
        if isinstance(grant_ls[0], str):
            return [dmg.DomoGrant(grant_str) for grant_str in grant_ls]

        elif isinstance(grant_ls[0], dmg.DomoGrant):
            return grant_ls

    # @classmethod
    # def _from_str(cls, id, name, description=None, auth: DomoAuth = None):

    #     return cls(id=id,
    #             name=name,
    #             description=description,
    #             auth=auth
    #             )

    @classmethod
    def _from_json(cls, obj, auth=dmda.DomoAuth, is_default_role=None):
        dd = obj
        if not isinstance(dd, util_dd.DictDot):
            dd = util_dd.DictDot(obj)

        return cls(
            id=dd.id,
            name=dd.name,
            description=dd.description,
            auth=auth,
            is_default_role=is_default_role,
        )

# %% ../../nbs/classes/50_DomoRole.ipynb 4
@patch_to(DomoRole, cls_method=True)
async def get_by_id(
    cls: DomoRole,
    role_id: int,
    auth: dmda.DomoAuth,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    return_raw: bool = False,
):
    res = await role_routes.get_role_by_id(
        role_id=role_id,
        auth=auth,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
        parent_class=cls.__name__,
    )

    if return_raw:
        return res.response

    return cls._from_json(res.response, auth=auth)

# %% ../../nbs/classes/50_DomoRole.ipynb 8
@patch_to(DomoRole)
async def get_grants(
    self: DomoRole,
    auth: dmda.DomoAuth = None,
    role_id: str = None,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):
    auth = auth or self.auth
    role_id = role_id or self.id
    res = await role_routes.get_role_grants(
        auth=auth,
        role_id=role_id,
        debug_api=debug_api,
        session=session,
        parent_class=self.__class__.__name__,
    )

    if return_raw:
        return res

    self.grant_ls = [dmg.DomoGrant(obj) for obj in res.response]

    return self.grant_ls

# %% ../../nbs/classes/50_DomoRole.ipynb 11
class SetRoleGrants_MissingGrants(de.DomoError):
    def __init__(self, role_id, missing_grants: [str], domo_instance):
        super().__init__(
            domo_instance=domo_instance,
            entity_id=role_id,
            message=f"failed to add grants: {', '.join(missing_grants)}",
        )

# %% ../../nbs/classes/50_DomoRole.ipynb 12
@patch_to(DomoRole)
async def set_grants(
    self: DomoRole,
    grant_ls: list[dmg.DomoGrant],
    role_id: str = None,
    auth: dmda.DomoAuth = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: bool = 2,
    session: httpx.AsyncClient = None,
):
    auth = auth or self.auth
    role_id = role_id or self.id

    domo_grants = self._valid_grant_ls(grant_ls)

    # dmic = dic.DomoInstanceConfig(auth = auth)
    # all_grants = await dmic.get_grants()

    # filtered_grant_ls = []

    # for domo_grant in all_grants:
    #     if domo_grant.id in grant_ls:
    #         filtered_grant_ls.append(domo_grant.id)

    #         if domo_grant.depends_on_ls:
    #             for parent_grant_id in domo_grant.depends_on_ls:
    #                 match_grant = next(( domo_grant for domo_grant in all_grants if parent_grant_id == domo_grant.id ))
    #                 if match_grant:
    #                     filtered_grant_ls.append(match_grant.id)

    # set grants
    res = await role_routes.set_role_grants(
        auth=auth,
        role_id=role_id,
        role_grant_ls=[domo_grant.id for domo_grant in domo_grants],
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
        parent_class=self.__class__.__name__,
    )

    # validate grants
    await asyncio.sleep(2)

    all_grants = await self.get_grants(auth=auth, debug_api=debug_api, session=session)

    missing_grants = [grant.id for grant in domo_grants if grant not in all_grants]

    if missing_grants:
        raise SetRoleGrants_MissingGrants(
            role_id=role_id,
            missing_grants=missing_grants,
            domo_instance=auth.domo_instance,
        )

    return domo_grants

# %% ../../nbs/classes/50_DomoRole.ipynb 16
@patch_to(DomoRole)
async def get_membership(
    self,
    role_id=None,
    auth: dmda.DomoAuth = None,
    return_raw: bool = False,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):
    auth = auth or self.auth
    role_id = role_id or self.id

    res = await role_routes.get_role_membership(
        auth=auth, role_id=role_id, debug_api=debug_api, session=session
    )

    if return_raw:
        return res.response

    membership_ls = [
        dmu.DomoUser._from_search_json(user_obj=obj, auth=auth) for obj in res.response
    ]

    self.membership_ls = membership_ls

    return membership_ls

# %% ../../nbs/classes/50_DomoRole.ipynb 19
class AddUser_Error(de.DomoError):
    def __init__(self, role_id, domo_instance, user_id, user_name=None):
        user_str = f"{user_id} - {user_name}" if user_name else user_id
        super().__init__(
            domo_instance=domo_instance,
            message=f"unable to add {user_str} to role {role_id}",
        )

# %% ../../nbs/classes/50_DomoRole.ipynb 20
@patch_to(DomoRole)
async def add_user(
    self,
    user: dmu.DomoUser,
    role_id: str = None,
    auth: dmda.DomoAuth = None,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):
    role_id = role_id or self.id
    auth = auth or self.auth

    await role_routes.role_membership_add_users(
        auth=auth,
        role_id=role_id,
        user_list=[user.id],
        debug_api=debug_api,
        session=session,
    )

    domo_members = await self.get_membership(
        auth=auth or self.auth, role_id=role_id or self.id, debug_api=debug_api
    )
    self.membership_ls = domo_members

    if user not in domo_members:
        raise AddUser_Error(
            role_id=role_id,
            domo_instance=auth.domo_instance,
            user_id=user.id,
            user_name=user.display_name,
        )

    return domo_members

# %% ../../nbs/classes/50_DomoRole.ipynb 24
@patch_to(DomoRole)
async def update_role_metadata(
    self: DomoRole,
    auth: dmda.DomoAuth = None,
    role_name=None,
    role_description: str = None,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):
    auth = auth or self.auth
    role_name = role_name or self.name

    res = await role_routes.update_role_metadata(
        role_id=self.id,
        role_name=role_name,
        role_description=role_description or self.description,
        auth=auth,
        debug_api=debug_api,
        session=session,
    )

    if return_raw:
        return res

    role_ls = await role_routes.get_roles(auth=auth)

    domo_role = next(
        (
            DomoRole._from_json(role, auth=auth)
            for role in role_ls.response
            if role.get("name") == role_name
        ),
        None,
    )

    return domo_role

# %% ../../nbs/classes/50_DomoRole.ipynb 28
class DeleteRole_Error(de.DomoError):
    def __init__(self, role_id, domo_instance):
        super().__init__(
            message=f"role: {role_id} not found", domo_instance=domo_instance
        )

# %% ../../nbs/classes/50_DomoRole.ipynb 29
@patch_to(DomoRole, cls_method=True)
async def delete_role(
    cls: DomoRole,
    role_id: int,
    auth: dmda.DomoAuth = None,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):
    domo_res = await role_routes.get_roles(auth=auth)

    domo_role = next(
        (role for role in domo_res.response if role.get("id") == role_id), None
    )

    if not domo_role:
        raise DeleteRole_Error(role_id=role_id, domo_instance=auth.domo_instance)

    return await role_routes.delete_role(
        role_id=role_id, auth=auth, debug_api=debug_api, session=session
    )

# %% ../../nbs/classes/50_DomoRole.ipynb 33
@dataclass
class DomoRoles:
    auth: dmda.DomoAuth

# %% ../../nbs/classes/50_DomoRole.ipynb 34
@patch_to(DomoRoles, cls_method=True)
async def get_roles(
    cls: DomoRoles,
    auth: dmda.DomoAuth,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):
    res = await role_routes.get_roles(auth=auth, session=session, debug_api=debug_api)

    if return_raw:
        return res

    default_role_res = await role_routes.get_default_role(
        auth=auth, session=session, debug_api=debug_api
    )

    return [
        DomoRole._from_json(
            role,
            auth,
            is_default_role=str(default_role_res.response) == str(role.get("id")),
        )
        for role in res.response
    ]

# %% ../../nbs/classes/50_DomoRole.ipynb 37
class SearchRole_NotFound(de.DomoError):
    def __init__(
        self, domo_instance, role_id, message="not found", function_name="search_role"
    ):
        super().__init__(
            domo_instance=domo_instance,
            message=message,
            entity_id=role_id,
            function_name=function_name,
        )

# %% ../../nbs/classes/50_DomoRole.ipynb 38
@patch_to(DomoRoles, cls_method=True)
async def search_role(
    cls: DomoRoles,
    auth: dmda.DomoAuth,
    role_name: str = None,
    role_id: str = None,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):
    all_roles = await DomoRoles.get_roles(
        auth=auth, debug_api=debug_api, session=session, return_raw=return_raw
    )

    if return_raw:
        return all_roles

    if role_name:
        domo_role = next((role for role in all_roles if role.name == role_name), None)

    if role_id:
        domo_role = next(
            (role for role in all_roles if str(role.id) == str(role_id)), None
        )

    if not domo_role:
        raise SearchRole_NotFound(domo_instance=auth.domo_instance, role_id=role_name)

    return domo_role

# %% ../../nbs/classes/50_DomoRole.ipynb 42
class CreateRole_Error(de.DomoError):
    def __init__(
        self, domo_instance, role_id, message, status, function_name="create_role"
    ):
        super().__init__(
            domo_instance=domo_instance,
            message=message,
            status=status,
            entity_id=role_id,
            function_name=function_name,
        )

# %% ../../nbs/classes/50_DomoRole.ipynb 43
@patch_to(DomoRoles, cls_method=True)
async def create_role(
    cls: DomoRoles,
    auth: dmda.DomoAuth,
    name: str,
    description: str = None,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):
    res = await role_routes.create_role(
        auth=auth,
        name=name,
        description=description,
        debug_api=debug_api,
        session=session,
    )

    if not res.is_success:
        role_res = await cls.get_roles(auth=auth)

        domo_role = next((role for role in role_res if role.name == name))

        if domo_role:
            raise CreateRole_Error(
                domo_instance=auth.domo_instance,
                role_id=name,
                message="role already exists",
                status=res.status,
            )

        raise CreateRole_Error(
            domo_instance=auth.domo_instance,
            role_id=name,
            message=res.response,
            status=res.status,
        )

    return await DomoRoles.search_role(auth=auth, role_name=name)

# %% ../../nbs/classes/50_DomoRole.ipynb 46
@patch_to(DomoRoles, cls_method=True)
async def upsert_role(
    cls: DomoRoles,
    auth: dmda.DomoAuth,
    name: str,
    description: str = None,
    grant_ls: [dmg.DomoGrant] = None,
    debug_api: bool = False,
    debug_prn: bool = False,
    session: httpx.AsyncClient = None,
):
    domo_role = None

    try:
        domo_role = await DomoRoles.search_role(
            role_name=name,
            auth=auth,
            debug_api=debug_api,
            session=session,
        )

        if domo_role:
            await domo_role.update_role_metadata(
                role_name=name, role_description=description, session=session
            )

    except SearchRole_NotFound as e:
        if debug_prn:
            print(f"No role match -- creating new role in {auth.domo_instance} - {e}")

        domo_role = await DomoRoles.create_role(
            auth=auth,
            name=name,
            description=description,
            debug_api=debug_api,
            session=session,
        )

    if grant_ls:
        grant_ls = domo_role._valid_grant_ls(grant_ls)
        await domo_role.set_grants(grant_ls=grant_ls)

    return domo_role

# %% ../../nbs/classes/50_DomoRole.ipynb 50
@patch_to(DomoRole)
async def set_as_default_role(
    self: DomoRole, debug_api: bool = False, session: httpx.AsyncClient = None
):
    return await role_routes.set_default_role(
        auth=self.auth, role_id=self.id, debug_api=debug_api, session=session
    )
