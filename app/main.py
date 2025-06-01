from dotenv import load_dotenv
from fastapi import Request, FastAPI
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import StatementError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.routers import auth, problem, schema, execute
from app.utils.response import api_response

load_dotenv()

app = FastAPI(root_path='/api', docs_url=None, redoc_url=None, openapi_url=None)

app.include_router(auth.router)
app.include_router(problem.router)
app.include_router(schema.router)
app.include_router(execute.router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return api_response(error=True, message=exc.detail, data=None)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return api_response(error=True, message=str(exc), data=None)


@app.exception_handler(StatementError)
async def general_exception_handler(request: Request, exc: StatementError):
    msg = str(exc.orig.args[1]) if (hasattr(exc.orig, 'args') and len(exc.orig.args) > 1) else str(exc.orig)
    return api_response(error=True, message=msg, data=None)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return api_response(error=True, message=str(exc), data=None)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
