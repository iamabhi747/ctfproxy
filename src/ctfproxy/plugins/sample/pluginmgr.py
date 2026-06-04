from argparse import ArgumentParser, _SubParsersAction

from urllib3 import util

from ...util.pluginmgr import PluginType, PluginManager, server_method
from ...util.log import log, LT

class SamplePluginManager (PluginManager):
    NAME = "SamplePluginManager"
    SHORTNAME = "sample"
    TYPE = PluginType.CLIENT_HOST

    @server_method
    def t1(self):
        log(LT.DEBUG, "Server Method t1 called.")
        return [10, 9, 10]

    def clientcli(self, args: dict):
        subcmd = args.subcmd
        if subcmd == "t1":
            arr = self.t1()
            log(LT.DEBUG, "Result of server method: ", arr)

        else:
            log(LT.WARN, f"Invalid/Not Implimented Sub-command in sample. ({subcmd})")
            return

    def clientcli_init(self, cmd_subp: _SubParsersAction[ArgumentParser], plugin_subp: _SubParsersAction[ArgumentParser]):
        sample_p = cmd_subp.add_parser("sample", help="Sample command for testing.")
        sample_p.set_defaults(plugin=self.NAME)

        sample_p.add_argument("subcmd", help="Sample subtest.", choices=["t1", "t2"])
        sample_p.add_argument("--opt1", "-a", help="Sample Option 1 / a", action="store_true")
