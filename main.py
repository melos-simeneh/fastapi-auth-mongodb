from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import Optional
from utils.db import mongo_connection
from utils.settings import MONGO_TEST_DB_NAME,MONGO_DB_NAME
from contextlib import asynccontextmanager
from routes import auth_routes
from slowapi.errors import RateLimitExceeded
from utils import exception_handlers



# ----------------- Lifespan ----------------- #
@asynccontextmanager
async def lifespan(app: FastAPI, db_name):

    await mongo_connection.connect(db_name)
    yield
    
    # Cleanup only if it's the test DB
    if db_name == MONGO_TEST_DB_NAME:
        await mongo_connection.db["users"].delete_many({})
        
    await mongo_connection.close()


# ----------------- Error Formatter ----------------- #
def format_error_response(message: str, errors: Optional[list] = None, status_code: int = 400):
    content = {"success": False, "message": message}
    if errors:
        content["errors"] = errors
    return JSONResponse(status_code=status_code, content=content)


# ----------------- Register Handlers ----------------- #
def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(RateLimitExceeded,exception_handlers.rate_limit_exceeded_handler)
    app.add_exception_handler(RequestValidationError,exception_handlers.validation_exception_handler)
    app.add_exception_handler(HTTPException,exception_handlers.http_exception_handler)
    app.add_exception_handler(Exception,exception_handlers.general_exception_handler)



# ----------------- App Factory ----------------- #
def create_app(db_name: str = MONGO_DB_NAME) -> FastAPI:
    app = FastAPI(
        title="FastAPI Auth with MongoDB",
        version="1.0.0",
        description="API Schema Documentation",
        lifespan=lambda app: lifespan(app, db_name)
    )

    app.include_router(auth_routes.router)
    register_exception_handlers(app)

    return app


# ----------------- Run App (Production Entry) ----------------- #
app = create_app()
