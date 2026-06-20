from fastapi import status


class AppException(Exception):
    detail: str = "Unexpected error"
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        detail: str | None = None,
        status_code: int | None = None,
    ) -> None:
        self.detail = detail or self.detail
        self.status_code = status_code or self.status_code

        super().__init__(self.detail)


class ObjectNotFoundError(AppException):
    detail = "Object not found"
    status_code = status.HTTP_404_NOT_FOUND


class ObjectAlreadyExistsError(AppException):
    detail = "Object already exists"
    status_code = status.HTTP_409_CONFLICT
