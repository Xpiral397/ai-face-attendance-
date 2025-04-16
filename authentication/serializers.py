from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User  # Removed StudentProfile, LecturerProfile

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model"""
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'full_name', 'role', 'active']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user and user.is_active:
            data['user'] = user
            return data
        raise serializers.ValidationError("Invalid credentials")

# Commented out for initial migration
# class StudentProfileSerializer(serializers.ModelSerializer):
#     """Serializer for the StudentProfile model"""
#     user = UserSerializer(read_only=True)
#     
#     class Meta:
#         model = StudentProfile
#         fields = ['id', 'user', 'department', 'level', 'matric_number', 'courses']
# 
# class LecturerProfileSerializer(serializers.ModelSerializer):
#     """Serializer for the LecturerProfile model"""
#     user = UserSerializer(read_only=True)
#     
#     class Meta:
#         model = LecturerProfile
#         fields = ['id', 'user', 'departments', 'levels', 'subjects'] 