from django.contrib import admin
from jobs.models import Vacancy, Review, ReviewEmployer

admin.site.register(Vacancy)
admin.site.register(Review)
admin.site.register(ReviewEmployer)