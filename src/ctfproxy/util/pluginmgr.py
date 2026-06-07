import inspect
from enum import Enum, auto
from typing import Any

import requests
from argparse import _SubParsersAction, ArgumentParser

from .pydanticmodels import ResponseData, ResponseType, ServerMethodRequest, ErrorResponse, ErrorType

class PluginType (Enum):
    CLIENT = auto()
    HOST = auto()
    CLIENT_HOST = auto()
    DISABLED = auto()

class InitState (Enum):
    DONE = auto()
    NOT_STARTED = auto()
    FAILED = auto()
    DEPEND_FAILED = auto()

# Decorator
def server_method(func):
    def wrapper(self, *args, **kwargs):
        if self.isInServer:
            return func(self, *args, **kwargs)

        else:
            sig = inspect.signature(func)
            allkwargs = sig.bind(self, *args, **kwargs).arguments
            allkwargs.pop("self", None)

            return self.request_server(ServerMethodRequest(
                plugin= self.NAME,
                method= func.__name__,
                kwargs= allkwargs
            ))

    wrapper._is_server_method = True
    return wrapper

class PluginManager:
    NAME = "NONE"
    SHORTNAME = "NAN"
    TYPE = PluginType.DISABLED
    PRIORITY = 100
    DD : dict[PluginManager] = dict()
    dependencies: set[str] = set()

    _IS : InitState = InitState.NOT_STARTED # General Init State
    _COS : InitState = InitState.NOT_STARTED # Config Init State
    _CLS : InitState = InitState.NOT_STARTED # Cli Init State
    serverDetails = dict()
    isInServer = False
    error = None

    serverConfig = None
    _serverConfigType = None
    userConfig = None
    _userConfigType = None

    #
    # "Private/Internal" methods
    #

    def __init__(self, isServer: bool):
        self.isInServer = isServer

    def request_server(self, request: ServerMethodRequest) -> dict:
        try:
            res = requests.post(f"http://127.0.0.1:{self.serverDetails.get("port", 7477)}/api/servermethod",
            data = request.model_dump_json(),
            headers = {
                "Content-Type": "application/json"
            })

            if res.status_code == 200:
                rd = ResponseData.model_validate(res.json())
                return rd.data
            else:
                rd = ErrorResponse.model_validate(res.json())
                if rd.errtyepe == ErrorType.INVALID_METHOD or rd.errtyepe == ErrorType.INVALID_PLUGIN:
                    raise NameError("Invalid plugin or method. " + rd.errmessage)
                elif rd.errtyepe == ErrorType.VALIDATION:
                    raise AttributeError("Invalid request, values do not follow schema. " + rd.errmessage)
                else:
                    raise RuntimeError("Failed to execute method. " + rd.errmessage)
        except:
            raise ConnectionError(747, "Failed to connect.")

    def handle_request(self, request: ServerMethodRequest) -> ResponseData:
        attr = getattr(self, request.method, None)
        if attr:
            if getattr(attr, "_is_server_method", False):
                result = attr(**request.kwargs)
                return ResponseData(success=True, datatype=ResponseType.METHOD_OUTPUT, data = result)
            else:
                raise HTTPException(477, detail=f"Requested method is not a server method. ({self.NAME}::{request.method})")
        else:
            raise HTTPException(477, detail=f"Requested method does not exists. ({self.NAME}::{request.method})")

    #
    # "Plugin" methods
    #

    def init(self, daemonRef):
        if self._IS != InitState.NOT_STARTED: return
        if not self.isInServer:
            self.serverDetails = daemonRef
        else:
            if self._serverConfigType is not None:
                self.serverConfig = self._serverConfigType.model_validate(daemonRef.get("serverConfig", {}))
            else:
                self.serverConfig = daemonRef.get("serverConfig", {})

            if self._userConfigType is not None:
                self.userConfig = self._userConfigType.model_validate(daemonRef.get("userConfig", {}))
            else:
                self.userConfig = daemonRef.get("userConfig", {})

    def hostcli(self, args: dict):
        pass

    def hostcli_init(self, cmd_subp: _SubParsersAction[ArgumentParser], plugin_subp: _SubParsersAction[ArgumentParser]):
        pass

    def hostconfig_init(self, config: dict[str, dict[str, Any]]):
        pass

    def clientcli(self, args: dict):
        pass

    def clientcli_init(self, cmd_subp: _SubParsersAction[ArgumentParser], plugin_subp: _SubParsersAction[ArgumentParser]):
        pass

    def clientconfig_init(self, config: dict[str, dict[str, Any]]):
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


