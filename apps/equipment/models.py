from django.db import models

class Equipment(models.Model):
    HEALTH_CHOICES = [
        ('excellent', '优'),
        ('good', '良'),
        ('warning', '预警'),
        ('danger', '危险'),
    ]
    name = models.CharField(max_length=200, verbose_name='设备名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='设备编号')
    category = models.CharField(max_length=100, verbose_name='设备类别')
    mine_name = models.CharField(max_length=150, verbose_name='所在矿井')
    location = models.CharField(max_length=200, verbose_name='安装位置')
    health_status = models.CharField(max_length=20, choices=HEALTH_CHOICES, default='good', verbose_name='健康状态')
    health_score = models.IntegerField(default=85, verbose_name='健康评分')
    runtime_hours = models.IntegerField(default=0, verbose_name='累计运行小时')
    next_maintenance_date = models.DateField(verbose_name='下次维护日期')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '设备台账'
        verbose_name_plural = verbose_name
        ordering = ['code']

    def __str__(self):
        return f'{self.name}({self.code})'


class EquipmentSensorPlan(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='sensor_plans', verbose_name='设备')
    sensor_type = models.CharField(max_length=100, verbose_name='诊断传感器类型')
    deploy_position = models.CharField(max_length=200, verbose_name='部署位置')
    purpose = models.CharField(max_length=200, verbose_name='部署目的')
    status = models.CharField(max_length=50, default='已部署', verbose_name='部署状态')

    class Meta:
        verbose_name = '诊断传感器部署'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.equipment.name}-{self.sensor_type}'


class InspectionRecord(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='inspections', verbose_name='设备')
    inspector = models.CharField(max_length=100, verbose_name='巡检人')
    result = models.CharField(max_length=100, verbose_name='巡检结论')
    vibration_value = models.FloatField(default=0, verbose_name='振动值')
    temperature_value = models.FloatField(default=0, verbose_name='温度值')
    note = models.TextField(blank=True, verbose_name='说明')
    inspected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '巡检记录'
        verbose_name_plural = verbose_name
        ordering = ['-inspected_at']

    def __str__(self):
        return f'{self.equipment.name} - {self.result}'


class MaintenanceOrder(models.Model):
    STATUS_CHOICES = [
        ('open', '待处理'),
        ('processing', '处理中'),
        ('done', '已完成'),
    ]
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='orders', verbose_name='设备')
    title = models.CharField(max_length=200, verbose_name='工单标题')
    priority = models.CharField(max_length=50, verbose_name='优先级')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name='工单状态')
    assignee = models.CharField(max_length=100, verbose_name='维修人员')
    summary = models.TextField(verbose_name='问题说明')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '维修工单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class DiagnosisCase(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='cases', verbose_name='设备')
    title = models.CharField(max_length=200, verbose_name='诊断主题')
    symptom = models.TextField(verbose_name='故障现象')
    diagnosis = models.TextField(verbose_name='专家诊断')
    recommendation = models.TextField(verbose_name='处置建议')
    expert_name = models.CharField(max_length=100, verbose_name='专家姓名')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '远程诊断案例'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ARSession(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='ar_sessions', verbose_name='设备')
    session_code = models.CharField(max_length=50, unique=True, verbose_name='AR会话编号')
    glasses_model = models.CharField(max_length=100, verbose_name='AR眼镜型号')
    field_engineer = models.CharField(max_length=100, verbose_name='现场人员')
    remote_expert = models.CharField(max_length=100, verbose_name='后台专家')
    status = models.CharField(max_length=50, default='已建立连接', verbose_name='会话状态')
    interaction_note = models.TextField(verbose_name='交互记录')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'AR远程协作'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.session_code
