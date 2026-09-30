class DomainError(Exception):
    status_code = 400


class BusinessRuleError(DomainError):
    status_code = 400


class PermissionDeniedError(DomainError):
    status_code = 403


class NotFoundError(DomainError):
    status_code = 404


class ConflictError(DomainError):
    status_code = 409


class ExternalServiceError(DomainError):
    status_code = 502