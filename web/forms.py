from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, TeacherProfile, Course, Exam

class StudentRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        if commit:
            user.save()
        return user
    
class TeacherRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'teacher'
        if commit:
            user.save()
        return user
    
class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['name', 'room', 'office_hours', 'email']
        widgets = {
            'office_hours': forms.Textarea(attrs={'rows': 4}),
        }
        

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'short_description', 'long_description', 
                  'total_hours', 'schedule_time', 'room']
        widgets = {
            'short_description': forms.Textarea(attrs={'rows': 3}),
            'long_description': forms.Textarea(attrs={'rows': 6}),
        }

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title', 'date', 'location', 'duration_minutes', 'description']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }