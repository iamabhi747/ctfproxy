from .cli import handle_cli
from .util.pluginmgr import PluginType

def main():
    handle_cli(PluginType.HOST)
