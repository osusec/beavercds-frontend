from django.http import HttpResponseForbidden, JsonResponse

from .settings import AUTHORIZATION_TOKEN


class AuthorizationTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if auth_header:
            request_token = auth_header.split(" ")[-1]
            if request_token == AUTHORIZATION_TOKEN:
                return self.get_response(request)

        return JsonResponse({"errors": "Unauthorized"}, status=401)
