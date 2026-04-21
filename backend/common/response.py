from rest_framework.response import Response


def success_response(data=None, message: str = "Success", status_code: int = 200) -> Response:
    return Response(
        {
            "code": 0,
            "message": message,
            "data": data,
        },
        status=status_code,
    )
