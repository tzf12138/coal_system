from django.db import models

class FillProcess(models.Model):
    PROCESS_CHOICES = [
        ('paste', '膏体充填'),
        ('tailings', '尾砂充填'),
        ('gangue', '原矸充填'),
    ]
    name = models.CharField(max_length=150, verbose_name='工艺名称')
    process_type = models.CharField(max_length=20, choices=PROCESS_CHOICES, verbose_name='工艺类型')
    mine_name = models.CharField(max_length=150, verbose_name='矿井/站点')
    status = models.CharField(max_length=50, default='运行中', verbose_name='运行状态')
    design_capacity = models.FloatField(default=0, verbose_name='设计能力（m³/h）')
    current_flow = models.FloatField(default=0, verbose_name='当前流量（m³/h）')
    concentration = models.FloatField(default=0, verbose_name='浓度（%）')
    pipeline_pressure = models.FloatField(default=0, verbose_name='管路压力（MPa）')
    data_quality = models.IntegerField(default=95, verbose_name='数据质量分')
    remark = models.TextField(blank=True, verbose_name='备注')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '充填工艺'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return f'{self.name} - {self.get_process_type_display()}'


class Sensor(models.Model):
    SENSOR_TYPES = [
        ('vibration', '振动传感器'),
        ('temperature', '温度传感器'),
        ('pressure', '压力传感器'),
        ('flow', '流量传感器'),
        ('level', '料位传感器'),
        ('gas', '气体传感器'),
        ('humidity', '湿度传感器'),
    ]
    process = models.ForeignKey(FillProcess, on_delete=models.CASCADE, related_name='sensors', verbose_name='所属工艺')
    name = models.CharField(max_length=150, verbose_name='传感器名称')
    sensor_type = models.CharField(max_length=30, choices=SENSOR_TYPES, verbose_name='传感器类型')
    code = models.CharField(max_length=50, unique=True, verbose_name='设备编码')
    location = models.CharField(max_length=200, verbose_name='安装位置')
    unit = models.CharField(max_length=30, default='', verbose_name='单位')
    current_value = models.FloatField(default=0, verbose_name='当前值')
    threshold_low = models.FloatField(default=0, verbose_name='下限')
    threshold_high = models.FloatField(default=0, verbose_name='上限')
    is_online = models.BooleanField(default=True, verbose_name='在线状态')
    last_report_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '传感器'
        verbose_name_plural = verbose_name
        ordering = ['code']

    def __str__(self):
        return f'{self.name}({self.code})'


class SensorReading(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='readings', verbose_name='传感器')
    value = models.FloatField(verbose_name='采集值')
    quality_score = models.IntegerField(default=100, verbose_name='质量分')
    collected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '传感器读数'
        verbose_name_plural = verbose_name
        ordering = ['-collected_at']

    def __str__(self):
        return f'{self.sensor.name} - {self.value}'


class VideoDevice(models.Model):
    process = models.ForeignKey(FillProcess, on_delete=models.CASCADE, related_name='video_devices', verbose_name='所属工艺')
    name = models.CharField(max_length=150, verbose_name='监控设备名称')
    location = models.CharField(max_length=200, verbose_name='安装位置')
    stream_url = models.CharField(max_length=255, blank=True, verbose_name='视频流地址')
    status = models.CharField(max_length=50, default='在线', verbose_name='状态')
    last_ping = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '监控设备'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class AlertEvent(models.Model):
    LEVEL_CHOICES = [
        ('low', '一般'),
        ('medium', '注意'),
        ('high', '严重'),
        ('critical', '紧急'),
    ]
    process = models.ForeignKey(FillProcess, on_delete=models.CASCADE, related_name='alerts', verbose_name='所属工艺')
    sensor = models.ForeignKey(Sensor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联传感器')
    title = models.CharField(max_length=200, verbose_name='报警标题')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, verbose_name='报警级别')
    description = models.TextField(verbose_name='报警描述')
    resolved = models.BooleanField(default=False, verbose_name='是否已处理')
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '报警事件'
        verbose_name_plural = verbose_name
        ordering = ['-occurred_at']

    def __str__(self):
        return f'{self.title} - {self.get_level_display()}'


class EnvironmentMetric(models.Model):
    mine_name = models.CharField(max_length=150, verbose_name='矿井名称')
    gas_concentration = models.FloatField(default=0, verbose_name='气体浓度')
    temperature = models.FloatField(default=0, verbose_name='温度')
    humidity = models.FloatField(default=0, verbose_name='湿度')
    pressure = models.FloatField(default=0, verbose_name='压力')
    risk_level = models.CharField(max_length=50, default='低', verbose_name='风险等级')
    recorded_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '环境监测'
        verbose_name_plural = verbose_name
        ordering = ['-recorded_at']

    def __str__(self):
        return f'{self.mine_name} - {self.risk_level}'
