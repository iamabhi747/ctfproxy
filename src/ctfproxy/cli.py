import argparse

from .plugins import PluginType, InitState, ALL_PLUGINS, filterPlugins 
from .daemon import CPDaemon
from .util.log import log, LT
from .util.config import CPConfig

def handle_cli(ct: PluginType):
    if ct not in [PluginType.CLIENT, PluginType.HOST]:
        return

    CPDaemon.ensure(ct)

    parser = argparse.ArgumentParser(description="CTF Proxy CLI v0.1")
    parser.set_defaults(plugin=None)

    cmd_subp = parser.add_subparsers(dest="command", required=True)

    help_p = cmd_subp.add_parser("help", help="Show help information")

    init_p = cmd_subp.add_parser("init", help="Init config.")

    plugin_p = cmd_subp.add_parser("plugin", aliases=['p'], help="Plugin related commands")
    plugin_p.add_argument("--server", "-s", help="Name of the server.")

    plugin_subp = plugin_p.add_subparsers(dest="plugincmd", required=True)

    # Filters & returns in topological order
    filteredPlugins = filterPlugins(ALL_PLUGINS, {ct, PluginType.CLIENT_HOST}, isServer=False)

    doneSet = set() 
    for _, plugin in filteredPlugins.items():
        if not plugin.dependencies.issubset(doneSet):
            plugin._CLS = InitState.DEPEND_FAILED
        elif plugin._CLS == InitState.NOT_STARTED:
            try:
                if ct == PluginType.HOST:
                    plugin.hostcli_init(cmd_subp, plugin_subp)
                else:
                    plugin.clientcli_init(cmd_subp, plugin_subp)
                plugin._CLS = InitState.DONE
                doneSet.add(plugin.NAME)
            except Exception as e:
                log(LT.DEBUG, f"Error in {plugin.NAME}:CLiint => {e}")
                plugin._CLS = InitState.FAILED
            except KeyboardInterrupt:
                exit(1)

    args = parser.parse_args()

    if args.command == 'help':
        parser.print_help()
        return

    elif args.command == 'init':
        cfg = CPConfig()
        if ct == PluginType.HOST:
            config = cfg.getHostConfig()
        else:
            config = cfg.getClientConfig()

        doneSet = set() 
        for _, plugin in filteredPlugins.items():
            if not plugin.dependencies.issubset(doneSet):
                plugin._COS = InitState.DEPEND_FAILED
            elif plugin._COS == InitState.NOT_STARTED:
                try:
                    if ct == PluginType.HOST:
                        plugin.hostconfig_init(config)
                    else:
                        plugin.clientconfig_init(config)
                    plugin._COS = InitState.DONE
                    doneSet.add(plugin.NAME)
                except Exception as e:
                    log(LT.DEBUG, f"Error in {plugin.NAME}:Configint => {e}")
                    plugin._COS = InitState.FAILED
                except KeyboardInterrupt:
                    exit(1)

        if ct == PluginType.HOST:
            cfg.saveHostConfig(config)
        else:
            cfg.saveClientConfig(config)
        log(LT.SUCCESS, "Config Saved.")
        return

    else:
        if args.plugin not in filteredPlugins:
            log(LT.EXIT, f"Something Went Wrong! Tried to call invalid plugin. ({args.plugin})")
            return
        try:
            doneSet = set() 
            for _, plugin in filteredPlugins.items():
                if not plugin.dependencies.issubset(doneSet):
                    plugin._IS = InitState.DEPEND_FAILED
                elif plugin._IS == InitState.NOT_STARTED:
                    for dependName in plugin.dependencies:
                        plugin.DD[dependName] = filteredPlugins[dependName]

                    try:
                        plugin.init(CPDaemon.getRef(ct))
                        plugin._IS = InitState.DONE
                        doneSet.add(plugin.NAME)
                    except Exception as e:
                        plugin._IS = InitState.FAILED
                        plugin.error = f"{e}"

            plugin = filteredPlugins[args.plugin]
            if plugin._IS == InitState.DONE:
                if ct == PluginType.HOST:
                    plugin.hostcli(args)
                else:
                    plugin.clientcli(args)

            else:
                log(LT.EXIT, f"Failed to init requested plugin ({plugin.NAME}), reason: {"Dependency Failed to init." if plugin._IS == InitState.DEPEND_FAILED else f"Error: {plugin.error}"}")
                return

        except Exception as e:
            log(LT.EXIT, f"Something Went Wrong! Plugin raised error while handling requuest. ({e})")
        return
