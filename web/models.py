from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

class User(AbstractUser):
    ROLES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )

    role = models.CharField(max_length=10, choices=ROLES)
    
    class Meta:
        db_table = 'auth_user'

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    name = models.CharField(verbose_name='Name', max_length=200)
    room = models.CharField(verbose_name='Raum', max_length=50)
    office_hours = models.TextField(verbose_name='Sprechstunde',help_text="Sprechstundenzeiten")
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Course(models.Model):
    title = models.CharField(verbose_name='Titel',
                             max_length=200, 
                             help_text='Kursname')
    
    short_description = models.CharField(verbose_name='Kurzbeschreibung',
                                         max_length=500, 
                                         help_text='Kurzbeschreibung')
    
    long_description = models.TextField(verbose_name='Beschreibung',
                                        help_text='Ausführliche Beschreibung')
    
    total_hours = models.PositiveIntegerField(verbose_name='Gesamtaufwand',
                                              validators=[MinValueValidator(1)], 
                                              help_text='Gesamtaufwand')
    
    schedule_time = models.CharField(max_length=200, 
                                     help_text='Kurszeiten')
    
    room = models.CharField(verbose_name='Raum',
                            max_length=50, 
                            help_text='Raum')
    
    teacher = models.ForeignKey(TeacherProfile, 
                                on_delete=models.CASCADE, 
                                related_name='courses')

    students = models.ManyToManyField(User, 
                                      related_name='enrolled_courses', 
                                      blank=True, 
                                      limit_choices_to={'role':'student'})
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
1
class Exam(models.Model):
    course = models.ForeignKey(Course, 
                               on_delete=models.CASCADE, 
                               related_name='exams', 
                               help_text='zugehöriger Kurs')
    
    title = models.CharField(max_length=200, 
                             help_text='Prüfungstitel')
    
    date = models.DateTimeField(help_text='Prüfungsdatum und Uhrzeit')

    location = models.CharField(max_length=200, 
                                help_text='Ort der Prüfung')
    
    duration_minutes = models.IntegerField(validators=[MinValueValidator(1)], 
                                           help_text='Dauer in Minuten')

    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title} - {self.course.title}'
    
    class Meta:
        ordering = ['date']