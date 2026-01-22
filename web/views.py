from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import User, TeacherProfile, Course, Exam

from .forms import (StudentRegistrationForm, TeacherRegistrationForm, 
                    TeacherProfileForm, CourseForm, ExamForm)

def home(request):
    return render(request, 'web/home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.role == 'student':
                return redirect('student_dashboard')
            elif user.role == 'teacher':
                return redirect('teacher_dashboard')
        else:
            messages.error(request, 
                           'Unbekannter Benutzername oder falsches Passwort.')
    
    return render(request, 'web/login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        role = request.POST.get('role')
        
        if role == 'student':
            form = StudentRegistrationForm(request.POST)
        elif role == 'teacher':
            form = TeacherRegistrationForm(request.POST)
        else:
            messages.error(request, 'Please select a valid role.')
            return render(request, 'web/register.html')
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome!')
            
            if role == 'student':
                return redirect('student_dashboard')
            else:
                return redirect('teacher_profile_create')
        else:
            return render(request, 'web/register.html', {'form': form, 'role': role})
    
    return render(request, 'web/register.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Sie wurden erfolgreich abgemeldet.')
    return redirect('login')

# Student views
@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('teacher_dashboard')

    enrolled_courses = request.user.enrolled_courses.all()
    return render(request, 'web/student_dashboard.html',{
        'enrolled_courses': enrolled_courses
    })

@login_required
def course_list(request):
    if request.user.role != 'student':
        return redirect('teacher_dashboard')
    
    search_query = request.GET.get('search', '')
    courses = Course.objects.all()

    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(teacher__name__icontains=search_query)
        )
    
    return render(request, 'web/course_list.html', {
        'courses':courses,
        'search_query':search_query
    })

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    is_enrolled = request.user.role == 'student' and request.user in course.students.all()

    return render(request, 'web/course_detail.html', {
        'course': course,
        'is_enrolled': is_enrolled
    })

@login_required
def enroll_course(request, course_id):
    if request.user.role != 'student':
        messages.error(request, 'Nur Studenten können sich in Kurse einschreiben.')
        return redirect('home')
    
    course = get_object_or_404(Course, id=course_id)

    if request.user in course.students.all():
        messages.warning(request, 'Sie sind bereits in diesem Kurs eingeschrieben.')
    else:
        course.students.add(request.user)
        messages.success(request, f'Sie haben sich erfolgreich in den Kurs "{course.title}" eingeschrieben.')
    
    return redirect('course_detail', course_id=course_id)

@login_required
def unenroll_course(request, course_id):
    if request.user.role != 'student':
        messages.error(request, 'Nur Studenten können sich aus Kursen austragen.')
        return redirect('home')

    course = get_object_or_404(Course, id=course_id)

    if request.user not in course.students.all():
        messages.warning(request, 'Sie sind in diesem Kurs nicht eingeschrieben.')
    else:
        course.students.remove(request.user)
        messages.success(request, f'Sie haben sich erfolgreich aus dem Kurs "{course.title}" ausgetragen.')

    return redirect('student_dashboard')

@login_required
def student_timetable(request):
    if request.user.role != 'student':
        return redirect('teacher_dashboard')
    
    enrolled_courses = request.user.enrolled_courses.all()
    
    # Time slots (2-hour blocks from 6:00 to 22:00)
    time_slots = ['06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00']
    
    # Initialize schedule structure
    schedule_by_slots = {}
    for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
        schedule_by_slots[day] = {}
        for slot in time_slots:
            schedule_by_slots[day][slot] = {'courses': [], 'spans': {}, 'skip': False}
    
    # Day name mappings (German to English keys)
    day_mappings = {
        'montag': 'monday',
        'dienstag': 'tuesday', 
        'mittwoch': 'wednesday',
        'donnerstag': 'thursday',
        'freitag': 'friday',
        'samstag': 'saturday',
        'sonntag': 'sunday',
        # Also support English names for backward compatibility
        'monday': 'monday',
        'tuesday': 'tuesday',
        'wednesday': 'wednesday',
        'thursday': 'thursday',
        'friday': 'friday',
        'saturday': 'saturday',
        'sunday': 'sunday'
    }
    
    import re
    
    for course in enrolled_courses:
        if not course.schedule_time:
            continue
        
        # Split by semicolon for multiple schedule entries
        schedule_entries = course.schedule_time.split(';')
        
        for schedule_entry in schedule_entries:
            schedule_entry = schedule_entry.strip()
            
            # Parse format: "Monday 10:00-12:00"
            match = re.match(r'(\w+)\s+(\d{2}):(\d{2})-(\d{2}):(\d{2})', schedule_entry, re.IGNORECASE)
            
            if match:
                day_name = match.group(1).lower()
                start_hour = int(match.group(2))
                start_min = match.group(3)
                end_hour = int(match.group(4))
                end_min = match.group(5)
                
                # Map day name to key
                day_key = day_mappings.get(day_name)
                
                if day_key:
                    # Find which time slots this course overlaps
                    overlapping_slots = []
                    for slot in time_slots:
                        slot_hour = int(slot.split(':')[0])
                        slot_end_hour = slot_hour + 2
                        
                        # Check if course overlaps with this time slot
                        if start_hour < slot_end_hour and end_hour > slot_hour:
                            overlapping_slots.append(slot)
                    
                    # Only add course to the first overlapping slot
                    if overlapping_slots:
                        first_slot = overlapping_slots[0]
                        span_count = len(overlapping_slots)
                        
                        # Add course to first slot with span info
                        if course not in schedule_by_slots[day_key][first_slot]['courses']:
                            schedule_by_slots[day_key][first_slot]['courses'].append(course)
                            schedule_by_slots[day_key][first_slot]['spans'][course.id] = span_count
                        
                        # Mark subsequent slots to skip rendering
                        for skip_slot in overlapping_slots[1:]:
                            schedule_by_slots[day_key][skip_slot]['skip'] = True
    
    return render(request, 'web/student_timetable.html', {
        'enrolled_courses': enrolled_courses,
        'schedule': schedule_by_slots,
        'time_slots': time_slots
    })

@login_required
def teacher_search(request):
    if request.user.role != 'student':
        return redirect('teacher_dashboard')
    
    search_query = request.GET.get('search', '')
    teachers = TeacherProfile.objects.all()

    if search_query:
        teachers = teachers.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    return render(request, 'web/teacher_search.html', {
        'teachers': teachers,
        'search_query': search_query
    })

@login_required
def teacher_profile_view(request, profile_id):
    teacher_profile = get_object_or_404(TeacherProfile, id=profile_id)
    courses = teacher_profile.courses.all()

    return render(request, 'web/teacher_profile_view.html', {
        'teacher_profile': teacher_profile,
        'courses': courses
    })

@login_required
def student_exams(request):
    if request.user.role != 'student':
        return redirect('teacher_dashboard')
    
    # Get all courses the student is enrolled in
    enrolled_courses = request.user.enrolled_courses.all()
    
    # Get all exams for those courses
    exams = Exam.objects.filter(course__in=enrolled_courses).order_by('date')
    
    return render(request, 'web/student_exams.html', {
        'exams': exams
    })

# Teacher views
@login_required
def teacher_dashboard(request):
    if request.user.role != 'teacher':
        return redirect('student_dashboard')
    
    try:
        profile = request.user.teacher_profile
        courses = profile.courses.all()
    except TeacherProfile.DoesNotExist:
        profile = None
        courses = []
    
    return render(request, 'web/teacher_dashboard.html', {
        'profile': profile,
        'courses': courses
    })

@login_required
def teacher_profile_create(request):
    if request.user.role != 'teacher':
        messages.error(request, 'Nur Dozierende können ein Profil erstellen.')
        return redirect('home')
    
    try:
        profile = request.user.teacher_profile
        messages.info(request, 'Sie haben bereits ein Profil, das Sie bearbeiten können.')
        return redirect('teacher_profile_edit')
    
    except TeacherProfile.DoesNotExist:
        pass

    if request.method == 'POST':
        form = TeacherProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Ihr Profil wurde erfolgreich erstellt.')
            return redirect('teacher_dashboard')
        
    else:
        form = TeacherProfileForm()

    return render(request, 'web/teacher_profile_form.html', {
        'form': form,
        'action': 'Create'
    })

@login_required
def teacher_exams(request):
    if request.user.role != 'teacher':
        return redirect('student_dashboard')
    
    try:
        profile = request.user.teacher_profile
        # Get all exams from all courses taught by this teacher
        exams = Exam.objects.filter(course__teacher=profile).order_by('date')
    except TeacherProfile.DoesNotExist:
        messages.error(request, 'Bitte erstelle zuerst ein Profil.')
        return redirect('teacher_profile_create')
    
    return render(request, 'web/teacher_exams.html', {
        'exams': exams,
        'profile': profile
    })

@login_required
def teacher_profile_edit(request):
    if request.user.role != 'teacher':
        messages.error(request, 'Nur Dozierende können ihr Profil bearbeiten.')
        return redirect('home')
    
    try:
        profile = request.user.teacher_profile
    except TeacherProfile.DoesNotExist:
        messages.error(request, 'Bitte erstellen Sie zuerst ein Profil.')
        return redirect('teacher_profile_create')
    
    if request.method == 'POST':
        form = TeacherProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ihr Profil wurde erfolgreich aktualisiert.')
            return redirect('teacher_dashboard')
        
    else:
        form = TeacherProfileForm(instance=profile)

    return render(request, 'web/teacher_profile_form.html', {
        'form': form,
        'action': 'Edit'
    })

@login_required
def course_create(request):
    if request.user.role != 'teacher':
        messages.error(request, 'Nur Dozierende können Kurse erstellen.')
        return redirect('home')
    
    try:
        profile = request.user.teacher_profile
    except TeacherProfile.DoesNotExist:
        messages.error(request, 'Sie müssen zuerst ein Profil erstellen.')
        return redirect('teacher_profile_create')
    
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = profile
            course.save()
            messages.success(request, 'Der Kurs wurde erfolgreich erstellt.')
            return redirect('teacher_dashboard')
    else:
        form = CourseForm()
    
    return render(request, 'web/course_form.html', {
        'form': form,
        'action': 'Create'
    })

@login_required
def course_edit(request, course_id):
    if request.user.role != 'teacher':
        messages.error(request, 'Nur Dozierende können Kurse bearbeiten.')
        return redirect('home')
    
    course = get_object_or_404(Course, id=course_id)

    if course.teacher.user != request.user:
        messages.error(request, 'Sie können nur Ihre eigenen Kurse bearbeiten.')
        return redirect('teacher_dashboard')
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Der Kurs wurde erfolgreich aktualisiert.')
            return redirect('teacher_dashboard')
    else:
        form = CourseForm(instance=course)
    
    return render(request, 'web/course_form.html', {
        'form':form,
        'action':'Edit',
        'course':course
    })

@login_required
def course_delete(request, course_id):
    if request.user.role != 'teacher':
        messages.error(request, 'Nur Dozierende können Kurse löschen.')
        return redirect('home')
    
    course = get_object_or_404(Course, id=course_id)

    if course.teacher.user != request.user:
        messages.error(request, 'Sie können nur Ihre eigenen Kurse löschen.')
        return redirect('teacher_dashboard')
    
    if request.method == 'POST':
        course.title = course.title
        course.delete()
        messages.success(request, f'Der Kurs "{course.title}" wurde erfolgreich gelöscht.')
        return redirect('teacher_dashboard')
    
    return render(request, 'web/course_confirm_delete.html', {'course':course})

@login_required
def teacher_courses(request):
    if request.user.role != 'teacher':
        return redirect('student_dashboard')
    
    try:
        profile = request.user.teacher_profile
        courses = profile.courses.all().order_by('-created_at')
    except TeacherProfile.DoesNotExist:
        messages.error(request, 'Bitte erstelle zuerst ein Profil.')
        return redirect('teacher_profile_create')
    
    return render(request, 'web/teacher_courses.html', {
        'courses': courses,
        'profile': profile
    })

@login_required
def exam_create(request, course_id):
    if request.user.role != 'teacher':
        messages.error(request, 'Nur Dozierende können Prüfungen erstellen.')
        return redirect('home')
    
    course = get_object_or_404(Course, id=course_id)

    if course.teacher.user != request.user:
        messages.error(request, 'Sie können nur Prüfungen für Ihre eigenen Kurse erstellen.')
        return redirect('teacher_dashboard')
    
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.course = course
            exam.save()
            messages.success(request, 'Die Prüfung wurde erfolgreich erstellt.')
            return redirect('teacher_dashboard')
        
    else:
        form = ExamForm()

    return render(request, 'web/exam_form.html', {
        'form': form,
        'action':'Create',
        'course':course
    })

@login_required
def exam_delete(request, exam_id):
    if request.user.role != 'teacher':
        messages.error(request, 'Nur Dozierende können Prüfungen löschen.')
        return redirect('home')
    
    exam = get_object_or_404(Exam, id=exam_id)
    
    if exam.course.teacher.user != request.user:
        messages.error(request, 'Sie können nur Prüfungen für Ihre eigenen Kurse löschen.')
        return redirect('teacher_dashboard')
    
    if request.method == 'POST':
        exam_title = exam.title
        exam.delete()
        messages.success(request, f'Die Prüfung "{exam_title}" wurde erfolgreich gelöscht.')
        return redirect('teacher_dashboard')
    
    return render(request,'web/exam_confirm_delete.html', {'exam':exam})