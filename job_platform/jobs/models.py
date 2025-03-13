from django.db import models

class Job(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    company = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
