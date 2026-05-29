from django.contrib import admin
from .models import Equipment, EquipmentSensorPlan, InspectionRecord, MaintenanceOrder, DiagnosisCase, ARSession

admin.site.register(Equipment)
admin.site.register(EquipmentSensorPlan)
admin.site.register(InspectionRecord)
admin.site.register(MaintenanceOrder)
admin.site.register(DiagnosisCase)
admin.site.register(ARSession)
