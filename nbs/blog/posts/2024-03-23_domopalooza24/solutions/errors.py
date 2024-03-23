class DomoAPIRequest_Error(Exception):
    """a customized Exception class for handing Domo errors"""

    def __init__(self, message):
        super().__init__(message)
