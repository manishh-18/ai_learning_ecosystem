from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Course, Enrollment, CourseVideo
from apps.assessments.models import Quiz
from .forms import CourseForm


@login_required
def create_course(request):
    if request.user.role != 'instructor':
        return redirect('home')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            return redirect('instructor_dashboard')
    else:
        form = CourseForm()

    return render(request, 'courses/create_course.html', {'form': form})


@login_required
def course_list(request):
    courses = Course.objects.all()

    enrolled = Enrollment.objects.filter(user=request.user)
    enrolled_courses = [e.course.id for e in enrolled]

    return render(request, 'courses/list.html', {
        'courses': courses,
        'enrolled_courses': enrolled_courses
    })

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    Enrollment.objects.get_or_create(
        user=request.user,
        course=course
    )

    return redirect('course_detail', course_id=course.id)

from .models import CourseMaterial
@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # check enrollment
    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        return redirect('course_list')


    from .models import CourseMaterial, CourseVideo
    from apps.assessments.models import Quiz

    materials = CourseMaterial.objects.filter(course=course)
    videos = CourseVideo.objects.filter(course=course)
    quizzes = Quiz.objects.filter(course=course)

    return render(request, 'courses/detail.html', {
        'course': course,
        'documents': materials,
        'videos' : videos,
        'quizzes': quizzes
    })

@login_required
def manage_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)

    materials = CourseMaterial.objects.filter(course=course)
    videos = CourseVideo.objects.filter(course=course)
    quizzes = Quiz.objects.filter(course=course)

    return render(request, 'courses/manage_course.html', {
        'course': course,
        'materials': materials,
        'videos': videos,
        'quizzes': quizzes
    })

@login_required
def add_material(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)

    if request.method == 'POST':
        title = request.POST.get('title')
        file = request.FILES.get('file')

        CourseMaterial.objects.create(
            course=course,
            title=title,
            file=file
        )
        return redirect('manage_course', course_id=course.id)

    return render(request, 'courses/add_material.html', {'course': course})

@login_required
def add_video(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)

    if request.method == 'POST':
        title = request.POST.get('title')
        url = request.POST.get('video_url')

        CourseVideo.objects.create(
            course=course,
            title=title,
            video_url=url
        )
        return redirect('manage_course', course_id=course.id)

    return render(request, 'courses/add_video.html', {'course': course})