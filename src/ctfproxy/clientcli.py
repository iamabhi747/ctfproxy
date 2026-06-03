import argparse

from .plugins import PluginType, ALL_PLUGINS, filterPlugins 
from .daemon import CPDaemon
from .util.log import log, LT

def main():
    CPDaemon.ensure(PluginType.CLIENT)

    parser = argparse.ArgumentParser(description="CTF Proxy CLI v0.1")
    parser.set_defaults(plugin=None)

    cmd_subp = parser.add_subparsers(dest="command", required=True)

    help_p = cmd_subp.add_parser("help", help="Show help information")

    plugin_p = cmd_subp.add_parser("plugin", aliases=['p'], help="Plugin related commands")
    plugin_p.add_argument("--server", "-s", help="Name of the server.")

    plugin_subp = plugin_p.add_subparsers(dest="plugincmd", required=True)

    clientPlugins = filterPlugins(ALL_PLUGINS, [PluginType.CLIENT, PluginType.CLIENT_HOST])
    for _, plugin in clientPlugins.items():
        plugin.clientcli_init(cmd_subp, plugin_subp)

    args = parser.parse_args()

    if args.command == 'help':
        parser.print_help()
        return

    else:
        if args.plugin not in clientPlugins:
            log(LT.EXIT, f"Something Went Wrong! Tried to call invalid plugin. ({plugincmd})")
            return
        try:
            plugin = clientPlugins[args.plugin]
            plugin.init(CPDaemon.getRef(), clientPlugins)
            plugin.clientcli(args)

        except Exception as e:
            log(LT.EXIT, f"Something Went Wrong! Plugin raised error while handling requuest. ({e})")
        return
