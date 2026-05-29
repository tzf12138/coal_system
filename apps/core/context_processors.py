from apps.monitoring.models import Sensor, AlertEvent, FillProcess
from apps.lifecycle.models import FillProject
from apps.equipment.models import Equipment, DiagnosisCase

def global_stats(request):
    return {
        'nav_sensor_count': Sensor.objects.count(),
        'nav_alert_count': AlertEvent.objects.filter(level__in=['high', 'critical'], resolved=False).count(),
        'nav_project_count': FillProject.objects.count(),
        'nav_equipment_count': Equipment.objects.count(),
        'nav_case_count': DiagnosisCase.objects.count(),
        'nav_process_count': FillProcess.objects.count(),
    }
