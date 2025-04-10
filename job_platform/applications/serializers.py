from rest_framework import serializers
from .models import *

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'

    def validate_status(self, value):
        valid_statuses = ['Ожидает рассмотрения', 'Принята', 'Отклонена']
        if value not in valid_statuses:
            raise serializers.ValidationError("Недопустимый статус заявки.")
        return value

    def validate_message(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Сообщение должно быть не менее 10 символов.")
        return value

    def validate_resume(self, value):
        if value and value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Размер файла не должен превышать 5 МБ.")
        return value

    def validate(self, data):
        if data['vacancy'].employer == data['student']:
            raise serializers.ValidationError("Студент не может подать заявку на свою собственную вакансию.")
        return data

class InterviewCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewCalendar
        fields = '__all__'


class CoverLetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoverLetter
        fields = '__all__'