from enum import Enum

class PluginType (Enum):
    CLIENT = auto()
    HOST = auto()
    CLIENT_HOST = auto()
    DISABLED = auto()

class PluginManager:
    NAME = "NONE"
    SHORTNAME = "NAN"
    TYPE = PluginType.DISABLED

    dependencies = dict()
    serverDetails = dict()
    isInServer = False
    isConnectedToServer = False

    #
    # "Private/Internal" methods
    #

    def __init__(self, isServer: bool):
        pass

    # Decorator
    def server_method():
        pass

    def request_server(self, request: dict) -> dict:
        pass

    def handle_request(self, request: dict) -> dict:
        pass

    def init_dependencies(self, daemonRef, plugins):
        pass

    #
    # "Plugin" methods
    #

    def init(self, daemonRef, plugins):
        pass

    def hostcli(self, args: dict):
        pass

    def hostcli_init(self, cmd_p, plugin_p):
        pass

    #
    # "Server" methods
    #

    @server_method
    def getStatus(self):
        pass

    @server_method
    def start(self):
        pass

    @server_method
    def stop(self):
        pass

    @server_method
    def connect(self):
        pass

    @server_method
    def disconnect(self):
        pass


