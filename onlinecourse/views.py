from django.shortcuts import get_object_or_404, redirect, render

from .models import Choice, Course, Learner, Submission


PASSING_SCORE = 70


def index(request):
    courses = Course.objects.all().order_by('name')
    return render(request, 'onlinecourse/index.html', {'courses': courses})


def course_details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return render(request, 'onlinecourse/course_details_bootstrap.html', {'course': course})


def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method != 'POST':
        return redirect('onlinecourse:course_details', course_id=course.id)

    learner = None
    if request.user.is_authenticated:
        learner, _ = Learner.objects.get_or_create(user=request.user)

    selected_choice_ids = request.POST.getlist('choice')
    selected_choices = Choice.objects.filter(id__in=selected_choice_ids)
    submission = Submission.objects.create(course=course, learner=learner)
    submission.choices.set(selected_choices)
    return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)


def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id, course=course)
    selected_choice_ids = set(submission.choices.values_list('id', flat=True))
    questions = []
    earned_points = 0
    total_points = 0

    for lesson in course.lessons.prefetch_related('questions__choices'):
        for question in lesson.questions.all():
            correct_ids = set(question.choices.filter(is_correct=True).values_list('id', flat=True))
            selected_ids = set(question.choices.filter(id__in=selected_choice_ids).values_list('id', flat=True))
            is_correct = selected_ids == correct_ids
            total_points += question.grade
            if is_correct:
                earned_points += question.grade
            questions.append({
                'question': question,
                'choices': question.choices.all(),
                'selected_ids': selected_ids,
                'correct_ids': correct_ids,
                'is_correct': is_correct,
            })

    score = round((earned_points / total_points) * 100) if total_points else 0
    context = {
        'course': course,
        'submission': submission,
        'questions': questions,
        'earned_points': earned_points,
        'total_points': total_points,
        'score': score,
        'passed': score >= PASSING_SCORE,
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)

# Create your views here.
