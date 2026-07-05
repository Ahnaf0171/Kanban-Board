import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import PermissionDenied, ValidationError as DjangoValidationError

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        data = response.data
        message = _extract_message(data)
        response.data = {"success": False, "error": {"message": message, "details": data}}
        return response

    if isinstance(exc, Http404):
        return Response({"success": False, "error": {"message": "Resource not found."}}, status=status.HTTP_404_NOT_FOUND)
    if isinstance(exc, PermissionDenied):
        return Response({"success": False, "error": {"message": "Permission denied."}}, status=status.HTTP_403_FORBIDDEN)
    if isinstance(exc, DjangoValidationError):
        return Response({"success": False, "error": {"message": str(exc)}}, status=status.HTTP_400_BAD_REQUEST)

    logger.exception("Unhandled exception: %s", exc)
    return Response({"success": False, "error": {"message": "Something went wrong."}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _flatten(value):
    if isinstance(value, list):
        return " ".join(_flatten(v) for v in value)
    return str(value)


def _extract_message(data):
    if isinstance(data, dict):
        if "detail" in data:
            return _flatten(data["detail"])
        if "non_field_errors" in data:
            return _flatten(data["non_field_errors"])
        messages = [_flatten(value) for value in data.values()]
        return " ".join(messages) if messages else "An error occurred."

    if isinstance(data, list) and data:
        return _flatten(data)

    return "An error occurred."