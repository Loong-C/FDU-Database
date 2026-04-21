from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models.deletion import ProtectedError, RestrictedError
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler


class ConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "conflict"
    default_detail = "The request conflicts with current business data."


def _message_from_detail(detail, fallback: str) -> str:
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list) and detail:
        return str(detail[0])
    if isinstance(detail, dict) and detail:
        first_value = next(iter(detail.values()))
        return _message_from_detail(first_value, fallback)
    return fallback


def custom_exception_handler(exc, context):
    if isinstance(exc, DjangoValidationError):
        detail = getattr(exc, "message_dict", None) or exc.messages
        exc = ValidationError(detail)
    elif isinstance(exc, (ProtectedError, RestrictedError)):
        exc = ConflictError("存在关联数据，当前记录不能删除。")

    response = exception_handler(exc, context)
    if response is None:
        return Response(
            {
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Internal server error",
                "data": None,
                "errors": None,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(exc, ValidationError):
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        message = "Validation failed"
    else:
        message = _message_from_detail(response.data, response.status_text)

    response.data = {
        "code": response.status_code,
        "message": message,
        "data": None,
        "errors": response.data if response.status_code != status.HTTP_204_NO_CONTENT else None,
    }
    return response
