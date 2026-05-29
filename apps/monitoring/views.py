import random
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from .forms import FillProcessForm, SensorForm
from .models import FillProcess, Sensor, SensorReading, VideoDevice, AlertEvent, EnvironmentMetric


def process_list(request):
    context = {
        'processes': FillProcess.objects.all(),
        'alerts': AlertEvent.objects.all()[:10],
        'environments': EnvironmentMetric.objects.all()[:5],
    }
    return render(request, 'monitoring/process_list.html', context)


def process_detail(request, pk):
    process = get_object_or_404(FillProcess, pk=pk)
    main_flow_sensor = process.sensors.filter(sensor_type='flow').first()
    main_pressure_sensor = process.sensors.filter(sensor_type='pressure').first()
    context = {
        'process': process,
        'sensors': process.sensors.all(),
        'videos': process.video_devices.all(),
        'alerts': process.alerts.all()[:20],
        'main_flow_sensor': main_flow_sensor,
        'main_pressure_sensor': main_pressure_sensor,
    }
    return render(request, 'monitoring/process_detail.html', context)


def sensor_center(request):
    context = {'sensors': Sensor.objects.select_related('process').all()}
    return render(request, 'monitoring/sensor_center.html', context)


def alert_center(request):
    context = {'alerts': AlertEvent.objects.select_related('process', 'sensor').all()}
    return render(request, 'monitoring/alert_center.html', context)


def _simulate_process_realtime(process):
    series_payload = {}
    for sensor in process.sensors.all():
        drift = random.uniform(-1.2, 1.2)
        if sensor.sensor_type == 'flow':
            drift = random.uniform(-4.5, 4.5)
        elif sensor.sensor_type == 'pressure':
            drift = random.uniform(-0.25, 0.25)
        elif sensor.sensor_type == 'temperature':
            drift = random.uniform(-1.0, 1.0)
        new_value = round(max(sensor.threshold_low, sensor.current_value + drift), 2)
        sensor.current_value = new_value
        sensor.save(update_fields=['current_value', 'last_report_time'])
        SensorReading.objects.create(sensor=sensor, value=new_value, quality_score=random.randint(92, 100))

        latest = list(sensor.readings.order_by('-collected_at')[:12])
        latest.reverse()
        series_payload[sensor.sensor_type] = {
            'sensor': sensor.name,
            'unit': sensor.unit,
            'labels': [item.collected_at.strftime('%H:%M:%S') for item in latest],
            'values': [item.value for item in latest],
        }

    flow_sensor = process.sensors.filter(sensor_type='flow').first()
    pressure_sensor = process.sensors.filter(sensor_type='pressure').first()
    if flow_sensor:
        process.current_flow = flow_sensor.current_value
    if pressure_sensor:
        process.pipeline_pressure = pressure_sensor.current_value
    process.concentration = round(max(40, min(95, process.concentration + random.uniform(-1.5, 1.5))), 2)
    process.save(update_fields=['current_flow', 'pipeline_pressure', 'concentration', 'updated_at'])

    table_rows = [
        {
            'id': sensor.id,
            'sensor': sensor.name,
            'type': sensor.get_sensor_type_display(),
            'location': sensor.location,
            'value': sensor.current_value,
            'unit': sensor.unit,
            'low': sensor.threshold_low,
            'high': sensor.threshold_high,
            'online': sensor.is_online,
        }
        for sensor in process.sensors.all()
    ]
    return series_payload, table_rows



def api_realtime(request):
    payload = []
    for sensor in Sensor.objects.select_related('process').all()[:20]:
        drift = random.uniform(-1.2, 1.2)
        value = round(max(sensor.threshold_low - 3, sensor.current_value + drift), 2)
        payload.append({
            'sensor': sensor.name,
            'code': sensor.code,
            'process': sensor.process.name,
            'value': value,
            'unit': sensor.unit,
            'online': sensor.is_online,
        })
    return JsonResponse({'status': 'ok', 'data': payload})


def api_process_trend(request, pk):
    process = get_object_or_404(FillProcess, pk=pk)
    do_refresh = request.GET.get('refresh') == '1'
    if do_refresh:
        series_payload, table_rows = _simulate_process_realtime(process)
    else:
        series_payload, table_rows = _simulate_process_realtime(process)
    return JsonResponse({
        'status': 'ok',
        'process': {
            'current_flow': process.current_flow,
            'concentration': process.concentration,
            'pipeline_pressure': process.pipeline_pressure,
            'status': process.status,
        },
        'series': series_payload,
        'sensors': table_rows,
    })



def process_create(request):
    if request.method == 'POST':
        form = FillProcessForm(request.POST)
        if form.is_valid():
            obj = form.save()
            messages.success(request, '充填工艺已创建。')
            return redirect('monitoring:process_detail', pk=obj.pk)
    else:
        form = FillProcessForm()
    return render(request, 'shared/form.html', {'form': form, 'page_title': '新增充填工艺', 'back_url': reverse('monitoring:process_list')})



def process_update(request, pk):
    obj = get_object_or_404(FillProcess, pk=pk)
    if request.method == 'POST':
        form = FillProcessForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save()
            messages.success(request, '充填工艺已更新。')
            return redirect('monitoring:process_detail', pk=obj.pk)
    else:
        form = FillProcessForm(instance=obj)
    return render(request, 'shared/form.html', {'form': form, 'page_title': '编辑充填工艺', 'back_url': reverse('monitoring:process_detail', kwargs={'pk': obj.pk})})



def process_delete(request, pk):
    obj = get_object_or_404(FillProcess, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, '充填工艺已删除。')
        return redirect('monitoring:process_list')
    return render(request, 'shared/confirm_delete.html', {'page_title': '删除充填工艺', 'object_name': obj.name, 'back_url': reverse('monitoring:process_detail', kwargs={'pk': pk})})



def sensor_create(request, process_pk=None):
    initial = {'process': process_pk} if process_pk else None
    if request.method == 'POST':
        form = SensorForm(request.POST)
        if form.is_valid():
            obj = form.save()
            messages.success(request, '传感器已新增。')
            return redirect('monitoring:process_detail', pk=obj.process_id)
    else:
        form = SensorForm(initial=initial)
    back_url = reverse('monitoring:process_detail', kwargs={'pk': process_pk}) if process_pk else reverse('monitoring:sensor_center')
    return render(request, 'shared/form.html', {'form': form, 'page_title': '新增传感器', 'back_url': back_url})



def sensor_update(request, pk):
    obj = get_object_or_404(Sensor, pk=pk)
    if request.method == 'POST':
        form = SensorForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save()
            messages.success(request, '传感器已更新。')
            return redirect('monitoring:process_detail', pk=obj.process_id)
    else:
        form = SensorForm(instance=obj)
    return render(request, 'shared/form.html', {'form': form, 'page_title': '编辑传感器', 'back_url': reverse('monitoring:process_detail', kwargs={'pk': obj.process_id})})



def sensor_delete(request, pk):
    obj = get_object_or_404(Sensor, pk=pk)
    back_pk = obj.process_id
    if request.method == 'POST':
        obj.delete()
        messages.success(request, '传感器已删除。')
        return redirect('monitoring:process_detail', pk=back_pk)
    return render(request, 'shared/confirm_delete.html', {'page_title': '删除传感器', 'object_name': obj.name, 'back_url': reverse('monitoring:process_detail', kwargs={'pk': back_pk})})
