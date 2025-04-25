from django.db import models
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_save
from django_countries.fields import CountryField
from django.conf import settings


User = get_user_model()

class Settings(models.Model):
    name = models.CharField(max_length=256)
    value = models.CharField(max_length=1024)
    description = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):

        return self.name


class TranslationKey(models.Model):
    key = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.key


class Translation(models.Model):
    LANGUAGES = (
        ('en', 'English'),
        ('ru', 'Russian'),
        ('be', 'Belarussian'),
    )

    translation_key = models.ForeignKey(TranslationKey, on_delete=models.CASCADE, related_name="translations")
    language = models.CharField(max_length=2, choices=LANGUAGES)
    translated_text = models.TextField()

    class Meta:
        unique_together = ('translation_key', 'language')

    def __str__(self):
        return f'{self.translation_key} ({self.language})'


class Coach(models.Model):
    TSHIRT_SIZE = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
        ('XXXL', 'XXXL'),
    ]
    firstname = models.CharField(max_length=50)
    secondname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    tshirt_size = models.CharField(max_length=10, choices=TSHIRT_SIZE)

    class Meta:
        verbose_name = 'Тренер'
        verbose_name_plural = 'Тренеры'

    def __str__(self):
        return f'[{self.id}] {self.lastname} {self.firstname} {self.secondname}'

    @property
    def fullname(self):
        return f'{self.lastname} {self.firstname} {self.secondname}'



class Team(models.Model):
    TEAM_STATUS = [
        ('in progress', 'Заполняется'),
        ('checking', 'На рассмотрении'),
        ('good', 'Участие в этапе'),
        ('error', 'Ошибки в заполнении'),
    ]

    TEAM_TYPE = [
        ('school', 'Junior'),
        ('university', 'Student')
    ]

    TEAM_PARTICIPANT_STATUS = [
        ('full','Одно учебное заведение'),
        ('mixed', 'Несколько учебных заведений'),
    ]

    name = models.CharField(max_length=64, unique=True)
    coach = models.ForeignKey(
        Coach,
        models.SET_NULL,
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=30, default='in progress', choices=TEAM_STATUS)
    type = models.CharField(max_length=50, choices=TEAM_TYPE)
    participant_status = models.CharField(max_length=30, choices=TEAM_PARTICIPANT_STATUS)
    quaterfinal = models.BooleanField(default=False, blank=True)
    semifinal = models.BooleanField(default=False, blank=True)
    final = models.BooleanField(default=False, blank=True)
    disqualified = models.BooleanField(default=False, blank=True)
    disqual_message = models.TextField(null=True, blank=True)
    system_login = models.CharField(max_length=100, null=True, blank=True)
    system_password = models.CharField(max_length=100, null=True, blank=True)
    is_generated_mail = models.BooleanField(default=False)
    location = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'

    def __str__(self):
        login = ''
        if self.status == 'good':
            if self.system_login:
                if self.is_generated_mail:
                    login = f'(YaC: {self.system_login})'
                else:
                    login = f'(YaC: {self.system_login}, mail didn\'t generated)'
            else:
                login = '(Waiting for login...)'
        return f'{self.name} {login}'

    @property
    def stage(self):
        if self.final:
            return 'Финал'
        if self.semifinal:
            return 'Полуфинал'
        if self.quaterfinal:
            return 'Отборочный этап'
        return 'Не допущен/обрабатывается к дальнейшему участию'

    @property
    def stage_en(self):
        if self.final:
            return 'Finals'
        if self.semifinal:
            return 'Semifinals'
        if self.quaterfinal:
            return 'Quaterfinals'
        return 'Denied/Getting processed for the further participation'

    @property
    def eng_status(self):
        if self.status == 'in progress':
            return 'In progess'
        elif self.status == 'checking':
            return 'Waiting for approvement'
        elif self.status == 'good':
            return 'Participating in round'
        elif self.status == 'error':
            return 'Filling-in mistake'

    @property
    def is_full(self):
        return self.participants.count() == 3


    @property
    def is_sent(self) -> bool:
        return self.status != 'in progress'

    @property
    def is_ready(self) -> bool:
        if self.is_sent:
            return False
        for user in self.participants.all():
            if not user.is_done:
                return False
        return True


class Participant(models.Model):
    STUDENT_STATUS = [
        ('студент', 'Студент'),
        ('школьник', 'Школьник'),
        ('аспирант', 'Аспирант'),
        ('магистрант', 'Магистрант'),
        ('др', 'Другое'),
    ]
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
        blank=True
    )
    firstname = models.CharField(max_length=50)
    secondname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    education = models.CharField(max_length=100)
    student_status = models.CharField(max_length=30, choices=STUDENT_STATUS)
    tshirt_size = models.CharField(max_length=10, choices=TSHIRT_SIZE)
    country = CountryField()
    group = models.CharField(max_length=6, blank=True, null=True)
    team = models.ForeignKey(
        Team,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name='participants'
    )

    class Meta:
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'


    def __str__(self):
        return f'[{self.country.code}] {self.firstname} {self.secondname} {self.lastname} ({self.education})'

    @property
    def is_done(self):
        if(
            self.firstname and
            self.secondname and
            self.lastname and
            self.email and
            self.phone and
            self.education and
            self.student_status and
            self.tshirt_size and
            self.country
        ):
            return True
        return False

    @property
    def fullname(self):
        return f'{self.lastname} {self.firstname} {self.secondname}'


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Participant.objects.create(user=instance)
    instance.participant.save()
