from django import forms
from .models import FillProject, ProjectTask


class FillProjectForm(forms.ModelForm):
    class Meta:
        model = FillProject
        fields = [
            'name', 'code', 'owner', 'mine_name', 'stage', 'budget', 'progress',
            'start_date', 'end_date', 'description'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ProjectTaskForm(forms.ModelForm):
    class Meta:
        model = ProjectTask
        fields = [
            'project', 'title', 'owner', 'stage', 'status', 'progress',
            'start_date', 'due_date', 'remark'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'remark': forms.Textarea(attrs={'rows': 3}),
        }
