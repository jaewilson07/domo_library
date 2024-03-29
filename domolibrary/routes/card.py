# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/card.ipynb.

# %% auto 0
__all__ = ['CardSearch_NotFoundError', 'get_kpi_definition', 'get_card_metadata', 'generate_body_search_cards_admin_summary',
           'search_cards_admin_summary']

# %% ../../nbs/routes/card.ipynb 2
from typing import List

import httpx

import domolibrary.client.get_data as gd
import domolibrary.client.ResponseGetData as rgd
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de


# %% ../../nbs/routes/card.ipynb 4
class CardSearch_NotFoundError(de.DomoError):
    def __init__(
        self,
        card_id,
        domo_instance,
        function_name,
        status,
        parent_class: str = None,
        message=None,
    ):
        super().__init__(
            status=status,
            message=f"card {card_id} not found",
            domo_instance=domo_instance,
            function_name=function_name,
            parent_class=parent_class,
        )

# %% ../../nbs/routes/card.ipynb 5
@gd.route_function
async def get_kpi_definition(
    auth: dmda.DomoAuth,
    card_id: str,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    parent_class: str = None,
    debug_num_stacks_to_drop=1,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/content/v3/cards/kpi/definition"

    body = {"urn": card_id}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if not res.is_success and res.response == "Not Found":
        raise CardSearch_NotFoundError(
            card_id=card_id,
            status=res.status,
            domo_instance=auth.domo_instance,
            function_name="get_kpi_definition",
        )

    return res

# %% ../../nbs/routes/card.ipynb 8
@gd.route_function
async def get_card_metadata(
    auth: dmda.DomoAuth,
    card_id: str,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    parent_class: str = None,
    debug_num_stacks_to_drop=1,
) -> rgd.ResponseGetData:
    optional_params = "metadata,certification,datasources,owners,problems"

    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/cards?urns={card_id}&parts={optional_params}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if res.is_success and len(res.response) == 0:
        raise CardSearch_NotFoundError(
            card_id=card_id,
            status=res.status,
            domo_instance=auth.domo_instance,
            parent_class=parent_class,
            function_name=res.traceback_details.function_name,
        )

    res.response = res.response[0]

    return res

# %% ../../nbs/routes/card.ipynb 11
def generate_body_search_cards_admin_summary(
    page_ids: List[str] = None,
    #  searchPages: bool = True,
    card_search_text: str = None,
    page_search_text: str = None,
) -> dict:
    body = {"ascending": True, "orderBy": "cardTitle"}

    if card_search_text:
        body.update(
            {"cardTitleSearchText": card_search_text, "includeCardTitleClause": True}
        )

    if page_search_text:
        body.update(
            {
                "pageTitleSearchText": page_search_text,
                "includePageTitleClause": True,
                "notOnPage": False,
            }
        )

    if page_ids:
        body.update({"pageIds": page_ids})

    return body

# %% ../../nbs/routes/card.ipynb 12
@gd.route_function
async def search_cards_admin_summary(
    auth: dmda.DomoAuth,
    body: dict,
    maximum: int = None,
    debug_api: bool = False,
    debug_loop: bool = False,
    session: httpx.AsyncClient = None,
    wait_sleep: int = 3,
    parent_class: str = None,
    debug_num_stacks_to_drop: int = 1,
) -> rgd.ResponseGetData:
    limit = 100
    offset = 0
    loop_until_end = False if maximum else True

    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/cards/adminsummary?skip={offset}&limit={limit}"

    offset_params = {
        "offset": "skip",
        "limit": "limit",
    }

    def arr_fn(res):
        return res.response.get("cardAdminSummaries")

    res = await gd.looper(
        auth=auth,
        method="POST",
        url=url,
        arr_fn=arr_fn,
        offset_params=offset_params,
        limit=limit,
        skip=offset,
        body=body,
        maximum=maximum,
        session=session,
        debug_api=debug_api,
        debug_loop=debug_loop,
        loop_until_end=loop_until_end,
        wait_sleep=wait_sleep,
        parent_class=parent_class,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
    )
    return res
