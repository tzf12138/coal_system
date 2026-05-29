from collections import Counter

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from openpyxl import Workbook

from .forms import FillProjectForm, ProjectTaskForm
from .models import AcceptanceRecord, FillProject, Milestone, ProjectDocument, ProjectTask, RiskRecord


def project_list(request):
    context = {
        'projects': FillProject.objects.all(),
        'tasks': ProjectTask.objects.select_related('project').all()[:10],
    }
    return render(request, 'lifecycle/project_list.html', context)


def project_detail(request, pk):
    project = get_object_or_404(FillProject, pk=pk)
    tasks = project.tasks.all()
    milestones = project.milestones.all()
    documents = project.documents.all()
    risks = project.risks.all()
    acceptances = project.acceptances.all()

    counter = Counter(tasks.values_list('status', flat=True))
    context = {
        'project': project,
        'tasks': tasks,
        'milestones': milestones,
        'documents': documents,
        'risks': risks,
        'acceptances': acceptances,
        'todo_task_count': counter.get('todo', 0),
        'doing_task_count': counter.get('doing', 0),
        'completed_task_count': counter.get('done', 0),
        'delayed_task_count': counter.get('delayed', 0),
    }
    return render(request, 'lifecycle/project_detail.html', context)


def task_board(request):
    context = {'tasks': ProjectTask.objects.select_related('project').all()}
    return render(request, 'lifecycle/task_board.html', context)


def project_create(request):
    if request.method == 'POST':
        form = FillProjectForm(request.POST)
        if form.is_valid():
            obj = form.save()
            messages.success(request, '项目已创建。')
            return redirect('lifecycle:project_detail', pk=obj.pk)
    else:
        form = FillProjectForm()
    return render(request, 'shared/form.html', {'form': form, 'page_title': '新增项目', 'back_url': reverse('lifecycle:project_list')})


def project_update(request, pk):
    obj = get_object_or_404(FillProject, pk=pk)
    if request.method == 'POST':
        form = FillProjectForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save()
            messages.success(request, '项目已更新。')
            return redirect('lifecycle:project_detail', pk=obj.pk)
    else:
        form = FillProjectForm(instance=obj)
    return render(request, 'shared/form.html', {'form': form, 'page_title': '编辑项目', 'back_url': reverse('lifecycle:project_detail', kwargs={'pk': obj.pk})})


def project_delete(request, pk):
    obj = get_object_or_404(FillProject, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, '项目已删除。')
        return redirect('lifecycle:project_list')
    return render(request, 'shared/confirm_delete.html', {'page_title': '删除项目', 'object_name': obj.name, 'back_url': reverse('lifecycle:project_detail', kwargs={'pk': pk})})


def task_create(request, project_pk=None):
    initial = {'project': project_pk} if project_pk else None
    if request.method == 'POST':
        form = ProjectTaskForm(request.POST)
        if form.is_valid():
            obj = form.save()
            messages.success(request, '任务已新增。')
            return redirect('lifecycle:project_detail', pk=obj.project_id)
    else:
        form = ProjectTaskForm(initial=initial)
    back_url = reverse('lifecycle:project_detail', kwargs={'pk': project_pk}) if project_pk else reverse('lifecycle:task_board')
    return render(request, 'shared/form.html', {'form': form, 'page_title': '新增项目任务', 'back_url': back_url})


def task_update(request, pk):
    obj = get_object_or_404(ProjectTask, pk=pk)
    if request.method == 'POST':
        form = ProjectTaskForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save()
            messages.success(request, '任务已更新。')
            return redirect('lifecycle:project_detail', pk=obj.project_id)
    else:
        form = ProjectTaskForm(instance=obj)
    return render(request, 'shared/form.html', {'form': form, 'page_title': '编辑项目任务', 'back_url': reverse('lifecycle:project_detail', kwargs={'pk': obj.project_id})})


def task_delete(request, pk):
    obj = get_object_or_404(ProjectTask, pk=pk)
    back_pk = obj.project_id
    if request.method == 'POST':
        obj.delete()
        messages.success(request, '任务已删除。')
        return redirect('lifecycle:project_detail', pk=back_pk)
    return render(request, 'shared/confirm_delete.html', {'page_title': '删除项目任务', 'object_name': obj.title, 'back_url': reverse('lifecycle:project_detail', kwargs={'pk': back_pk})})


def export_project_tasks_excel(request, pk):
    project = get_object_or_404(FillProject, pk=pk)
    tasks = project.tasks.all().order_by('id')

    wb = Workbook()
    ws = wb.active
    ws.title = '项目任务'
    ws.append(['项目名称', project.name])
    ws.append(['项目编号', project.code])
    ws.append(['实施矿井', project.mine_name])
    ws.append(['项目负责人', project.owner])
    ws.append([])
    ws.append(['任务名称', '责任人', '阶段', '状态', '进度', '开始日期', '截止日期', '备注'])

    for task in tasks:
        ws.append([
            task.title,
            task.owner,
            task.stage,
            task.get_status_display(),
            f'{task.progress}%',
            str(task.start_date) if task.start_date else '',
            str(task.due_date) if task.due_date else '',
            task.remark or '',
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{project.code}_任务清单.xlsx"'
    wb.save(response)
    return response
