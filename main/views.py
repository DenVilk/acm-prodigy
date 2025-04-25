import json
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from main.forms import (
    CreateCoachForm,
    CreateParticipantForm,
    CreateTeamForm,
    CreateUserForm,
    AuthUserForm
)
from config.settings import RECAPTCHA_PUBLIC_KEY
from main.models import Coach, Participant, Team
from main.services import get_available_reg, get_credentials_show, get_olympiad_type
from main.mixins import LanguageMixin
from main.utils import Configuration


class IndexView(LanguageMixin, TemplateView):
    template_name = 'main/index.html'

    def get(self, request, *args, **kwargs):
        return self.render_page(request, self.template_name)


class RulesView(LanguageMixin, TemplateView):
    template_name = 'main/rules.html'

    def get(self, request, *args, **kwargs):
        return self.render_page(request, self.template_name, {'disable_footer':True, })


class CommonInfoView(LanguageMixin, TemplateView):
    template_name = 'main/common_info.html'

    def get(self, request, *args, **kwargs):
        return self.render_page(request, self.template_name, {'disable_footer': True, })


class SignUpView(LanguageMixin, CreateView):
    form_class = CreateUserForm
    success_url = 'login'
    template_name = 'main/registration/signup.html'

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
                form.save()
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


class UserLoginView(LanguageMixin, LoginView):
    form_class = AuthUserForm
    success_url = 'index'
    template_name = 'main/registration/login.html'

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


class TeamListView(LanguageMixin, View):
    template_name = 'main/team_list.html'

    def get(self, request, *args, **kwargs):
        teams = Team.objects.filter(status='good')

        return self.render_page(
            request,
            self.template_name,
            {
                'teams': teams,
                'disable_footer': True,
            }
        )


class TeamSemifinalListView(LanguageMixin, View):
    template_name = 'main/team_list.html'

    def get(self, request, *args, **kwargs):
        teams = Team.objects.filter(status='good', semifinal=True)

        return self.render_page(
            request,
            self.template_name,
            {
                'teams': teams,
                'disable_footer': True,
            }
        )


class TeamStudentFinalListView(LanguageMixin, View):
    template_name = 'main/team_list.html'

    def get(self, request, *args, **kwargs):
        teams = Team.objects.filter(status='good', final=True, type='university')

        return self.render_page(
            request,
            self.template_name,
            {
                'teams': teams,
                'disable_footer': True,
            }
        )


class TeamSchoolFinalListView(LanguageMixin, View):
    template_name = 'main/team_list.html'

    def get(self, request, *args, **kwargs):
        teams = Team.objects.filter(status='good', final=True, type='school')

        return self.render_page(
            request,
            self.template_name,
            {
                'teams': teams,
                'gratitude': True,
                'disable_footer': True,
            }
        )


class TeamView(LanguageMixin, LoginRequiredMixin, View):
    template_name = 'main/team_detail.html'

    def get(self, request, *args, **kwargs):
        context = {
            'team_page': 'active',
            'available_reg': get_available_reg(),
            'olymp_type': get_olympiad_type(),
            'disable_footer': True,
            'credentials': get_credentials_show(),
        }

        return self.render_page(
            request,
            self.template_name,
            context
        )


class CreateCoachView(LanguageMixin, LoginRequiredMixin, CreateView):
    model = Coach
    template_name = 'main/coach.html'
    form_class = CreateCoachForm

    def get(self, request, *args, **kwargs):
        if get_olympiad_type()=='single' or\
            not request.user.participant.team or\
            request.user.participant.team.coach or\
            request.user.participant.team.status != 'in progress':
            return redirect('team-detail')

        form = self.form_class()
        return self.render_page(
            request,
            self.template_name,
            {
                'form': form,
                'disable_footer': True,
            }
        )

    def post(self, request, *args, **kwargs):
        if get_olympiad_type()=='single' or\
            not request.user.participant.team or \
            request.user.participant.team.coach or\
            request.user.participant.team.status != 'in progress':
            return redirect('team-detail')

        form = self.form_class(request.POST)

        if form.is_valid():
            coach = Coach(**form.cleaned_data)
            coach.save()
            request.user.participant.team.coach = coach
            request.user.participant.team.save()

            return redirect('team-detail')

        return self.render_page(
            request,
            self.template_name,
            {
                'form':form,
            }
        )


class CreateTeamView(LanguageMixin, LoginRequiredMixin, CreateView):
    model = Team
    template_name = 'main/team_create.html'
    form_class = CreateTeamForm

    def get(self, request, *args, **kwargs):
        if not get_available_reg() or \
            get_olympiad_type() =='single' or \
            request.user.participant.team:

            return redirect('team-detail')

        form = self.form_class()
        return self.render_page(
            request,
            self.template_name,
            {
                'form':form,
                'disable_footer': True,
            }
        )

    def post(self, request, *args, **kwargs):
        if not get_available_reg() or \
            request.user.participant.team:

            return redirect('team-detail')

        if get_olympiad_type() == 'single':
            team = Team(
                name = request.user.username,
                type = Team.TEAM_TYPE[1][0],
                participant_status = Team.TEAM_PARTICIPANT_STATUS[0][0],
            )
            team.save()
            request.user.participant.team = team
            request.user.participant.save()

            return redirect('team-detail')
        else:
            form = self.form_class(request.POST)

            if form.is_valid():
                team = Team(
                    name = form.cleaned_data['name'],
                    type = Team.TEAM_TYPE[form.cleaned_data['command_type']][0],
                    participant_status = Team.TEAM_PARTICIPANT_STATUS[form.cleaned_data['univer_type']][0],
                )

                team.save()
                request.user.participant.team = team
                request.user.participant.save()

                return redirect('team-detail')

            return self.render_page(
                request,
                self.template_name,
                {
                    'form':form,
                }
            )


