from django import forms
from .models import FillProcess, Sensor


class DateTimeLocalInput(forms.DateTimeInput):
    input_type = 'datetime-local'


class FillProcessForm(forms.ModelForm):
    class Meta:
        model = FillProcess
        fields = [
            'name', 'process_type', 'mine_name', 'status', 'design_capacity',
            'current_flow', 'concentration', 'pipeline_pressure', 'data_quality', 'remark'
        ]
        widgets = {
            'remark': forms.Textarea(attrs={'rows': 3}),
        }


class SensorForm(forms.ModelForm):
    class Meta:
        model = Sensor
        fields = [
            'process', 'name', 'sensor_type', 'code', 'location', 'unit',
            'current_value', 'threshold_low', 'threshold_high', 'is_online'
        ]
