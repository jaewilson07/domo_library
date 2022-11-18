from dataclasses import dataclass, field

from .routes import card_routes
from .DomoAuth import DomoDeveloperAuth, DomoFullAuth
from ..utils.DictDot import DictDot
from ..utils.Base import Base


@dataclass
class DomoCard(Base):
    id: str
    full_auth: DomoFullAuth = field(repr=False)
    title: str = None
    description: str = None
    type: str = None
    urn: str = None
    chart_type: str = None
    dataset_id: str = None
    certification: field(default_factory=dict) = None
    owner_members: field(default_factory=list) = None

    def __post_init__(self):
        Base().__init__()

        self.domo_instance = self.full_auth.domo_instance
        # self.Definition = CardDefinition(self)

    def display_url(self) -> str:
        return f'https://{self.domo_instance}.domo.com/kpis/details/{self.id}'

    @classmethod
    async def get_from_id(cls, id: str, full_auth: DomoFullAuth, debug: bool = False):
        res = await card_routes.get_card_metadata(full_auth=full_auth, card_id=id, debug=debug)

        if res.status == 200:
            dd = DictDot(res.response[0])

            card = cls(
                full_auth=full_auth,
                id=dd.id,
                title=dd.title,
                description=dd.description,
                type=dd.type,
                urn=dd.urn,
                certification=dd.certification,
                owner_members=dd.owners,
                chart_type=dd.metadata.chartType
            )

            if dd.datasources:
                card.dataset_id = dd.datasources[0].dataSourceId

            return card
