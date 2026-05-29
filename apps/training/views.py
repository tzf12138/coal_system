from django.shortcuts import render
from .models import TrainingCourse, TrainingRecord

def course_list(request):
    context = {
        'courses': TrainingCourse.objects.all(),
        'records': TrainingRecord.objects.select_related('course').all()[:10],
    }
    return render(request, 'training/course_list.html', context)