class CreateParticipantView(LanguageMixin, LoginRequiredMixin, CreateView):
    model = Participant
    template_name = 'main/participant.html'
    form_class = CreateParticipantForm

    def get(self, request, *args, **kwargs):
        if get_olympiad_type() == 'single' or \
            not request.user.participant.team or\
            request.user.participant.team.participants.count() == 3 or\
            request.user.participant.team.status != 'in progress':
            return redirect('team-detail')

        form = self.form_class()
        return self.render_page(
            request,
            self.template_name,
            {
                'form': form,
                'disable_footer': True,
            }
        )

    def post(self, request, *args, **kwargs):
        if get_olympiad_type() == 'single' or \
            not request.user.participant.team or\
            request.user.participant.team.participants.count() == 3 or\
            request.user.participant.team.status != 'in progress':
            return redirect('team-detail')

        form = self.form_class(request.POST)
        if form.is_valid():
            participant = Participant(
                **form.cleaned_data,
                team = request.user.participant.team,
            )
            participant.save()

            return redirect('team-detail')

        return self.render_page(request, self.template_name, {'form':form,})


class ChangeParticipantView(LanguageMixin, LoginRequiredMixin, View):
    model = Participant
    template_name = 'main/participant.html'
    form_class = CreateParticipantForm

    def get_participant_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Participant, id=id_)

    def get(self, request, *args, **kwargs):
        _participant = self.get_participant_object()
        if not request.user.participant.team or \
            request.user.participant.team.status != 'in progress' or \
            not (_participant in request.user.participant.team.participants.all()):
            return redirect('team-detail')

        form = self.form_class(instance=_participant)
        return self.render_page(
            request,
            self.template_name,
            {
                'form':form,
                'disable_footer': True,
            }
        )

    def post(self, request, *args, **kwargs):
        _participant = self.get_participant_object()
        if not request.user.participant.team or \
            request.user.participant.team.status != 'in progress' or \
            not (_participant in request.user.participant.team.participants.all()):
            return redirect('team-detail')

        form = self.form_class(request.POST, instance=_participant)
        if form.is_valid():
            form.save()
            if get_olympiad_type()=='single' and _participant == request.user.participant:
                new_p = form.cleaned_data
                request.user.participant.team.name = f'{new_p["lastname"]} {new_p["firstname"]} {new_p["secondname"]}'
                request.user.participant.team.save()
            return redirect('team-detail')

        return self.render_page(
            request,
            self.template_name,
            {
                'form':form,
            }
        )


class ChangeCoachView(LanguageMixin, LoginRequiredMixin, View):
    model = Coach
    template_name = 'main/coach.html'
    form_class = CreateCoachForm

    def get(self, request, *args, **kwargs):
        if not request.user.participant.team or \
            request.user.participant.team.status != 'in progress' or \
            not request.user.participant.team.coach:
            return redirect('team-detail')

        _coach = request.user.participant.team.coach
        form = self.form_class(instance=_coach)
        return self.render_page(
            request,
            self.template_name,
            {
                'form':form,
            }
        )

    def post(self, request, *args, **kwargs):
        if not request.user.participant.team or \
            request.user.participant.team.status != 'in progress' or \
            not request.user.participant.team.coach:
            return redirect('team-detail')

        _coach = request.user.participant.team.coach
        form = self.form_class(request.POST, instance=_coach)

        if form.is_valid():
            form.save()

            return redirect('team-detail')

        return self.render_page(
            request,
            self.template_name,
            {
                'form':form,
            }
        )

class VerifyView(LanguageMixin, LoginRequiredMixin, View):
    template_name = 'main/verify.html'

    def get(self, request, *args, **kwargs):
        if not request.user.participant.team or\
            not request.user.participant.team.is_ready:
            return redirect('team-detail')

        return self.render_page(
            request,
            self.template_name,
        )

    def post(self, request, *args, **kwargs):
        if not request.user.participant.team or\
            not request.user.participant.team.is_ready:
            return redirect('team-detail')

        request.user.participant.team.status = 'checking'
        request.user.participant.team.save()

        return redirect('team-detail')


class TeamInfoView(View):

    def get_team(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Team, id=id_)

    def get(self, request, *args, **kwargs):
        team = self.get_team()

        data = {
            "id": team.id,
            "name": team.name,
            "location": team.location,
        }

        return HttpResponse(
            json.dumps(data),
            status=200,
            content_type='application/json; charset=utf-8'
        )
