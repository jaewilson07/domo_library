from typing import List

import aiohttp

from ...utils.ResponseGetData import ResponseGetData
from ..DomoAuth import DomoFullAuth
from .get_data import get_data


async def get_kpi_definition(full_auth: DomoFullAuth, card_id: str, debug: bool = False) -> ResponseGetData:
    url = f"https://{full_auth.domo_instance}.domo.com/api/content/v3/cards/kpi/definition"

    body = {"urn": card_id}

    res = await get_data(
        auth=full_auth,
        url=url,
        method='PUT',
        body=body,
        debug=False
    )

    return res


async def get_card_metadata(full_auth: DomoFullAuth, card_id: str, debug: bool = False) -> ResponseGetData:
    optional_params = "metadata,certification,datasources,owners,problems"
    url = f"https://{full_auth.domo_instance}.domo.com/api/content/v1/cards?urns={card_id}&parts={optional_params}"

    res = await get_data(
        auth=full_auth,
        url=url,
        method='GET',
        debug=False
    )

    return res


def generate_body_search_cards_admin_summary(page_ids: List[str] = None,
                                             searchPages: bool = True,
                                             cardSearchText: str = '',
                                             pageSearchText: str = '') -> dict:
    body = {
        # "includeCardCertificationClause": false,
        # "cardCertification": [
        #     {
        #         "state": "CERTIFIED"
        #     }
        # ],
        "includeCardTitleClause": True if cardSearchText else False,
        "includePageTitleClause": True if pageSearchText else False,
        "notOnPage": False,
        "ascending": True,
        "orderBy": "cardTitle"
    }

    if cardSearchText:
        body.update({'cardTitleSearchText': cardSearchText})

    if pageSearchText:
        body.update({'pageTitleSearchText': pageSearchText})

    if page_ids:
        body.update({'pageIds': page_ids})

    return body


async def search_cards_admin_summary(full_auth: DomoFullAuth,
                                     body: dict,
                                     limit: int = 100,
                                     offset: int = 0,
                                     debug: bool = False,
                                     log_results: bool = False
                                     ) -> ResponseGetData:
    url = f'https://{full_auth.domo_instance}.domo.com/api/content/v2/cards/adminsummary?skip={offset}&limit={limit}'

    res = await get_data(
        auth=full_auth,
        url=url,
        body=body,
        method='POST',
        debug=debug,
        log_results=log_results
    )

    return res
