from django.contrib.auth.models import AbstractUser
from django.db import models
from courses.models import Course, Group

class CustomUser(AbstractUser):
    """Кастомная модель пользователя - студента."""

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=250,
        unique=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password'
    )



    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id',)

    def __str__(self):
        return self.get_full_name()


class Balance(models.Model):
    """Модель баланса пользователя."""

    user = models.ForeignKey(
        to=CustomUser,
        on_delete=models.CASCADE,
    )

    balance = models.PositiveIntegerField(
        verbose_name='balance',
        default=1000
    )

    class Meta:
        verbose_name = 'Баланс'
        verbose_name_plural = 'Балансы'
        ordering = ('-id',)


class Subscription(models.Model):
    """Модель подписки пользователя на курс."""

    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Course, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-id',)

