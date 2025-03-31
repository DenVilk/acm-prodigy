from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model


User = get_user_model()


class Volunteer(models.Model):
    TSHIRT_SIZE = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
        ('XXXL', 'XXXL'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='volunteer',
    )
    firstname = models.CharField(max_length=50)
    secondname = models.CharField(max_length=50, blank=True, null=True)
    lastname = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    telegram = models.CharField(max_length=50)
    education = models.CharField(max_length=100)
    tshirt_size = models.CharField(max_length=10, choices=TSHIRT_SIZE)
    group = models.CharField(max_length=6, blank=True, null=True)
    rating = models.IntegerField(default=50)

    @property
    def telegram_link(self):
        return f'https://t.me/{self.telegram}'

    def __str__(self) -> str:
        return f'{self.lastname} {self.firstname}'

    class Meta:
        verbose_name = 'Волонтер'
        verbose_name_plural = 'Волонтеры'


class Locations(models.Model):
    name = models.CharField(max_length=50)
    administrator = models.ForeignKey(
        Volunteer,
        related_name='admin_locations',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f'Зона: {self.name}'

    class Meta:
        verbose_name = 'Локация'
        verbose_name_plural = 'Локации'


class VolunteerPositions(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'


class Event(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateTimeField()
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'


class VolunteerParticipation(models.Model):
    STATUS = [
        ('pending', 'Pending'),
        ('declined', 'Declined'),
        ('approved', 'Approved'),
    ]
    volunteer = models.ForeignKey(
        Volunteer,
        on_delete=models.CASCADE,
        related_name='applications',
    )
    position_wishes = models.ManyToManyField(
        VolunteerPositions,
        blank=True,
        related_name='position_wishes',
    )
    position = models.ForeignKey(
        VolunteerPositions,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='volunteers',
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='volunteers',
    )
    status = models.CharField(max_length=10, choices=STATUS, default=STATUS[0][1])
    location = models.ForeignKey(
        Locations,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='volunteers',
    )
    is_responsible = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'Участие {self.volunteer} в {self.event}'

    class Meta:
        verbose_name = 'Заявка волонтера'
        verbose_name_plural = 'Заявки волонтеров'