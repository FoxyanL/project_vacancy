from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Application
from .serializers import ApplicationSerializer
from jobs.models import Vacancy
from jobs.serializers import VacancySerializer
from django.db import models
from django.conf import settings
from rest_framework import viewsets

class StudentApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(student=self.request.user)

class EmployerVacanciesView(generics.ListAPIView):
    serializer_class = VacancySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Vacancy.objects.filter(employer=self.request.user)

class ApplicationView(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено')
    ], default='pending')

    def __str__(self):
        return f"{self.student.username} -> {self.vacancy.title} ({self.status})"

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)
