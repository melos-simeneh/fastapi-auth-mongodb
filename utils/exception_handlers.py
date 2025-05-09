from fastapi import  Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import Optional
from slowapi.errors import RateLimitExceeded

# ----------------- Error Formatter ----------------- #
def format_error_response(message: str, errors: Optional[list] = None, status_code: int = 400):
    content = {"success": False, "message": message}
    if errors:
        content["errors"] = errors
    return JSONResponse(status_code=status_code, content=content)

async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
        return format_error_response("Too many requests. Please try again later.", status_code=429)

 
async def validation_exception_handler(request: Request, exc: RequestValidationError):
        error_details = [
            {
                "field": ".".join(str(loc) for loc in err["loc"][1:]) or str(err["loc"][0]),
                "message": err["msg"][13:] if err["msg"].startswith("Value error, ") else err["msg"],
            }
            for err in exc.errors()
        ]
        return format_error_response("Validation failed", error_details, 422)


async def http_exception_handler(request: Request, exc: HTTPException):
        return format_error_response(str(exc.detail), status_code=exc.status_code)


async def key_error_handler(request: Request, exc: KeyError):
        return format_error_response("Missing key", [{
            "field": str(exc),
            "message": "A required key was not found"
        }])


async def general_exception_handler(request: Request, exc: Exception):
        return format_error_response("Internal server error", [{
            "message": str(exc)
        }], status_code=500)