from django.contrib import admin
from .models import FillProcess, Sensor, SensorReading, VideoDevice, AlertEvent, EnvironmentMetric

admin.site.register(FillProcess)
admin.site.register(Sensor)
admin.site.register(SensorReading)
admin.site.register(VideoDevice)
admin.site.register(AlertEvent)
admin.site.register(EnvironmentMetric)
