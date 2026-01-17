from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, TeacherProfile, Course, Exam

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role', {'fields':('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role', {'fields':('role',)}),
    )

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'room', 'user']
    search_fields = ['name', 'email']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'schedule_time', 'room', 'total_hours']
    list_filter = ['teacher']
    search_fields = ['title', 'teacher__name']
    filter_horizontal = ['students']

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'date', 'location', 'duration_minutes']
    list_filter = ['course', 'date']
    search_fields = ['title', 'course__title']