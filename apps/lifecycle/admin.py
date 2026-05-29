from django.contrib import admin
from .models import FillProject, ProjectTask, Milestone, ProjectDocument, RiskRecord, AcceptanceRecord

admin.site.register(FillProject)
admin.site.register(ProjectTask)
admin.site.register(Milestone)
admin.site.register(ProjectDocument)
admin.site.register(RiskRecord)
admin.site.register(AcceptanceRecord)
