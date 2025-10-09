from enum import StrEnum


class ReturnTypes(StrEnum):
    UserNotAuthenticated = "User Not Authenticated"
    UserDataNotFound = "User Data Not Found"


# CUSTOM ERRORS
class DatabaseError(Exception):
    pass


class SpotifyAPIError(Exception):
    pass


class SpotifyClientNotAuthenticated(Exception):
    pass
