import random

from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from openpyxl import Workbook

from .forms import EquipmentForm, MaintenanceOrderForm
from .models import ARSession, DiagnosisCase, Equipment, InspectionRecord, MaintenanceOrder


def equipment_list(request):
    context = {
        'equipments': Equipment.objects.all(),
        'orders': MaintenanceOrder.objects.all()[:10],
    }
    return render(request, 'equipment/equipment_list.html', context)


def equipment_detail(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    context = {
        'equipment': equipment,
        'plans': equipment.sensor_plans.all(),
        'inspections': equipment.inspections.all()[:10],
        'orders': equipment.orders.all(),
        'cases': equipment.cases.all(),
        'ar_sessions': equipment.ar_sessions.all(),
    }
    return render(request, 'equipment/equipment_detail.html', context)


def diagnosis_center(request):
    context = {
        'cases': DiagnosisCase.objects.select_related('equipment').all(),
        'sessions': ARSession.objects.select_related('equipment').all(),
    }
    return render(request, 'equipment/diagnosis_center.html', context)


def equipment_create(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            obj = form.save()
            messages.success(request, '设备已创建。')
            return redirect('equipment:equipment_detail', pk=obj.pk)
    else:
        form = EquipmentForm()
    return render(request, 'shared/form.html', {'form': form, 'page_title': '新增设备', 'back_url': reverse('equipment:equipment_list')})


def equipment_update(request, pk):
    obj = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        form = EquipmentForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save()
            messages.success(request, '设备已更新。')
            return redirect('equipment:equipment_detail', pk=obj.pk)
    else:
        form = EquipmentForm(instance=obj)
    return render(request, 'shared/form.html', {'form': form, 'page_title': '编辑设备', 'back_url': reverse('equipment:equipment_detail', kwargs={'pk': obj.pk})})


def equipment_delete(request, pk):
    obj = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, '设备已删除。')
        return redirect('equipment:equipment_list')
    return render(request, 'shared/confirm_delete.html', {'page_title': '删除设备', 'object_name': obj.name, 'back_url': reverse('equipment:equipment_detail', kwargs={'pk': pk})})


def order_create(request, equipment_pk=None):
    initial = {'equipment': equipment_pk} if equipment_pk else None
    if request.method == 'POST':
        form = MaintenanceOrderForm(request.POST)
        if form.is_valid():
            obj = form.save()
            messages.success(request, '维修工单已新增。')
            return redirect('equipment:equipment_detail', pk=obj.equipment_id)
    else:
        form = MaintenanceOrderForm(initial=initial)
    back_url = reverse('equipment:equipment_detail', kwargs={'pk': equipment_pk}) if equipment_pk else reverse('equipment:equipment_list')
    return render(request, 'shared/form.html', {'form': form, 'page_title': '新增维修工单', 'back_url': back_url})


def order_update(request, pk):
    obj = get_object_or_404(MaintenanceOrder, pk=pk)
    if request.method == 'POST':
        form = MaintenanceOrderForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save()
            messages.success(request, '维修工单已更新。')
            return redirect('equipment:equipment_detail', pk=obj.equipment_id)
    else:
        form = MaintenanceOrderForm(instance=obj)
    return render(request, 'shared/form.html', {'form': form, 'page_title': '编辑维修工单', 'back_url': reverse('equipment:equipment_detail', kwargs={'pk': obj.equipment_id})})


def order_delete(request, pk):
    obj = get_object_or_404(MaintenanceOrder, pk=pk)
    back_pk = obj.equipment_id
    if request.method == 'POST':
        obj.delete()
        messages.success(request, '维修工单已删除。')
        return redirect('equipment:equipment_detail', pk=back_pk)
    return render(request, 'shared/confirm_delete.html', {'page_title': '删除维修工单', 'object_name': obj.title, 'back_url': reverse('equipment:equipment_detail', kwargs={'pk': back_pk})})


def _health_status_by_score(score: int) -> str:
    if score >= 90:
        return 'excellent'
    if score >= 75:
        return 'good'
    if score >= 60:
        return 'warning'
    return 'danger'


def _simulate_equipment_health(equipment):
    last_record = equipment.inspections.order_by('-inspected_at').first()
    base_vibration = last_record.vibration_value if last_record else 3.5
    base_temperature = last_record.temperature_value if last_record else 58.0

    vibration = round(max(0.5, base_vibration + random.uniform(-0.45, 0.45)), 2)
    temperature = round(max(20, base_temperature + random.uniform(-1.8, 1.8)), 2)
    score_delta = random.randint(-4, 3)
    new_score = max(45, min(98, equipment.health_score + score_delta))
    equipment.health_score = new_score
    equipment.runtime_hours += random.randint(1, 6)
    equipment.health_status = _health_status_by_score(new_score)
    equipment.save(update_fields=['health_score', 'runtime_hours', 'health_status', 'updated_at'])

    result_text = '状态正常'
    if equipment.health_status == 'warning':
        result_text = '需安排重点巡检'
    elif equipment.health_status == 'danger':
        result_text = '建议立即停机检查'
    elif equipment.health_status == 'excellent':
        result_text = '运行稳定'

    InspectionRecord.objects.create(
        equipment=equipment,
        inspector='系统自动诊断',
        result=result_text,
        vibration_value=vibration,
        temperature_value=temperature,
        note='由演示系统生成的实时健康诊断采样数据。'
    )

    latest = list(equipment.inspections.order_by('-inspected_at')[:10])
    latest.reverse()
    return {
        'labels': [item.inspected_at.strftime('%H:%M:%S') for item in latest],
        'vibration_values': [item.vibration_value for item in latest],
        'temperature_values': [item.temperature_value for item in latest],
        'health_score': equipment.health_score,
        'runtime_hours': equipment.runtime_hours,
        'health_status': equipment.get_health_status_display(),
    }


def api_equipment_health(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    payload = _simulate_equipment_health(equipment)
    return JsonResponse({'status': 'ok', 'equipment': {'health_score': payload['health_score'], 'runtime_hours': payload['runtime_hours'], 'health_status': payload['health_status']}, 'series': {'labels': payload['labels'], 'vibration_values': payload['vibration_values'], 'temperature_values': payload['temperature_values']}})


def export_orders_excel(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    orders = equipment.orders.all().order_by('-created_at')
    wb = Workbook()
    ws = wb.active
    ws.title = '维修工单'
    ws.append(['设备名称', equipment.name])
    ws.append(['设备编号', equipment.code])
    ws.append([])
    ws.append(['工单标题', '优先级', '状态', '维修人员', '问题说明', '创建时间'])
    for order in orders:
        ws.append([order.title, order.priority, order.get_status_display(), order.assignee, order.summary, order.created_at.strftime('%Y-%m-%d %H:%M')])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{equipment.code}_维修工单.xlsx"'
    wb.save(response)
    return response
