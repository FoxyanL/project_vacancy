from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from jobs.models import Vacancy
from django.conf import settings

class Application(models.Model):
    student = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default="Ожидает рассмотрения")
    message = models.TextField(null=True, blank=True, default='')
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Заявка на вакансию {self.vacancy.title} от {self.student.username}"
    
class InterviewCalendar(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interviews')
    application = models.ForeignKey('applications.Application', on_delete=models.CASCADE, related_name='interview_entries')
    interview_date = models.DateTimeField()

    def __str__(self):
        return f"Собеседование {self.user.username} на {self.interview_date.strftime('%Y-%m-%d %H:%M')}"

class CoverLetter(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cover_letters')
    vacancy = models.ForeignKey('jobs.Vacancy', on_delete=models.CASCADE, related_name='cover_letters')
    message = models.TextField()
    resume_attached = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Сопроводительное письмо от {self.user.username} к вакансии {self.vacancy.title}"


