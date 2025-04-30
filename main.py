from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import Optional
from utils.db import mongo_connection
from utils.settings import MONGO_TEST_DB_NAME,MONGO_DB_NAME
from contextlib import asynccontextmanager
from routes import auth_routes
from slowapi.errors import RateLimitExceeded


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
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
        return format_error_response("Too many requests. Please try again later.", status_code=429)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        error_details = [
            {
                "field": ".".join(str(loc) for loc in err["loc"][1:]) or str(err["loc"][0]),
                "message": err["msg"][13:] if err["msg"].startswith("Value error, ") else err["msg"],
            }
            for err in exc.errors()
        ]
        return format_error_response("Validation failed", error_details, 422)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return format_error_response(str(exc.detail), status_code=exc.status_code)

    @app.exception_handler(KeyError)
    async def key_error_handler(request: Request, exc: KeyError):
        return format_error_response("Missing key", [{
            "field": str(exc),
            "message": "A required key was not found"
        }])

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return format_error_response("Internal server error", [{
            "message": str(exc)
        }], status_code=500)


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
