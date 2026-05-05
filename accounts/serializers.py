from rest_framework import serializers
from .models import User, ProfilePicture

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'phone_number', 'is_active', 'is_verified', 'is_staff', 'role', 'date_joined', 'updated_at', 'last_login']
        read_only_fields = ['id', 'date_joined', 'updated_at', 'last_login']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'phone_number', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfilePicture
        fields = ['id', 'user', 'image', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']