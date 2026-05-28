from ._enum_compat import StrEnum


class Direction(StrEnum):
    CLIENT_TO_SERVER = 'client_to_server'
    SERVER_TO_CLIENT = 'server_to_client'
    APP_TO_SERVER = 'app_to_server'
    SERVER_TO_APP = 'server_to_app'
    SYSTEM = 'system'
