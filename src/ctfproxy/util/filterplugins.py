from .pluginmgr import PluginType, PluginManager

def filterPlugins(plugins: list[type[PluginManager]], types: set[PluginType], isServer : bool = False) -> dict[str, PluginManager]:
    filteredPlugins = dict()

    for plugClass in plugins:
        if plugClass.TYPE in types:
            filteredPlugins[plugClass.NAME] = plugClass(isServer)

    return filteredPlugins
