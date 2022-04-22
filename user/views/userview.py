from django.db import transaction
from rest_framework import viewsets, generics, status
from rest_framework.authtoken.views import ObtainAuthToken
# from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.forms.models import model_to_dict
from rest_framework.permissions import AllowAny, IsAuthenticated
from task import settings as SETTINGS
from django.contrib.auth import logout
from django.contrib.auth.models import update_last_login
from rest_framework.decorators import api_view, action
from django.http import JsonResponse
from django.core import serializers
import json

from user.models.usermodel import User
from user.models.customtokenmodel import CustomToken as Token
from user.serializers.userserializer import UserSerializer, ListUserSerializer
# from task.utils import helper as HELPER

import logging
logger = logging.getLogger(__name__)


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        """ User login call 
            User and password should not be None
        """
        if(request.data.get('username') == None or request.data.get('password') == None): 
            return Response(data={
                "status": "error",
                "errors": [{"message": "Email and password required."}]},
                status=400
            )

        try:
            # AuthToken serializer to validate userid and password
            serializer = self.serializer_class(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            update_last_login(None, token.user)
            user_serializer = ListUserSerializer(user)
            return Response({ 
                "status": "success", 
                "token": token.key, 
                "message": "You are successfully logged in.", 
                "data": {
                    "user": user_serializer.data
                    } 
                }, 
                 status=200)
        except Exception as e: 
            logger.error(str(e))
            return Response(data={
                "status": "error",
                "errors": [
                    {
                        "message": ["Invalid user"]
                    }
                ],
                },
                status=400
            )


class UserCreateAPIView(viewsets.ViewSet):
    """ Create a new user """
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """ Create user call 
            Create user request is made by super user or manager only
            User role is manager or user only
        """
        data = request.data
        try:
            # Checking if create user request is made by super user or manager only
            if not request.user.is_superuser and request.user.role != SETTINGS.MANAGER_ROLE:
                return Response(data={
                    "status": "error",
                    "errors": [
                        {
                            "message": ["User donot have enough previleges to perform this actions."]
                        }
                    ],
                    }, 
                    status=400
                    )
            # Checking if the user role is manager or user only
            if data['role'].lower() != SETTINGS.USER_ROLE and \
                data['role'].lower() != SETTINGS.MANAGER_ROLE: 
                    return Response(data={
                        "status": "error",
                        "errors": [
                            {
                                "message": ["User role can be either manager or user."]
                            }
                        ],
                        },
                        status=400
                    )

            # Converting email and full_name (if exists) to small letters
            data['email'] = data['email'].lower()
            if 'full_name' in data: data['full_name'] = data['full_name'].lower()

            if User.inactive.filter(email=data['email']):
                return Response(data={
                    "status": "error",
                    "errors": [
                        {
                            "message": ["User with this email address already exists"]
                        }
                    ],
                    },
                    status=400
                )

            # Creating new user if validated
            with transaction.atomic():
                serializer = UserSerializer(data=data)
                if serializer.is_valid():
                    new_user = serializer.create(serializer.validated_data)
                    new_user.set_password(serializer.validated_data['password'])
                    new_user.save()

                else: return Response(data={
                    "status": "error",
                    "errors": [serializer.errors]},
                    status=400
                    )
            
            return Response({
                "status": "success",
                "message": f"User {new_user.id} successfully create.",
                "data": {
                    "user": { "id": new_user.id }
                }
            }, 200)
        except Exception as e: 
            logger.error(str(e))
            return Response(data={
                "status": "error",
                "errors": [
                    {
                        "message": ["User cannot be created at the moment."],
                        "msg2": [str(e)]
                    }
                ],
                },
                status=422
            )


class UserAPIView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    def list(self, request):
        """ User list call """
        if request.user.role != "manager":
            logger.error(f"User {request.user} is not mangaer, trying to access Users List")
            return Response({
                "status": "error",
                "errors": [
                    {
                        "message": ["Not authorized to view users list"]
                    }
                ],
                }, 400)

        try:
            data = request.query_params
            if 'list' in data:
                if data['list'] == 'inactive':
                    user_list_serializer = ListUserSerializer(User.inactive.filter(role__in = (SETTINGS.USER_ROLE, SETTINGS.MANAGER_ROLE)), many=True)
                else :
                    logger.error(f"list user:wrong query parameter")
                    return Response({
                        "status": "error",
                        "errors": [
                            {
                                "message": ["unable to get user list"]
                            }
                        ],
                        },
                        404)
            else:
                user_list_serializer = ListUserSerializer(User.objects.filter(role__in = (SETTINGS.USER_ROLE, SETTINGS.MANAGER_ROLE)), many=True)
        except Exception as e:
            logger.error(f"list user : {str(e)}")
            return Response({
            "status": "error",
            "errors": [
                {
                    "message": ["unable to get user list"]
                }
            ],
            },
            404)

        return Response({
            "status": "success",
            "message": "User list successfully returned.",
            "data": {"user": user_list_serializer.data
            }
        }, 200)



    @action(methods=['PUT'], detail=False, url_path='update-user', url_name='update-user')
    def update_user(self, request, format=None):
        """ Update user, and assign role. 
            Update user request is made by super user or manager only
        """
        data = request.data
        try:
            # Checking if create user request is made by super user or manager only
            if not request.user.is_superuser and request.user.role != SETTINGS.MANAGER_ROLE:
                return Response(data={
                    "status": "error",
                    "errors": [
                        {
                        "message": ["User donot have enough previleges to perform this actions."]
                        }
                    ],
                    },
                    status=400
                    )
            # Getting user object that is to be updated
            user_obj = User.objects.get(pk=data['id'])
            if not 'id' in data: return Response(data={
                "status": "error",
                "errors": [
                    {
                        "message": ["Please provide user id."],
                        "msg2": [str(e)]
                    }
                ],
                "errors": ["Please provide user id.",
                str(e)]},
                status=400
                )
            if 'email' in data: return Response(data={
                "status": "error",
                "errors": [
                    {
                        "message": ["Email cannot be updated."],
                        "msg2": [str(e)]
                    }
                ],
                },
                status=400
            )
            if 'full_name' in data: user_obj.full_name = data['full_name'].lower()
            if 'password' in data: user_obj.set_password(data['password'])
            if "phone_no" in data: user_obj.phone_no = data['phone_no']
            if "is_active" in data: user_obj.is_active = data['is_active']
            if "role" in data and (data['role'] == SETTINGS.MANAGER_ROLE or \
                data['role'] == SETTINGS.USER_ROLE):
                    user_obj.role = data['role']
            # Updating user details
            user_obj.save()
            user_serializer = ListUserSerializer(user_obj)

            return Response({
                "status": "success",
                "message": "User successfully updated.",
                "data": {
                    "user": user_serializer.data
                }
            }, 200)

        except User.DoesNotExist: return Response(data={
            "status": "error",
            "errors": [
                {
                    "message": ["User not found."]
                }
            ],
            },
            status=404
            )
        except Exception as e: 
            logger.error(str(e))
            return Response(
                data={"status": "error",
                "errors": [
                    {
                        "message": ["User cannot be updated at the moment."],
                        "msg2": [str(e)]
                    }
                ],
                },
                status=422
            )
    

    @action(methods=['PATCH'], detail=False, url_path='update-profile', url_name='update-profile')
    def update_profile(self, request, format=None):
        """ User profile update call 
            Manager by default returns only active users, so only active users can update their profile
            Update only full name and phone no fields
        """
        data = request.data
        try:
            # Getting user object that is to be updated
            user_obj = User.objects.get(pk=request.user.id)

            # Update only full name and phone no fields
            if 'full_name' in data: user_obj.full_name = data['full_name'].lower()
            if "phone_no" in data: user_obj.phone_no = data['phone_no']
            # Update user model
            user_obj.save()
            user_serializer = ListUserSerializer(user_obj)

            return Response({
                "status": "success",
                "message": "User successfully updated.",
                "data": {
                    "user": user_serializer.data
                }
            }, 200)

        except User.DoesNotExist: return Response(data={
            "status": "error",
            "errors": [
                {
                    "message": ["User not found."]
                }
            ],
            },
            status=404
            )
        except Exception as e: 
            logger.error(str(e))
            return Response(
                data={"status": "error",
                "errors": [
                    {
                        "message": ["Profile cannot be updated at the moment."],
                        "msg2": [str(e)]
                    }
                ],
                },
                status=422
            )


    @action(detail=False, methods=['DELETE'], url_path='delete')
    def delete(self, request):
        """ User soft delete (is_active flag) call """
        try:
            if request.user.is_superuser or request.user.role == SETTINGS.MANAGER_ROLE:
                user = User.objects.get(pk=self.request.GET.get('q'))
                if (user != None):
                    user.is_active = not user.is_active
                    user.save()
                    return Response({
                        "status": "success",
                        "message": "User successfully deleted."
                    }, 200)
            return Response(data={
                "status": "error",
                "errors": [
                    {
                        "message": ["You donot have permissions to delete a user."]
                    }
                ],
                },
                status=400
                )
        except User.DoesNotExist: 
            return Response(data={
                "status": "error",
                "errors": [
                    {
                        "message": ["User not found."]
                    }
                ], 
                },
                status=404
            )
        except Exception as e: 
            logger.error(str(e))
            return Response(data={
                "status": "error",
                "errors": [
                    {
                        "message": ["User cannot be deleted."],
                        "msg2": [str(e)]
                    }
                ],
                }, 
                status=422
            )

    @action(methods=['PATCH'], detail=True, url_path='state', url_name='state')
    def state(self, request, pk=None):
        """ User soft enable and disable/dalete (is_active flag) call """
        try:
            data = request.query_params
            if request.user.is_superuser or request.user.role == SETTINGS.MANAGER_ROLE:
                user = User.allusers.get(pk=pk)
                if 'q' in data:
                    if (data['q'] == 'enable'):
                        if (user.is_active == True):
                            logger.error(f"trying to activate already active user : {user.email}")
                            return Response(data={
                            "status": "error",
                            "errors": [
                                {
                                    "message": ["User is already active."]
                                }
                            ],
                            },
                            status=400
                            )
                        user.is_active = True
                        user.save()
                        logger.info(f"User {user.email} sucessfully enabled")
                        return Response({
                            "status": "success",
                            "message": "User successfully enabled."
                        }, 200)
                    if (data['q'] == 'disable'):
                        if (user.is_active==False):
                            logger.error(f"trying to delete already deleted user : {user.email}")
                            return Response(data={
                            "status": "error",
                            "errors": [
                                {
                                    "message": ["User is already inactive."]
                                }
                            ],
                            },
                            status=400
                            )
                        user.is_active = False
                        user.save()
                        logger.info(f"User {user.email} sucessfully disabled")
                        return Response({
                            "status": "success",
                            "message": "User successfully disabled."
                        }, 200)
                    else:
                        logger.error(f"Wrong query parameter")
                        return Response(data={
                        "status": "error",
                        "errors": [
                            {
                            "message": ["Wrong query parameter"]
                            }
                        ],
                        },
                        status=400
                    )
                else: 
                    logger.error(f"Query parameter for status change not proided")
                    return Response(data={
                    "status": "error",
                    "errors": [
                        {
                        "message": ["User status to be changed not provided."]
                        }
                    ],
                    },
                    status=400
                    )

            logger.error(f"User {request.user.email} permissions error while deleting or activating other user")
            return Response(data={
                "status": "error",
                "errors": [
                    {
                    "message": ["Only Manager can enable or disable a user."]
                    }
                ],
                },
                status=400
                )
        except User.DoesNotExist:
            logger.error(f"User {pk} not found")
            return Response(data={
            "status": "error",
            "errors": [
                {
                "message": ["User not found."]
                }
            ], 
            },
            status=404
            )
        
    @action(detail=False, methods=['GET'], url_path='me')
    def me(self, request):
        """ User me call """
        return Response({ 
            "status": "success",
            "message": "User information successfully returned.",
            "data": ListUserSerializer(request.user).data },
            200
        )

 
    def retrieve(self, request, pk):
        """ Specific user call """
        try:
            user = User.objects.get(pk=pk)
            return Response({
                 "status": "success",
                 "message": "User details success.",
                 "data": ListUserSerializer(user).data },
                 200
                 )
        except User.DoesNotExist: 
            return Response(data={
                "status": "error",
                "errors": [
                    {
                    "message": ["User not found."]
                    }
                ],
                },
                status=422
            )
        except Exception as e: 
            logger.error(str(e))
            return Response(data={
                "status": "error", 
                "errors": [
                    {
                    "message": ["User doesnot exists."]
                    }
                ],
                }, 
                status=422
            )
    
    @action(detail=False, methods=['PATCH'], url_path='changepassword')
    def change_password(self, request):
        """ Change password call 
            Old password should be same as in model
            Password length should be in between 6 - 20 characters
            Old and new passwords should not match
            Password1 and password2 should be same
        """
        data = request.data
        try:
            valid, message = True, ''
            # Password1 and password2 should be same
            if not data['password1'] == data['password2']:
                valid = False
                message+="Password donot matches. "
            
            # New password cannot be same as old password
            if data['password1'] == data['old_password']:
                valid = False
                message+="New password cannot be same as old password. "

            # Password length should be in between 6 - 20 characters
            if len(data['password1']) < 6 or len(data['password1']) > 20:
                valid = False
                message+="New password cannot be less than 6 and greater than 20 characters. "

            # Getting and updating user password
            user = User.objects.get(id=self.request.user.id)
            
            # Verifying old password
            if not user.check_password(data['old_password']):
                valid = False
                message+="Previous password is incorrect. "

            if not valid:    
                return Response(data={
                        "status": "error",
                        "errors": [
                            {
                            "message": [message]
                            }
                        ],
                        }, status=400
                    )

            user.set_password(data['password1'])
            user.save()
            # Deleting token if exists
            if hasattr(user, 'auth_token'): user.auth_token.delete()

            return Response({
                "status": "success",
                "message": f"Password has been changed."}, 
                status=status.HTTP_200_OK
                )

        except User.DoesNotExist: 
            return Response(data={
                "status": "error",
                "errors": [
                    {
                    "message": ["User not found."]
                    }
                ],
                },
                status=400
            )
        except Exception as e: 
            logger.error(str(e))
            return Response(data={
                "status": "error","errors": [
                    {
                    "message": ["Password cannot be changed at the moment."],
                    "msg2": [str(e)]

                    }
                ],
                },
                status=422
            )


    @action(detail=False, methods=['POST'])
    def logout(self, request):
        """ User logout call """
        try:
            user_obj = request.user
            token_exists = Token.objects.get(user=user_obj).delete()
            logger.info(f'User {user_obj.email} deleted')
            return Response({
                "status": "success",
                "message": f"User {user_obj.email} is logged out."}, 
                status=status.HTTP_200_OK
                )

        except (AttributeError, ObjectDoesNotExist): pass
        except Exception as e: 
            logger.error(str(e))
            return Response(data={
                "status": "error",
                "errors": [
                    {
                    "message": ["User cannot be logged out at the moment."],
                    "msg2": [str(e)]
                    }
                ],
                },
                status=422
            )
