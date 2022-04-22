from rest_framework import serializers
from user.models.usermodel import User
from django.contrib.auth import get_user_model

class UserSerializer(serializers.ModelSerializer):
    """ Serializer for user object """

    class Meta:
        model = get_user_model()
        fields = '__all__'
        read_only_fields = ['id']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 6}}

class ListUserSerializer(serializers.ModelSerializer):
    """ List all user serializer """
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'phone_no', 'is_active', 'role', 'date_joined', 'last_login']
        read_only_fields = ['id']

class UserNameSerializer(serializers.ModelSerializer):
    """ List all user serializer """
    
    creator = serializers.SerializerMethodField('get_creator')

    class Meta:
        model = User
        fields = ['id', 'full_name', '']
        read_only_fields = ['id']

    def get_creator(self, obj):
        return CountrySerializer(instance=obj.created_by).data['full_name']
