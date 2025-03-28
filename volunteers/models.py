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

    def __str__(self) -> str:
        return f'{self.lastname} {self.firstname}'


class Locations(models.Model):
    name = models.CharField(max_length=50)
    responsible = models.ForeignKey(
        Volunteer,
        related_name='responsibilites',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    volunteers = models.ManyToManyField(
        Volunteer,
        related_name='locations',
        blank=True,
    )
    administrator = models.ForeignKey(
        Volunteer,
        related_name='admin_locations',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f'Зона: {self.name}'


class VolunteerPositions(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class VolunteerParticipation(models.Model):
    STATUS = [
        ('Pending', 'pending'),
        ('Declined', 'declined'),
        ('Approved', 'approved'),
    ]
    volunteer = models.ForeignKey(
        Volunteer,
        on_delete=models.CASCADE,
        related_name='application'
    )
    position_wishes = models.ManyToManyField(
        VolunteerPositions,
        blank=True,
        related_name='position_wishes'
    )
    position = models.ForeignKey(
        Volunteer,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='volunteers'
    )
    status = models.CharField(max_length=10, choices=STATUS)

    def __str__(self) -> str:
        return f'Участие {self.volunteer}'