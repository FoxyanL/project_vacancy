from rest_framework import serializers
from django.contrib.auth.models import User
from users.models import Profile
from django.contrib.auth import get_user_model
from jobs.models import Vacancy, Review, ReviewEmployer
from users.models import Notification
from jobs.models import Rating

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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user', 'bio', 'location', 'role']

    def validate_role(self, value):
        valid_roles = ['student', 'employer']
        if value not in valid_roles:
            raise serializers.ValidationError("Недопустимая роль.")
        return value

    def validate_bio(self, value):
        if len(value) > 500:
            raise serializers.ValidationError("Биография не должна превышать 500 символов.")
        return value

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Рейтинг должен быть от 1 до 5.")
        return value

    def validate_comment(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Комментарий должен быть не менее 10 символов.")
        return value

class ReviewEmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewEmployer
        fields = '__all__'

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Рейтинг должен быть от 1 до 5.")
        return value

    def validate_comment(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Комментарий должен быть не менее 10 символов.")
        return value

class VacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = '__all__'

    def validate_salary_min(self, value):
        if value < 0:
            raise serializers.ValidationError("Минимальная зарплата не может быть меньше 0.")
        return value

    def validate_salary_max(self, value):
        if value < 0:
            raise serializers.ValidationError("Максимальная зарплата не может быть меньше 0.")
        return value

    def validate(self, data):
        if data['salary_min'] > data['salary_max']:
            raise serializers.ValidationError("Минимальная зарплата не может быть больше максимальной.")
        return data

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

    def validate_message(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Сообщение должно быть не менее 10 символов.")
        return value

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Рейтинг должен быть от 1 до 5.")
        return value
