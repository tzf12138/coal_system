from django.db.models import Count
from django.shortcuts import render

from apps.core.models import Announcement, DashboardNote, ExpertKnowledge
from apps.equipment.models import ARSession, DiagnosisCase, Equipment
from apps.lifecycle.models import AcceptanceRecord, FillProject, ProjectTask
from apps.monitoring.models import AlertEvent, EnvironmentMetric, FillProcess, Sensor, VideoDevice
from apps.training.models import TrainingCourse, TrainingRecord


def home(request):
    context = {
        'announcements': Announcement.objects.all()[:5],
        'dashboard_notes': DashboardNote.objects.all()[:8],
        'processes': FillProcess.objects.all()[:6],
        'latest_alerts': AlertEvent.objects.select_related('process', 'sensor').all()[:8],
        'project_count': FillProject.objects.count(),
        'task_count': ProjectTask.objects.count(),
        'acceptance_count': AcceptanceRecord.objects.count(),
        'sensor_count': Sensor.objects.count(),
        'video_count': VideoDevice.objects.count(),
        'environment_count': EnvironmentMetric.objects.count(),
        'equipment_count': Equipment.objects.count(),
        'diagnosis_count': DiagnosisCase.objects.count(),
        'ar_count': ARSession.objects.count(),
        'training_count': TrainingCourse.objects.count(),
        'training_record_count': TrainingRecord.objects.count(),
        'knowledge_list': ExpertKnowledge.objects.all()[:6],
        'process_type_summary': FillProcess.objects.values('process_type').annotate(total=Count('id')),
    }
    return render(request, 'core/home.html', context)


def dashboard(request):
    process_count = FillProcess.objects.count()
    project_count = FillProject.objects.count()
    equipment_count = Equipment.objects.count()
    high_alert_count = AlertEvent.objects.filter(level__in=['high', 'critical']).count()

    process_summary = {item['process_type']: item['total'] for item in FillProcess.objects.values('process_type').annotate(total=Count('id'))}
    project_stage_summary = {item['stage']: item['total'] for item in FillProject.objects.values('stage').annotate(total=Count('id'))}

    context = {
        'process_count': process_count,
        'project_count': project_count,
        'equipment_count': equipment_count,
        'high_alert_count': high_alert_count,
        'online_sensor_count': Sensor.objects.filter(is_online=True).count(),
        'active_project_count': FillProject.objects.filter(stage__in=['construction', 'commissioning', 'operation']).count(),
        'healthy_equipment_count': Equipment.objects.filter(health_status__in=['excellent', 'good']).count(),
        'paste_process_count': process_summary.get('paste', 0),
        'tailings_process_count': process_summary.get('tailings', 0),
        'gangue_process_count': process_summary.get('gangue', 0),
        'stage_initiation_count': project_stage_summary.get('initiation', 0),
        'stage_design_count': project_stage_summary.get('design', 0),
        'stage_procurement_count': project_stage_summary.get('procurement', 0),
        'stage_construction_count': project_stage_summary.get('construction', 0),
        'stage_commissioning_count': project_stage_summary.get('commissioning', 0),
        'stage_acceptance_count': project_stage_summary.get('acceptance', 0),
        'stage_operation_count': project_stage_summary.get('operation', 0),
    }
    return render(request, 'core/dashboard.html', context)


def knowledge(request):
    context = {'knowledge_list': ExpertKnowledge.objects.all()}
    return render(request, 'core/knowledge.html', context)



def digital_twin(request):
    context = {
        'processes': FillProcess.objects.all(),
        'equipments': Equipment.objects.all(),
        'sensors': Sensor.objects.filter(is_online=True)[:12],
        'alerts': AlertEvent.objects.filter(resolved=False)[:6],
    }
    return render(request, 'core/digital_twin.html', context)


def ai_center(request):
    equipments = Equipment.objects.all()
    risk_items = []
    for item in equipments:
        risk_score = max(1, min(99, 100 - item.health_score + (8 if item.health_status in ['warning', 'danger'] else 0)))
        risk_items.append({
            'equipment': item,
            'risk_score': risk_score,
            'risk_level': '高' if risk_score >= 35 else '中' if risk_score >= 18 else '低',
        })
    context = {
        'risk_items': risk_items,
        'alert_count': AlertEvent.objects.filter(resolved=False).count(),
        'project_count': FillProject.objects.count(),
        'equipment_count': Equipment.objects.count(),
        'sensor_count': Sensor.objects.count(),
    }
    return render(request, 'core/ai_center.html', context)


def smart_control(request):
    context = {
        'processes': FillProcess.objects.all(),
        'sensors': Sensor.objects.select_related('process').all()[:16],
        'environment_list': EnvironmentMetric.objects.all(),
        'alerts': AlertEvent.objects.filter(resolved=False)[:8],
    }
    return render(request, 'core/smart_control.html', context)


def ar_guidance(request):
    context = {
        'cases': DiagnosisCase.objects.select_related('equipment').all(),
        'sessions': ARSession.objects.select_related('equipment').all(),
        'equipments': Equipment.objects.all(),
    }
    return render(request, 'core/ar_guidance.html', context)
