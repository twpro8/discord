from fastapi import status


class LumiereError(Exception):
    detail: str = "Unexpected error"
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        detail: str | None = None,
        status_code: int | None = None,
    ) -> None:
        if detail is not None:
            self.detail = detail

        if status_code is not None:
            self.status_code = status_code

        super().__init__(self.detail)


class NotFoundError(LumiereError):
    detail = "Object not found"
    status_code = status.HTTP_404_NOT_FOUND


class ConflictError(LumiereError):
    detail = "Object already exists"
    status_code = status.HTTP_409_CONFLICT


class ValidationError(LumiereError):
    detail = "Validation error"
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
