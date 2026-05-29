from django.db import models

class Announcement(models.Model):
    title = models.CharField(max_length=200, verbose_name='公告标题')
    content = models.TextField(verbose_name='公告内容')
    level = models.CharField(max_length=20, default='info', verbose_name='级别')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '平台公告'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class DashboardNote(models.Model):
    title = models.CharField(max_length=200, verbose_name='看板主题')
    value = models.CharField(max_length=100, verbose_name='指标值')
    description = models.CharField(max_length=255, blank=True, verbose_name='说明')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '首页指标卡片'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class ExpertKnowledge(models.Model):
    category = models.CharField(max_length=100, verbose_name='知识分类')
    title = models.CharField(max_length=200, verbose_name='知识标题')
    content = models.TextField(verbose_name='知识内容')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '专家知识库'
        verbose_name_plural = verbose_name
        ordering = ['category', 'title']

    def __str__(self):
        return f'{self.category} - {self.title}'
