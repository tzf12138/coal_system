from django.db import models

class FillProject(models.Model):
    STAGE_CHOICES = [
        ('initiation', '立项'),
        ('design', '设计'),
        ('procurement', '采购'),
        ('construction', '施工'),
        ('commissioning', '调试'),
        ('acceptance', '验收'),
        ('operation', '运维'),
    ]
    name = models.CharField(max_length=200, verbose_name='项目名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='项目编号')
    owner = models.CharField(max_length=100, verbose_name='负责人')
    mine_name = models.CharField(max_length=150, verbose_name='实施矿井')
    stage = models.CharField(max_length=30, choices=STAGE_CHOICES, default='initiation', verbose_name='项目阶段')
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='项目预算')
    progress = models.IntegerField(default=0, verbose_name='整体进度(%)')
    start_date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(verbose_name='计划结束日期')
    description = models.TextField(blank=True, verbose_name='项目说明')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '充填项目'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ProjectTask(models.Model):
    STATUS_CHOICES = [
        ('todo', '待开始'),
        ('doing', '进行中'),
        ('done', '已完成'),
        ('delayed', '延期'),
    ]
    project = models.ForeignKey(FillProject, on_delete=models.CASCADE, related_name='tasks', verbose_name='所属项目')
    title = models.CharField(max_length=200, verbose_name='任务名称')
    owner = models.CharField(max_length=100, verbose_name='责任人')
    stage = models.CharField(max_length=30, verbose_name='阶段')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo', verbose_name='状态')
    progress = models.IntegerField(default=0, verbose_name='进度')
    start_date = models.DateField(verbose_name='开始日期')
    due_date = models.DateField(verbose_name='截止日期')
    remark = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '项目任务'
        verbose_name_plural = verbose_name
        ordering = ['due_date']

    def __str__(self):
        return self.title


class Milestone(models.Model):
    project = models.ForeignKey(FillProject, on_delete=models.CASCADE, related_name='milestones', verbose_name='所属项目')
    title = models.CharField(max_length=200, verbose_name='里程碑')
    milestone_date = models.DateField(verbose_name='节点日期')
    completed = models.BooleanField(default=False, verbose_name='是否完成')
    description = models.TextField(blank=True, verbose_name='说明')

    class Meta:
        verbose_name = '里程碑'
        verbose_name_plural = verbose_name
        ordering = ['milestone_date']

    def __str__(self):
        return self.title


class ProjectDocument(models.Model):
    project = models.ForeignKey(FillProject, on_delete=models.CASCADE, related_name='documents', verbose_name='所属项目')
    title = models.CharField(max_length=200, verbose_name='文档名称')
    category = models.CharField(max_length=100, verbose_name='文档类别')
    version = models.CharField(max_length=50, default='V1.0', verbose_name='版本')
    file_note = models.TextField(blank=True, verbose_name='文件说明')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '项目文档'
        verbose_name_plural = verbose_name
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title


class RiskRecord(models.Model):
    project = models.ForeignKey(FillProject, on_delete=models.CASCADE, related_name='risks', verbose_name='所属项目')
    title = models.CharField(max_length=200, verbose_name='风险名称')
    level = models.CharField(max_length=50, verbose_name='风险等级')
    status = models.CharField(max_length=50, default='监控中', verbose_name='处置状态')
    strategy = models.TextField(verbose_name='应对措施')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '项目风险'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class AcceptanceRecord(models.Model):
    project = models.ForeignKey(FillProject, on_delete=models.CASCADE, related_name='acceptances', verbose_name='所属项目')
    acceptance_stage = models.CharField(max_length=100, verbose_name='验收阶段')
    score = models.IntegerField(default=0, verbose_name='验收分数')
    result = models.CharField(max_length=100, verbose_name='验收结果')
    summary = models.TextField(verbose_name='验收总结')
    accepted_at = models.DateField(verbose_name='验收日期')

    class Meta:
        verbose_name = '验收记录'
        verbose_name_plural = verbose_name
        ordering = ['-accepted_at']

    def __str__(self):
        return f'{self.project.name} - {self.acceptance_stage}'
