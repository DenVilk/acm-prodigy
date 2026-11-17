from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django_recaptcha.fields import ReCaptchaField
from main.models import Coach, Participant, Team
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from main.utils import Configuration
from main.services import get_olympiad_type


class PrinterForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={"rows":5, "cols":20}))


class AuthUserForm(AuthenticationForm, forms.ModelForm):

	class Meta:
		model = User
		fields = ('username', 'password')

class CreateUserForm(UserCreationForm):
    captcha = ReCaptchaField()
    personal_data_agreement = forms.BooleanField(initial=False, required=False)

class CreateParticipantForm(forms.ModelForm):

    class Meta:
        model = Participant
        fields = (
            'firstname',
            'secondname',
            'lastname',
            'email',
            'phone',
            'education',
            'group',
            'student_status',
            'tshirt_size',
            'country',
        )

    def __init__(self, *args, **kwargs):
        super(CreateParticipantForm, self).__init__(*args, **kwargs)
        self.fields['student_status'].widget.attrs.update({
            'data-default': 'Статус',
            'class': 'selects'
        })
        self.fields['tshirt_size'].widget.attrs.update({
            'data-default': 'Размер майки',
            'class': 'selects'
        })
        self.fields['country'].widget.attrs.update({
            'data-default': 'Страна',
            'class': 'selects'
        })

        self.fields['firstname'].widget.attrs.update({'placeholder': 'Имя', 'class': 'btn-star-input'})
        self.fields['secondname'].widget.attrs.update({'placeholder': 'Отчество', 'class': 'btn-star-input'})
        self.fields['lastname'].widget.attrs.update({'placeholder': 'Фамилия', 'class': 'btn-star-input'})
        self.fields['education'].widget.attrs.update({'placeholder': 'Учебное заведение', 'class': 'btn-star-input'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Email', 'class': 'btn-star-input'})
        self.fields['phone'].widget.attrs.update({'placeholder': 'Номер телефона', 'class': 'btn-star-input'})

    def clean_group(self):
        data = self.cleaned_data['group']
        checking = True if Configuration('configuration.registration.student_group')=='true' else False
        if checking:
            import requests
            if data == '':
                raise ValidationError('Group cannot by empty')
            resp = requests.get('https://iis.bsuir.by/api/v1/student-groups')
            for group in resp.json():
                if group['name'] == data:
                    return data
            raise ValidationError('Cannot validate group number')
        return data


class CreateTeamForm(forms.Form):
    name = forms.CharField(max_length=150)
    command_type = forms.IntegerField()
    univer_type = forms.IntegerField()

    def clean_name(self):
        data = self.cleaned_data['name']
        checking = False if get_olympiad_type()=='single' else True
        if checking:
            if len(Team.objects.filter(name=data))!=0:
                raise ValidationError('Команда с таким названием уже существует')
        return data


class CreateCoachForm(forms.ModelForm):

    class Meta:
        model = Coach
        fields = (
            '__all__'
        )

    def __init__(self, *args, **kwargs):
        super(CreateCoachForm, self).__init__(*args, **kwargs)
        self.fields['firstname'].widget.attrs.update({'class': 'btn-star-input'})
        self.fields['secondname'].widget.attrs.update({'class': 'btn-star-input'})
        self.fields['lastname'].widget.attrs.update({'class': 'btn-star-input'})
        self.fields['email'].widget.attrs.update({'class': 'btn-star-input'})
        self.fields['phone'].widget.attrs.update({'class': 'btn-star-input'})
        self.fields['tshirt_size'].widget.attrs.update({'class': 'btn-star-input'})
        self.fields['firstname'].widget.attrs.update({'placeholder': 'Имя'})
        self.fields['secondname'].widget.attrs.update({'placeholder': 'Отчество'})
        self.fields['lastname'].widget.attrs.update({'placeholder': 'Фамилия'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Email'})
        self.fields['phone'].widget.attrs.update({'placeholder': 'Номер телефона'})
        self.fields['tshirt_size'].widget.attrs.update({'class': 'selects', 'data-default': 'Размер майки'})
