class AuthRequiredException(Exception):
    def __init__(self, message="Must include Auth Object"):
        self.message = message


class InvalidCredentialsError(Exception):
    def __init__(self, status, message="invalid credentials"):
        self.message = f"Status {status} - {message}" or message


class InvalidInstanceError(Exception):
    def __init__(self, message="invalid instance"):
        self.message = message





class NoDataReturned(Exception):
    def __init__(self, message="invalid dataset", domo_instance=None, dataset_id=None):

        if dataset_id:
            message = f"{message} - {dataset_id}"

        if domo_instance:
            message = f"{message} in {domo_instance}"

        self.message = message


class ResourceUnavailable(Exception):
    """Exception representing a failed request to a resource"""

    def __init__(self, msg, http_response):
        Exception.__init__(self)
        self._msg = msg
        self._status = http_response.status

    def __str__(self):
        return "%s (HTTP status: %s)" % (self._msg, self._status)


class Unauthorized(ResourceUnavailable):
    pass


class TokenError(Exception):
    pass
