from django.urls import path
from .views import (
    export_project_tasks_excel, project_create, project_delete, project_detail,
    project_list, project_update, task_board, task_create, task_delete, task_update,
)

app_name = 'lifecycle'

urlpatterns = [
    path('', project_list, name='project_list'),
    path('create/', project_create, name='project_create'),
    path('project/<int:pk>/', project_detail, name='project_detail'),
    path('project/<int:pk>/edit/', project_update, name='project_update'),
    path('project/<int:pk>/delete/', project_delete, name='project_delete'),
    path('project/<int:pk>/export-tasks-excel/', export_project_tasks_excel, name='export_project_tasks_excel'),
    path('project/<int:project_pk>/task/create/', task_create, name='task_create_for_project'),
    path('tasks/', task_board, name='task_board'),
    path('task/create/', task_create, name='task_create'),
    path('task/<int:pk>/edit/', task_update, name='task_update'),
    path('task/<int:pk>/delete/', task_delete, name='task_delete'),
]
