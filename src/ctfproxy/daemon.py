import sys
import time
import json
import subprocess
from contextlib import asynccontextmanager

import uvicorn
import requests
from fastapi import FastAPI, APIRouter, HTTPException, Request 
from fastapi.responses import Response
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .plugins import ALL_PLUGINS, PluginType, InitState, PluginManager,  filterPlugins
from .util.pydanticmodels import *
from .util.config import CPConfig
from .util.log import LT, log
from .util.getfreeport import getFreePort

class CPDaemon:
    TYPE = PluginType.DISABLED
    plugins: dict[str, PluginManager] = {}

    router : APIRouter = None
    ipcapp = None
    serverPort = 7477
    config = None

    #
    # Cli
    #

    @staticmethod
    def ensure(type: PluginType):
        if type not in [PluginType.HOST, PluginType.CLIENT]:
            log(LT.WARN, "Invalid Daemon type, only HOST & ClIENT allowed.")
            return

        if not CPDaemon.isActive(type):
            CPDaemon.launch(type)

    @staticmethod
    def launch(type: PluginType) -> bool:
        tname = ""
        if type == PluginType.HOST: tname = "host"
        elif type == PluginType.CLIENT: tname = "client"
        else: return

        if CPDaemon.isActive(type):
            log(LT.INFO, "CPDaemon is already running.")
            return True

        try:
            cmd = [sys.executable, "-m", "ctfproxy.daemon", tname]

            kwargs = {
                "stdout": subprocess.DEVNULL,
                "stderr": subprocess.DEVNULL,
                "stdin" : subprocess.DEVNULL,
            }

            if sys.platform == "win32":
                kwargs["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
            else:
                kwargs["start_new_session"] = True
                kwargs["cwd"] = "/"

            process = subprocess.Popen(cmd, **kwargs)
            log(LT.DEBUG, "Daemon Process ID: ", process.pid)
        except Exception as e:
            log(LT.ERROR, f"Failed to launch CPDaemon. ({e.__class__.__name__})")
            return False

        status = CPDaemon.isActive(type, True)
        if status:
            log(LT.INFO, f"{tname} daemon is started.")
        else:
            log(LT.ERROR, f"{tname} daemon failed to start!")
        return status

    @staticmethod
    def isActive(type: PluginType, waitTillActive = False, tries = 10) -> bool:
        cfg = CPConfig()
        sock = None
        getSockFunc = None
        if type == PluginType.HOST:
            getSockFunc = cfg.getHostDaemon
        elif type == PluginType.CLIENT:
            getSockFunc = cfg.getClientDaemon
        else:
            log(LT.WARN, "Invalid Daemon type, only HOST & ClIENT allowed.")
            return False

        while tries > 0:
            sock = getSockFunc()
            # log(LT.DEBUG, "Daemon Info: ", sock)
            if  sock is not None and sock.get("active", False):
                try:
                    res = requests.get(f"http://127.0.0.1:{sock.get("port", 7477)}/api/checkhealth", timeout=0.2)
                    if res.status_code == 200 and res.json().get("success", False):
                        # log(LT.DEBUG, "Daemon is Active!")
                        return True
                except Exception as e:
                    log(LT.DEBUG, "Got error: ", e)
                    if not waitTillActive: 
                        return False

            if not waitTillActive:
                return False

            tries -= 1
            time.sleep(0.2)
        return False

    @staticmethod
    def getRef(type: PluginType) -> dict:
        cfg = CPConfig()

        if type == PluginType.HOST:
            return cfg.getHostDaemon()
        elif type == PluginType.CLIENT:
            return cfg.getClientDaemon()
        else:
            return {}

    #
    # Control Server
    #

    def start_server(self):
        @asynccontextmanager
        async def server_lifespan(app: FastAPI):
            self.on_server_start()
            yield
            self.on_server_stop()

        self.router = APIRouter()
        self.router.add_api_route("/api/checkhealth", self.handle_checkhealth, methods=["GET"], response_model=ResponseData)
        self.router.add_api_route("/api/servermethod", self.handle_servermethod, methods=["POST"], response_model=ResponseData)
        self.router.add_api_route("/api/daemonmethod", self.handle_daemonmethod, methods=["POST"], response_model=ResponseData)

        self.ipcapp = FastAPI(title="Control Server for CTFProxy Daemon", lifespan=server_lifespan)
        self.ipcapp.include_router(self.router)

        self.ipcapp.add_exception_handler(RequestValidationError, self.handle_input_validation_exception)
        self.ipcapp.add_exception_handler(StarletteHTTPException, self.handle_http_exception)
        self.ipcapp.add_exception_handler(Exception, self.handle_inernal_exception)

        self.serverPort = getFreePort('127.0.0.1')
        uvicorn.run(self.ipcapp, host='127.0.0.1', port=self.serverPort)

    def on_server_start(self):
        log(LT.DEBUG, "Control Server Started at port", self.serverPort)
        daemonInfo = {
            "active": True,
            "port": self.serverPort,
        }
        if self.TYPE == PluginType.HOST:
            self.config.saveHostDaemon(daemonInfo)
        else:
            self.config.saveClientDaemon(daemonInfo)

    def on_server_stop(self):
        log(LT.DEBUG, "Control Server Stoped.")
        if self.TYPE == PluginType.HOST:
            self.config.saveHostDaemon(None)
        else:
            self.config.saveClientDaemon(None)

    async def handle_checkhealth(self, request: Request):
        return ResponseData(success=True, datatype = ResponseType.HEALTH, data={
           "status": "OK", 
        })

    async def handle_servermethod(self, request: ServerMethodRequest):
        if request.plugin in self.plugins:
            return self.plugins[request.plugin].handle_request(request)
        else:
            raise HTTPException(478, detail=f"Requested plugin does not exits. ({request.plugin})")

    async def handle_daemonmethod(self, request: DaemonMethodRequest):
        attr = getattr(self, request.method, None)
        if attr:
            if getattr(attr, "_is_daemon_method", False):
                result = attr(**request.kwargs)
                return ResponseData(success=True, datatype=ResponseType.METHOD_OUTPUT, data = result)
            else:
                raise HTTPException(477, detail=f"Requested method is not a daemon method. ({request.method})")
        else:
            raise HTTPException(477, detail=f"Requested method does not exists. ({request.method})")


    async def handle_inernal_exception(self, request: Request, e: Exception):
        return Response(status_code=500, content=ErrorResponse(
            success=False,
            statuscode = 500,
            errtyepe = ErrorType.OPERATION,
            errmessage = f"Requested method raised err. ({e.__class__.__name__})",
            detail = f"{e}"
        ).model_dump_json())

    async def handle_http_exception(self, request: Request, e: StarletteHTTPException):
        typeMap = {
            477: ErrorType.INVALID_METHOD,
            478: ErrorType.INVALID_PLUGIN,
        }
        return Response(status_code=e.status_code, content=ErrorResponse(
            success=False,
            statuscode = e.status_code,
            errtyepe = typeMap.get(e.status_code, ErrorType.OPERATION),
            errmessage = f"Non OK HTTP response.",
            detail = e.detail
        ).model_dump_json())

    async def handle_input_validation_exception(self, request: Request, e: RequestValidationError):
        return Response(status_code=422, content=ErrorResponse(
            success=False,
            statuscode = 422,
            errtyepe = ErrorType.VALIDATION,
            errmessage = f"Invalid Input.",
            detail = e.errors()
        ).model_dump_json())

    # Decorator
    def daemon_method(func):
        func._is_daemon_method = True
        return func

    #
    # CPDaemon
    #

    def __init__(self, type: PluginType = PluginType.DISABLED):
        self.TYPE = type

    def start_plugins(self):
        self.plugins = filterPlugins(ALL_PLUGINS, [self.TYPE, PluginType.CLIENT_HOST], isServer=True)

        if self.TYPE == PluginType.HOST:
            userConfig = self.config.getHostConfig()
            serverConfig = self.config.getDefaultServerConfig()
        else:
            userConfig = self.config.getClientConfig()
            serverConfig = {}

        doneSet = set()
        for _, plugin in self.plugins.items():
            if not plugin.dependencies.issubset(doneSet):
                plugin._IS = InitState.DEPEND_FAILED
            elif plugin._IS == InitState.NOT_STARTED:
                for dependName in plugin.dependencies:
                    plugin.DD[dependName] = self.plugins[dependName]

                try:
                    plugin.init({
                        "serverConfig": serverConfig.get(plugin.NAME, {}),
                        "userConfig": userConfig.get(plugin.NAME, {})
                    })
                    plugin._IS = InitState.DONE
                    doneSet.add(plugin.NAME)
                except Exception as e:
                    plugin._IS = InitState.FAILED
                    plugin.error = f"{e}"

    def start(self):
        self.config = CPConfig()
        self.start_plugins()

        # Blocking, Should be called at very end of start()
        self.start_server()

    @daemon_method
    def stop(self):
        pass

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2 or sys.argv[1] not in ["host", "client"]:
        print("CPDaemon requires type to be specified as argument. (host / client)")
        exit(1)

    _type = PluginType.DISABLED
    if sys.argv[1] == "host":
        _type = PluginType.HOST
    elif sys.argv[1] == "client":
        _type = PluginType.CLIENT

    daemon = CPDaemon(_type)
    daemon.start()
