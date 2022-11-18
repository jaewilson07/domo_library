from dataclasses import dataclass, field

from Library.utils.DictDot import DictDot
from Library.DomoClasses.DomoAuth import DomoFullAuth
from Library.DomoClasses.routes import grant_routes


@dataclass
class DomoGrant:
    id: str
    display_group: str
    depends_on: [str]
    title: str
    description: str = None
    role_membership: [str] = None

    @classmethod
    def _from_json(cls, obj):
        dd = DictDot(obj)

        return cls(id=dd.authority,
                   display_group=dd.authorityUIGroup,
                   depends_on=dd.dependsOnAuthorities,
                   title=dd.title,
                   description=dd.description,
                   role_membership=[str(role) for role in dd.roleIds])
