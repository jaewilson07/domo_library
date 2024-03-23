import requests


def get_accounts(
    domo_instance,
    headers: dict = None,
    session_token: str = None,
    debug_api: bool = False,
):

    headers = headers or {}

    if session_token:
        headers.update({"x-domo-authentication": session_token})

    url = f"https://{domo_instance}.domo.com/api/data/v2/datasources/providers"

    if debug_api:
        print({"headers": headers, "url": url})

    return requests.request(method="GET", url=url, headers=headers)
