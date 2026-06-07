from .util.pluginmgr import PluginType
from .cli import handle_cli

def main():
    handle_cli(PluginType.CLIENT)
