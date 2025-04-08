from rest_framework import serializers
from django.contrib.auth.models import User
from users.models import Profile
from django.contrib.auth import get_user_model

User = get_user_model()

class UserUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(min_length=3, max_length=150)

    class Meta:
        model = User
        fields = ['username', 'email']

    def validate_username(self, value):
        if value.isdigit():
            raise serializers.ValidationError("Имя пользователя не может состоять только из цифр.")
        return value

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio', 'location']

    def validate_bio(self, value):
        if len(value) > 500:
            raise serializers.ValidationError("Биография не должна превышать 500 символов.")
        return value

    def validate_location(self, value):
        if any(char.isdigit() for char in value):
            raise serializers.ValidationError("Локация не должна содержать цифры.")
        return value
