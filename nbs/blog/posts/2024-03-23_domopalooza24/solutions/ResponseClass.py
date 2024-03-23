from dataclasses import dataclass
import requests


@dataclass
class ResponseClass:
    status: int
    is_success: bool
    response: dict

    @classmethod
    def from_request_response(cls, res: requests.models.Response):

        is_success = res.ok

        response = res.json()

        if not is_success:
            response = response["message"]

        return cls(
            status=res.status_code,
            is_success=is_success,
            response=response,
        )
