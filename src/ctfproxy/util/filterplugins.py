import heapq
import logging
import sys

from .pluginmgr import PluginType, PluginManager

logger = logging.getLogger(__name__)

def filterPlugins(plugins: list[type[PluginManager]], types: set[PluginType], isServer : bool = False) -> dict[str, PluginManager]:
    filteredPlugins = dict()

    pluginMap = {
        p.NAME: p for p in plugins if p.TYPE in types
    }

    adjList: dict[str, list[str]] = {
        pname: [] for pname in pluginMap.keys()
    }
    inDegree: dict[str, int] = {
        pname: 0 for pname in pluginMap.keys()
    }

    for pname, plugin in pluginMap.items():
        inDegree[pname] = len(plugin.dependencies)

        for dep in plugin.dependencies:
            if dep not in adjList:
                logger.critical(f"Missing dependency: '{dep}' required by '{plugin.NAME}'")
                sys.exit(1)
            adjList[dep].append(plugin.NAME)

    zeroDegreeHeap = []
    for name, degree in inDegree.items():
        if degree == 0:
            heapq.heappush(zeroDegreeHeap, (pluginMap[name].PRIORITY, name))

    while zeroDegreeHeap:
        _, pname = heapq.heappop(zeroDegreeHeap)
        filteredPlugins[pname] = pluginMap[pname](isServer)

        for dependent in adjList[pname]:
            inDegree[dependent] -= 1

            if inDegree[dependent] == 0:
                heapq.heappush(zeroDegreeHeap, (pluginMap[dependent].PRIORITY, dependent))

    if len(pluginMap) != len(filteredPlugins):
        logger.critical("Circular dependency detected. Cannot sort topologically.")
        sys.exit(1)

    return filteredPlugins
