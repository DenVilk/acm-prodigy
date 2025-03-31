from django import forms

from volunteers.models import (
    Volunteer,
    VolunteerParticipation,
    VolunteerPositions,
)


class VolunteerForm(forms.ModelForm):

    class Meta:
        model = Volunteer
        fields = (
            'lastname',
            'firstname',
            'secondname',
            'phone',
            'telegram',
            'email',
            'education',
            'tshirt_size',
            'group',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class VolunteerParticipationForm(forms.ModelForm):
    position_wishes = forms.ModelMultipleChoiceField(
        queryset=VolunteerPositions.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )
    class Meta:
        model = VolunteerParticipation
        fields = (
            'position_wishes',
        )
