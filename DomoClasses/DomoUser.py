from dataclasses import dataclass, field
from typing import List

from ..utils.Base import Base
from ..utils.DictDot import DictDot
from . import DomoAuth as dmda
from .routes import user_routes


class DomoUsers:
    def __init__(self, user):
        self.user = user

    @staticmethod
    def util_match_domo_users_to_emails(domo_users: list, user_email_list: List[str]) -> list:
        """pass in an array of user emails to match against an array of Domo User"""

        matches = []
        for idx, email in enumerate(user_email_list):
            matchUsr = next((domo_usr for domo_usr in domo_users if email.lower() == domo_usr.email_address.lower()),
                            None)
            if matchUsr is not None:
                matches.append(matchUsr)
        return matches

    def _users_to_domo_user(json_list, full_auth: dmda.DomoFullAuth):
        domo_users = []
        for json_obj in json_list:
            user = DomoUser._from_search_json(
                full_auth=full_auth,
                json_obj=json_obj)
            domo_users.append(user)

        return domo_users

    def _users_to_virtual_user(json_list, full_auth: dmda.DomoFullAuth):
        domo_users = []
        for json_obj in json_list:
            user = DomoUser._from_virtual_json(
                full_auth=full_auth,
                json_obj=json_obj)
            domo_users.append(user)

        return domo_users

    @classmethod
    async def all_users(cls, full_auth: dmda.DomoFullAuth, log_results: bool = False):

        res = await user_routes.get_all_users(full_auth=full_auth, log_results=log_results)

        if res.status == 200:
            json_list = res.response
            return cls._users_to_domo_user(json_list=json_list, full_auth=full_auth)

    @classmethod
    async def by_id(cls, user_ids: list[str],
                    full_auth: dmda.DomoFullAuth,
                    only_allow_one: bool = True,
                    log_results: bool = False, debug: bool = False) -> list:

        body = user_routes.generate_search_users_body_by_id(user_ids)
        res = await user_routes.search_users(full_auth=full_auth, body=body, log_results=log_results, debug=debug)

        if res.status == 200:
            json_list = res.response.get('users')

            if not json_list:
                return None

            domo_users = cls._users_to_domo_user(
                json_list, full_auth=full_auth)

            if only_allow_one:
                return domo_users[0]

            return domo_users

    @classmethod
    async def by_email(cls, email_address: str, full_auth: dmda.DomoFullAuth,
                       only_allow_one: bool = True,
                       log_results: bool = False, debug: bool = False) -> list:

        body = user_routes.generate_search_users_body_by_email(email_address)
        res = await user_routes.search_users(full_auth=full_auth, body=body, log_results=log_results, debug=debug)

        if res.status == 200:
            json_list = res.response.get('users')

            if not json_list:
                return None

            domo_users = cls._users_to_domo_user(
                json_list, full_auth=full_auth)

            if only_allow_one:
                domo_users = cls.util_match_domo_users_to_emails(
                    domo_users, [email_address])
                return domo_users[0]

            return domo_users

        return None

    @classmethod
    async def virtual_user_by_subscriber_instance(cls,
                                                  subscriber_instance: str,
                                                  full_auth: dmda.DomoFullAuth,
                                                  debug: bool = False, log_results: bool = False
                                                  ):
        res = await user_routes.search_virtual_user_by_subscriber_instance(full_auth=full_auth,
                                                                           subscriber_instance=subscriber_instance,
                                                                           log_results=log_results, debug=debug)

        if res.status != 200:
            return None

        json_list = res.response
        
        if debug:
            print (json_list)

        if not json_list:
            return None

        domo_users = cls._users_to_virtual_user(json_list, full_auth=full_auth)
        return domo_users[0]


@dataclass
class DomoUser(Base):
    id: str
    domo_instance: str
    full_auth: dmda.DomoFullAuth = field(repr=False)
    display_name: str = None
    email_address: str = None

    publisher_domain: str = None
    subscriber_domain: str = None
    virtual_user_id: str = None

    def __post_init__(self):
        Base().__init__()

    @classmethod
    def _from_search_json(cls, full_auth, json_obj):
        dd = DictDot(json_obj)

        u = cls(
            domo_instance=full_auth.domo_instance,
            full_auth=full_auth,
            id=dd.id or dd.userId,
            display_name=dd.displayName,
            email_address=dd.emailAddress
        )
        return u

    @classmethod
    def _from_virtual_json(cls, full_auth, json_obj):
        dd = DictDot(json_obj)

        u = cls(
            domo_instance=full_auth.domo_instance,
            full_auth=full_auth,
            id=dd.id,
            publisher_domain=dd.publisherDomain,
            subscriber_domain=dd.subscriberDomain,
            virtual_user_id=dd.virtualUserId
        )
        return u

    async def reset_password(self, new_password: str, debug: bool = False, log_results: bool = False):

        res = await user_routes.reset_password(full_auth=self.full_auth, user_id=self.id, new_password=new_password,
                                               debug=debug, log_results=log_results)

        return res

    @classmethod
    async def request_password_reset(cls, domo_instance: str, email: str, locale: str = 'en-us', debug: bool = False):

        return await user_routes.request_password_reset(domo_instance=domo_instance, email=email, locale=locale,
                                                        debug=debug)

    @classmethod
    async def create_user(cls, full_auth: dmda.DomoFullAuth, display_name, email, role_id, password: str = None,
                          send_password_reset_email: bool = False,
                          debug: bool = False, log_results: bool = False):

        res = await user_routes.create_user(full_auth=full_auth, display_name=display_name, email=email,
                                            role_id=role_id, debug=debug, log_results=log_results)

        if debug:
            print(res)

        if res.status != 200:
            return None

        dd = DictDot(res.response)
        u = cls(domo_instance=full_auth.domo_instance,
                full_auth=full_auth,
                id=dd.id or dd.userId,
                display_name=dd.displayName,
                email_address=dd.emailAddress)

        if password:
            await u.reset_password(new_password=password)

        if send_password_reset_email:
            await u.request_password_reset(domo_instance=full_auth.domo_instance,
                                           email=u.email_address)

        return u
    
    async def set_user_landing_page(self, 
                                    page_id:str,
                                    user_id: str = None,
                                    full_auth : dmda.DomoFullAuth = None,
                                   debug:bool = False):

        res = await user_routes.set_user_landing_page(full_auth = full_auth or self.full_auth, page_id = page_id, 
                                                      user_id = self.id or user_id , debug = debug)

        if res.status != 200:
            return False

        return True
            
