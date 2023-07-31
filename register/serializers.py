from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from rest_framework import serializers
from .models import CustomUser as User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone_number', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            name=validated_data['name'],
            phone_number=validated_data['phone_number'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        token = Token.objects.create(user=user)
        print("token ",token)
        # Save the token
        token.save()

        return user,token
