
from sys import argv

import uvicorn
from fastapi import FastAPI, APIRouter, Request, HTTPException
from fastapi.responses import Response
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .plugins import ALL_PLUGINS, PluginType, PluginManager,  filterPlugins
from .util.pydanticmodels import *

class CPDaemon:
    TYPE = PluginType.DISABLED
    plugins: list[PluginManager] = []

    router : APIRouter = None
    ipcapp = None

    #
    # Cli
    #

    @staticmethod
    def ensure(type: PluginType):
        pass

    @staticmethod
    def launch(type: PluginType):
        pass

    @staticmethod
    def isActive(type: PluginType):
        pass

    #
    # Control Server
    #

    def start_server(self):
        self.router = APIRouter()
        self.router.add_api_route("/api/checkhealth", self.handle_checkhealth, methods=["GET"], response_model=ResponseData)
        self.router.add_api_route("/api/servermethod", self.handle_servermethod, methods=["POST"], response_model=ResponseData)
        self.router.add_api_route("/api/daemonmethod", self.handle_daemonmethod, methods=["POST"], response_model=ResponseData)

        self.ipcapp = FastAPI(title="Control Server for CTFProxy Daemon")
        self.ipcapp.include_router(self.router)

        self.ipcapp.add_exception_handler(RequestValidationError, self.handle_input_validation_exception)
        self.ipcapp.add_exception_handler(StarletteHTTPException, self.handle_http_exception)
        self.ipcapp.add_exception_handler(Exception, self.handle_inernal_exception)

        uvicorn.run(self.ipcapp, host='0.0.0.0', port=5555)

    async def handle_checkhealth(self, request: Request):
        return ResponseData(success=True, datatype = ResponseType.HEALTH, data={
           "status": "OK", 
        })

    async def handle_servermethod(self, request: ServerMethodRequest):
        pass

    async def handle_daemonmethod(self, request: DaemonMethodRequest):
        pass

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
    def daemon_method():
        pass

    #
    # CPDaemon
    #

    def __init__(self, type: PluginType = PluginType.DISABLED):
        self.TYPE = type

    def start(self):
        # Blocking, Should be called at very end of start()
        self.start_server()

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
