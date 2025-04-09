from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

class Vacancy(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    city = models.CharField(max_length=100, default="Unknown")
    salary_min = models.PositiveIntegerField(default="0")
    salary_max = models.PositiveIntegerField(default="0")
    currency = models.CharField(max_length=10, choices=[("RUB", "₽"), ("USD", "$"), ("EUR", "€")], default="RUB")
    deadline = models.DateField(default="2025-12-31")
    employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Review(models.Model):
    student = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    employer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='received_reviews')
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Отзыв от {self.student.username} о работодателе {self.employer.username} для вакансии {self.vacancy.title}"


class ReviewEmployer(models.Model):
    employer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='employer_reviews')
    student = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='student_reviews')
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employer', 'student', 'vacancy')

    def __str__(self):
        return f"Отзыв работодателя {self.employer.username} о студенте {self.student.username} по вакансии {self.vacancy.title}"


class Rating(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    job = models.ForeignKey('jobs.Vacancy', on_delete=models.CASCADE)
    employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_ratings')
    rating = models.IntegerField(choices=[(1, '1 - Очень плохо'), (2, '2 - Плохо'), (3, '3 - Средне'), (4, '4 - Хорошо'), (5, '5 - Отлично')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Rating from {self.student} about {self.employer} and {self.job}'
