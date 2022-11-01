import aiohttp
from dataclasses import field, dataclass

from .DomoAuth import DomoFullAuth
from .routes import appdb_routes
from ..utils.Base import Base


@dataclass
class AppdbDocument:
    content: field(default_factory=dict)
    collection_id: str = None
    document_id: str = None

    document_body: field(default_factory=dict) = None

    def __post_init__(self):
        self.generate_doc_body()

    def generate_doc_body(self):
        body = {
            'content': self.content
        }

        self.document_body = body
        return body


@dataclass
class DomoAppDbCollection:
    app_id: str
    domo_environment: str
    collection_name: str
    full_auth: DomoFullAuth

    async def get_documents(self):
        res = await appdb_routes.get_documents(full_auth=self.full_auth,
                                               app_id=self.app_id,
                                               domo_environment=self.domo_environment,
                                               collection_name=self.collection_name)

        if res.status == 200:
            return res.response

    async def create_document(self, content: dict, session: aiohttp.ClientSession = None, debug: bool = False):
        appdb_document = AppdbDocument(content=content)

        res = await appdb_routes.create_document(full_auth=self.full_auth,
                                                 app_id=self.app_id,
                                                 domo_environment=self.domo_environment,
                                                 collection_name=self.collection_name,
                                                 document=appdb_document.document_body,
                                                 session=session,
                                                 debug=debug)
        # if debug:
        print(res)
        if res == 200:
            return res.response
