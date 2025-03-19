from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from jobs.models import Vacancy

class Application(models.Model):
    student = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default="Ожидает рассмотрения")
    message = models.TextField()
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Заявка на вакансию {self.vacancy.title} от {self.student.username}"
