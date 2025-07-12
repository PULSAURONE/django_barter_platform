from django.db import models
from django.db import models
from django.contrib.auth.models import User


class Ad(models.Model):
    """Модель объявления."""

    # состояния товара
    CONDITION_CHOICES = [
        ('new', 'Новый'),
        ('used', 'Б/у'),
    ]

    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание товара")
    image_url = models.URLField(max_length=200, blank=True, null=True, verbose_name="URL изображения")
    category = models.CharField(max_length=100, verbose_name="Категория")
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, verbose_name="Состояние")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")

    # Связь с пользователем, который создал объявление
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ads', verbose_name="Пользователь")

    def __str__(self):
        return f"{self.title} от {self.user.username}"

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ['-created_at']


class ExchangeProposal(models.Model):
    """Модель предложения обмена."""

    # Варианты для статуса предложения
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена'),
    ]

    # Объявление, которое предлагают в обмен (отправитель)
    ad_sender = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='sent_proposals')

    # Объявление, на которое делают предложение (получатель)
    ad_receiver = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='received_proposals')

    comment = models.TextField(blank=True, verbose_name="Комментарий")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Предложение от {self.ad_sender.user.username} для {self.ad_receiver.user.username}"

    class Meta:
        verbose_name = "Предложение обмена"
        verbose_name_plural = "Предложения обмена"
        ordering = ['-created_at']