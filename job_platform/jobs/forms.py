from django import forms
from applications.models import Application
from jobs.models import Review, Rating, Vacancy, ReviewEmployer

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['message', 'resume']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, str(i)) for i in range(1, 6)], attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'rating': 'Оценка',
            'comment': 'Комментарий',
        }


class ReviewEmployerForm(forms.ModelForm):
    class Meta:
        model = ReviewEmployer
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
        }


class RatingForm(forms.Form):
    rating = forms.ChoiceField(choices=[(1, '1 - Очень плохо'), (2, '2 - Плохо'), (3, '3 - Средне'), (4, '4 - Хорошо'), (5, '5 - Отлично')], widget=forms.RadioSelect)

class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = ['title', 'description', 'city', 'salary_min', 'salary_max', 'currency', 'deadline']
