from rest_framework.authentication import TokenAuthentication
from user.models.customtokenmodel import CustomToken

class customtoken(TokenAuthentication):
    model = CustomToken

