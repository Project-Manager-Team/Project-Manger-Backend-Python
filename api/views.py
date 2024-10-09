from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response


@api_view(["GET"])
def hello(request: Request):
    message = "Hello, world!"

    if username := request.user.username:
        message = f"Hello, your username is {username}."

    return Response({"message": message})
