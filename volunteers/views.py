from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, View
from django.contrib.auth.views import LoginView

from config.settings import RECAPTCHA_PUBLIC_KEY
from main.forms import AuthUserForm, CreateUserForm
from main.mixins import LanguageMixin
from main.utils import Configuration

from volunteers.forms import (
    VolunteerForm,
    VolunteerParticipationForm,
)
from volunteers.mixins import (
    VolunteerAccessMixin,
    VolunteerEventAccessMixin,
)
from volunteers.models import (
    Event,
    Locations,
    Volunteer,
    VolunteerParticipation,
)

class IndexView(LanguageMixin, View):
    template_name = 'volunteers/index.html'

    def get(self, request, *args, **kwargs):
        form = None
        if Volunteer.objects.filter(user=request.user).exists():
            form = VolunteerForm(instance=request.user.volunteer)
        else:
            form = VolunteerForm()

        return self.render_page(
            request,
            self.template_name,
            {
                'form': form,
            }
        )

    def post(self, request, *args, **kwargs):
        form = VolunteerForm(request.POST, instance=request.user.volunteer)
        if form.is_valid():
            form.save()
            return redirect('volunteers-index')

        return self.render_page(
            request,
            self.template_name,
            {
                'form': form,
            }
        )


class ParticipationDetailView(VolunteerAccessMixin, LanguageMixin, View):
    template_name = 'volunteers/participation_detail.html'

    def get_object(self, id):
        return get_object_or_404(Event, id=id)

    def get(self, request, *args, **kwargs):
        event = self.get_object(kwargs['id'])
        participation = None
        if VolunteerParticipation.objects.filter(
            event=event,
            volunteer=request.user.volunteer,
        ).exists():
            participation = VolunteerParticipation.objects.get(
                event=event,
                volunteer=request.user.volunteer
            )

        form = VolunteerParticipationForm()

        return self.render_page(
            request,
            self.template_name,
            {
                'event': event,
                'participation': participation,
                'form': form
            }
        )

    def post(self, request, *args, **kwargs):
        event = self.get_object(kwargs['id'])
        if VolunteerParticipation.objects.filter(
            event=event,
            volunteer=request.user.volunteer,
        ).exists():
            return redirect('participation-detail', event.id)

        participation = None
        form = VolunteerParticipationForm(request.POST)
        if form.is_valid():
            application = VolunteerParticipation.objects.create(
                volunteer=request.user.volunteer,
                event=event,
            )
            for item in form.cleaned_data['position_wishes']:
                application.position_wishes.add(item.id)
            application.save()
            return redirect('participation-detail', event.id)

        return self.render_page(
            request,
            self.template_name,
            {
                'event': event,
                'participation': participation,
                'form': form
            }
        )


class LocationsListView(VolunteerAccessMixin, LanguageMixin, View):
    template_name = 'volunteers/location_list.html'

    def get(self, request, *args, **kwargs):
        locations = Locations.objects.all()
        return self.render_page(
            request,
            self.template_name,
            {
                'locations': locations,
            }
        )


class EventDetailView(VolunteerEventAccessMixin, VolunteerAccessMixin, LanguageMixin, View):
    template_name = 'volunteers/event_detail.html'

    def get_object(self, id):
        return get_object_or_404(Event, id=id)

    def get(self, request, *args, **kwargs):
        event = self.get_object(kwargs['id'])
        location_volunteers = {}

        for volunteer in event.volunteers.all():
            location_volunteers[volunteer.location] = (
                location_volunteers.get(volunteer.location, []) + [volunteer]
            )

        if None in location_volunteers.keys():
            del location_volunteers[None]

        return self.render_page(
            request,
            self.template_name,
            {
                'event': event,
                'location_volunteers': location_volunteers,
            }
        )


def create_volunteer(request):
    if not request.method == 'POST' or\
       not request.user.is_authenticated or \
       Volunteer.objects.filter(user=request.user).exists():
        return redirect('volunteers-index')

    Volunteer.objects.create(user=request.user)
    return redirect('volunteers-index')


class SignUpView(VolunteerAccessMixin, LanguageMixin, CreateView):
    form_class = CreateUserForm
    success_url = 'volunteers-login'
    template_name = 'volunteers/registration/signup.html'

    def get(self, request, *args, **kwargs):
        agreement = Configuration('configuration.agreement')
        agreement_url = Configuration('configuration.agreement.url')

        return self.render_page(request, self.template_name, {
            'signup' : 'active',
            'captcha_key' : RECAPTCHA_PUBLIC_KEY,
            'form': self.get_form(),
            'agreement': agreement,
            'agreement_url': agreement_url,
        })

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        agreement = Configuration('configuration.agreement')
        agreement_url = Configuration('configuration.agreement.url')

        if form.is_valid():
            if (
                Configuration('configuration.agreement') == 'true' and
                not form.cleaned_data['personal_data_agreement']
            ):
                form.add_error('personal_data_agreement', 'Required field')
            else:
                res = form.save()
                Volunteer.objects.create(user=res)
                return redirect(self.success_url)

        return self.render_page(
            request,
            self.template_name,
            {
                'form': form,
                'disable_footer': True,
                'agreement': agreement,
                'agreement_url': agreement_url,
            }
        )


class UserLoginView(VolunteerAccessMixin, LanguageMixin, LoginView):
    form_class = AuthUserForm
    template_name = 'volunteers/registration/login.html'

    def get(self, request, *args, **kwargs):
        return self.render_page(
            request,
            self.template_name,
            {
                'form': self.get_form(),
                'login': 'active',
            }
        )

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)