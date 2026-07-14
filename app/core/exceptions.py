from typing import Any, Optional


class AppException(Exception):
    """Base application exception with structured error data."""

    def __init__(
        self,
        status_code: int = 500,
        detail: str = "Internal server error",
        error_code: str = "INTERNAL_ERROR",
        headers: Optional[dict] = None,
        context: Optional[dict] = None,
    ):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        self.headers = headers
        self.context = context or {}
        super().__init__(self.detail)

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": {
                "code": self.error_code,
                "message": self.detail,
                "status_code": self.status_code,
                "context": self.context,
            }
        }


class NotFoundException(AppException):
    def __init__(self, entity: str = "Resource", entity_id: Any = None):
        detail = f"{entity} not found"
        if entity_id:
            detail = f"{entity} with id '{entity_id}' not found"
        super().__init__(
            status_code=404,
            detail=detail,
            error_code="NOT_FOUND",
            context={"entity": entity, "entity_id": entity_id},
        )


class DuplicateException(AppException):
    def __init__(self, entity: str = "Resource", field: str = "", value: Any = None):
        detail = f"{entity} already exists"
        if field and value:
            detail = f"{entity} with {field} '{value}' already exists"
        super().__init__(
            status_code=409,
            detail=detail,
            error_code="DUPLICATE_ENTITY",
            context={"entity": entity, "field": field, "value": str(value)},
        )


class ValidationException(AppException):
    def __init__(self, detail: str = "Validation failed", errors: Optional[list] = None):
        super().__init__(
            status_code=422,
            detail=detail,
            error_code="VALIDATION_ERROR",
            context={"errors": errors or []},
        )


class AuthenticationException(AppException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=401,
            detail=detail,
            error_code="AUTHENTICATION_ERROR",
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationException(AppException):
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=403,
            detail=detail,
            error_code="FORBIDDEN",
        )


class RateLimitException(AppException):
    def __init__(self, detail: str = "Rate limit exceeded. Try again later."):
        super().__init__(
            status_code=429,
            detail=detail,
            error_code="RATE_LIMIT_EXCEEDED",
        )


class IntegrationException(AppException):
    def __init__(self, service: str = "external", detail: str = "External service error"):
        super().__init__(
            status_code=502,
            detail=detail,
            error_code=f"{service.upper()}_ERROR",
            context={"service": service},
        )


class DatabaseException(AppException):
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=503,
            detail=detail,
            error_code="DATABASE_ERROR",
        )
