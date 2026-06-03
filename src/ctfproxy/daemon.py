
from .plugins import ALL_PLUGINS, PluginType, PluginManager,  filterPlugins

class CPDaemon:
    TYPE = PluginType.DISABLED
    plugins: list[PluginManager] = []

    #
    # Cli
    #

    @staticmethod
    def ensure(type: PluginType):
        pass

    @staticmethod
    def launch(type: PluginType):
        pass

    @staticmethod
    def isActive(type: PluginType):
        pass

    #
    # Server
    #

    def start_server(self):
        pass

    def handle_checkhealth(self, request):
        pass

    def handle_servermethod(self, request):
        pass

    def handle_daemonmethod(self, request):
        pass

    # Decorator
    def daemon_method():
        pass

    #
    # CPDaemon
    #

    def start(type: PluginType):
        pass

    def stop():
        pass


