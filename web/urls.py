from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    #Students
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/courses/', views.course_list, name='course_list'),
    path('student/courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('student/courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('student/courses/<int:course_id>/unenroll/', views.unenroll_course, name='unenroll_course'),
    path('student/timetable/', views.student_timetable, name='student_timetable'),
    path('student/teachers/', views.teacher_search, name='teacher_search'),
    path('student/teachers/<int:profile_id>/', views.teacher_profile_view, name='teacher_profile_view'),

    #Teachers
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/profile/create/', views.teacher_profile_create, name='teacher_profile_create'),
    path('teacher/profile/edit/', views.teacher_profile_edit, name='teacher_profile_edit'),
    path('teacher/courses/create/', views.course_create, name='course_create'),
    path('teacher/courses/<int:course_id>/edit/', views.course_edit, name='course_edit'),
    path('teacher/courses/<int:course_id>/delete/', views.course_delete, name='course_delete'),
    path('teacher/courses/<int:course_id>/exams/create/', views.exam_create, name='exam_create'),
    path('teacher/exams/<int:exam_id>/delete/', views.exam_delete, name='exam_delete'),
]
