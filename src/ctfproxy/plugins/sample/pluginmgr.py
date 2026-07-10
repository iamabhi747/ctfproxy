from urllib3 import util
from typing import Any
from pydantic import BaseModel
from InquirerPy import inquirer
from InquirerPy.validator import NumberValidator
from argparse import ArgumentParser, _SubParsersAction

from ...util.pluginmgr import PluginType, ClientPluginHandler, daemon_method
from ...util.log import log, LT, console

class SampleConfig (BaseModel):
    isDefined: bool = False
    name: str = ""
    salary: int = 0
    company: str = ""

class SamplePluginManager (ClientPluginHandler):
    NAME = "SamplePluginManager"
    SHORTNAME = "sample"

    userConfig: SampleConfig = SampleConfig()
    _userConfigType = SampleConfig

    @daemon_method
    def t1(self):
        log(LT.DEBUG, "Server Method t1 called.")
        return [10, 9, 10]

    @daemon_method
    def t2(self) -> str:
        log(LT.DEBUG, f"Sending name in config. ({self.userConfig.name})")
        return self.userConfig.name


    def cli(self, args: dict):
        subcmd = args.subcmd
        if subcmd == "t1":
            arr = self.t1()
            log(LT.DEBUG, "Result of server method: ", arr)

        elif subcmd == "t2":
            name = self.t2()
            log(LT.DEBUG, "Got Name as:", name)

        else:
            log(LT.WARN, f"Invalid/Not Implimented Sub-command in sample. ({subcmd})")
            return

    def cli_init(self, cmd_subp: _SubParsersAction[ArgumentParser], plugin_subp: _SubParsersAction[ArgumentParser]):
        sample_p = cmd_subp.add_parser("sample", help="Sample command for testing.")
        sample_p.set_defaults(plugin=self.NAME)

        sample_p.add_argument("subcmd", help="Sample subtest.", choices=["t1", "t2"])
        sample_p.add_argument("--opt1", "-a", help="Sample Option 1 / a", action="store_true")

    def config_init(self, config: dict[str, dict[str, Any]]):
        sampleConfig = SampleConfig.model_validate(config.get(self.NAME, dict()))

        console.print("[cyan bold underline]( Sample Config )[/]")

        if sampleConfig.isDefined:
            skip = inquirer.confirm(message="Sample Config is already defined, do you want to skip?", default=True).execute()
            if skip:
                return

        sampleConfig.name = inquirer.text(message="Enter your name:", default=sampleConfig.name).execute()
        sampleConfig.company = inquirer.text(
            message="Which company would you like to apply:",
                completer={
                "Nvidia": None,
                "Google": None,
                "Facebook": None,
                "Amazon": None,
                "Netflix": None,
                "Apple": None,
                "Microsoft": None,
            },
            multicolumn_complete=True,
            default=sampleConfig.company
        ).execute()
        sampleConfig.salary = inquirer.text(
            message="What's your salary expectation(k):",
            transformer=lambda result: "%sk" % result,
            filter=lambda result: int(result) * 1000,
            validate=NumberValidator(),
            default=f"{int(sampleConfig.salary / 1000)}"
        ).execute()
        confirm = inquirer.confirm(message="Confirm?", default=False).execute()

        if confirm:
            sampleConfig.isDefined = True
            config[self.NAME] = sampleConfig.model_dump()
