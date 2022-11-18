import aiohttp

from ..utils.DictDot import DictDot
from dataclasses import dataclass, field

from Library.DomoClasses.DomoAuth import DomoFullAuth
from .routes import role_routes


@dataclass
class DomoRole:
    full_auth: DomoFullAuth

    id: str
    name: str = None
    description: str = None
    is_system_role: int = None

    grant_list: list[str] = field(default_factory=list)
    membership_list: list = field(default_factory=list)

    @classmethod
    def _from_str(cls, id, name, description=None, full_auth: DomoFullAuth = None):

        return cls(id=id,
                   name=name,
                   description=description,
                   full_auth=full_auth,
                   is_system_role=1 if id <= 5 else 0
                   )

    async def get_membership(self, full_auth: DomoFullAuth = None,
                             role_id=None, debug: bool = False, session: aiohttp.ClientSession = None):

        res = await role_routes.get_role_membership(full_auth=full_auth or self.full_auth,
                                                    role_id=role_id or self.id,
                                                    debug=debug, session=session)
        if res.status == 200:
            self.membership_list = res.response.get('users')

            return {'status': res.status,
                    'users': res.response.get('users')}

    @classmethod
    async def create_role(cls,
                          full_auth: DomoFullAuth,
                          name: str,
                          description: str = None,
                          debug: bool = False):

        res = await role_routes.create_role(full_auth=full_auth,
                                            name=name,
                                            description=description,
                                            debug=debug)
        if debug:
            print(res)

        if res.status == 200:
            return cls._from_str(id=res.response.get('id'),
                                 name=res.response.get('name'),
                                 description=res.response.get('description'),
                                 full_auth=full_auth)
        return None

    async def update_role_grants(self,
                                 grant_list: list[str],
                                 role_id: str = None,
                                 full_auth: DomoFullAuth = None,
                                 debug: bool = False):

        res = await role_routes.update_role_grants(full_auth=full_auth or self.full_auth,
                                                   role_id=role_id or self.id,
                                                   role_grant_list=grant_list,
                                                   debug=debug)

        if res.status == 200 or res.status == 204:
            res_roles = await role_routes.get_role_grants(full_auth or self.full_auth,
                                                          role_id=role_id or self.id,
                                                          debug=debug)
            return {'status': res.status,
                    'role_id': role_id or self.id,
                    'grants': res_roles.response
                    }

    async def add_user(self, user_list: list[str],
                       role_id: str = None,
                       full_auth: DomoFullAuth = None, debug: bool = False):

        res = await role_routes.role_membership_add_user(full_auth=full_auth or self.full_auth,
                                                         role_id=role_id or self.id,
                                                         user_list=user_list,
                                                         debug=debug)
        if res.status == 204:
            res_membership = await role_routes.get_role_membership(full_auth=full_auth or self.full_auth,
                                                                   role_id=role_id or self.id,
                                                                   debug=debug)

            return {'status': res.status,
                    'users': res_membership.response.get('users')}

        return res

    async def set_as_default_role(self, debug: bool = False):
        return await role_routes.set_default_role(full_auth=self.full_auth,
                                                  role_id=self.id,
                                                  debug=debug)
