from rest_framework import serializers
from .models import Vacancy

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
