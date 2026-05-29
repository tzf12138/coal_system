from django import forms
from .models import Equipment, MaintenanceOrder


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = [
            'name', 'code', 'category', 'mine_name', 'location', 'health_status',
            'health_score', 'runtime_hours', 'next_maintenance_date'
        ]
        widgets = {
            'next_maintenance_date': forms.DateInput(attrs={'type': 'date'}),
        }


class MaintenanceOrderForm(forms.ModelForm):
    class Meta:
        model = MaintenanceOrder
        fields = [
            'equipment', 'title', 'priority', 'status', 'assignee', 'summary'
        ]
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 3}),
        }
