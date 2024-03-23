import requests
from .errors import DomoAPIRequest_Error


def get_full_auth(
    domo_instance: str, domo_username: str, domo_password: str
) -> str:  # returns a session token
    """use username and password to generate an access token"""

    url = f"https://{domo_instance}.domo.com/api/content/v2/authentication"

    body = {
        "method": "password",
        "emailAddress": domo_username,
        "password": domo_password,
    }

    res = requests.request(method="POST", url=url, json=body)
    data = res.json()

    token = data.get("sessionToken")

    if not token:
        raise DomoAPIRequest_Error("unable to retrieve a session token")

    return token
