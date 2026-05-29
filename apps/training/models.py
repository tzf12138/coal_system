from django.db import models

class TrainingCourse(models.Model):
    title = models.CharField(max_length=200, verbose_name='课程名称')
    category = models.CharField(max_length=100, verbose_name='课程类别')
    teacher = models.CharField(max_length=100, verbose_name='讲师')
    duration_hours = models.IntegerField(default=2, verbose_name='学时')
    mode = models.CharField(max_length=50, default='线上+实训', verbose_name='培训形式')
    description = models.TextField(blank=True, verbose_name='课程简介')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '培训课程'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class TrainingRecord(models.Model):
    course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE, related_name='records', verbose_name='课程')
    trainee = models.CharField(max_length=100, verbose_name='学员')
    department = models.CharField(max_length=100, verbose_name='部门')
    score = models.IntegerField(default=0, verbose_name='考核成绩')
    passed = models.BooleanField(default=False, verbose_name='是否通过')
    completed_at = models.DateField(verbose_name='完成日期')

    class Meta:
        verbose_name = '培训记录'
        verbose_name_plural = verbose_name
        ordering = ['-completed_at']

    def __str__(self):
        return f'{self.trainee} - {self.course.title}'
