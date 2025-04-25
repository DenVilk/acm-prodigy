import requests
from uuid import uuid4
from django.contrib import admin
from django.conf import settings
from django.http import HttpResponse

from main.utils import Configuration
from main.models import (
    AcceptedSolution,
    Participant,
    Team,
    Coach,
    TranslationKey,
    Translation,
    Settings,
)

admin.site.site_header = f'ACM (ver. {settings.VERSION})'


@admin.register(AcceptedSolution)
class SolutionAdmin(admin.ModelAdmin):
    list_display = (
        'user_id',
        'problem_id',
        'problem_title',
        'user_title',
    )

@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'value',
    )


class TranslationInline(admin.TabularInline):
    model = Translation
    extra = 1
    min_num = 1
    max_num = len(Translation.LANGUAGES)


@admin.register(TranslationKey)
class TranslationKeyAdmin(admin.ModelAdmin):
    list_display = ('key',)
    search_fields = ('key',)
    inlines = [TranslationInline]


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'fullname',
        'email',
        'phone',
        'team',
        'education',
        'user__username',
    )
    search_fields = ['firstname', 'secondname', 'lastname', 'email', 'user__username']
    empty_value_display = 'unknown'


class ParticipantInline(admin.TabularInline):
    extra = 0
    model = Participant
    exclude = ['user']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    inlines = [ParticipantInline]
    list_display = (
        '__str__',
        'status',
        'type',
        'system_login'
    )
    search_fields = ['name', 'participants__lastname',
                     'coach__lastname', 'system_login']
    list_filter = (
        'status',
        'type',
        'is_generated_mail',
        'quaterfinal',
        'semifinal',
        'final',
        'disqualified'
    )
    actions = [
        'mark_as_sent',
        'mark_as_unsent',
        'export_logins_and_names',
        'export_system_logins',
        'export_for_registration',
        'export_bagdes',
        'export_coachs',
        'export_participants',
        'export_stream',
        'export_diploms',
        'count_statistics',
        'reset',
        'generate_users',
        'export_emails',
    ]

    @admin.action(description='Export users emails')
    def export_emails(self, request, queryset):
        mails = set()
        for team in queryset.all():
            for part in team.participants.all():
                mails.add(part.email.strip())
        mails = mails - set(('', None))
        return HttpResponse(', '.join(mails), content_type='text/plain; charset=utf-8')

    @admin.action(description='Mark selected teams as mail sent')
    def mark_as_sent(self, request, queryset):
        queryset.update(sent=True)

    @admin.action(description='Unmark selected teams as mail sent')
    def mark_as_unsent(self, request, queryset):
        queryset.update(sent=False)

    @admin.action(description='Export logins and team names')
    def export_logins_and_names(self, request, queryset):
        res = ''
        for team in queryset:
            surnames = []
            for part in team.participants.all():
                surnames.append(part.lastname)
            surname_str = ', '.join(surnames)
            res += f'{team.system_login} {team.name}: {surname_str}\n'
        return HttpResponse(res, content_type='text/plain; charset=utf-8')

    @admin.action(description="Export logins for Yandex")
    def export_system_logins(self, request, queryset):
        res = ''
        for team in queryset:
            res += f'{team.system_login}@contest.yandex.ru\n'
        return HttpResponse(res, content_type='text/plain')

    @admin.action(description="Export for registration list")
    def export_for_registration(self, request, queryset):
        res = ''
        for team in queryset:
            res += f'{team.name},{team.system_login},{team.system_password}\n'
        return HttpResponse(res, content_type='text/plain; charset=utf-8')

    @admin.action(description="Export users for badges")
    def export_bagdes(self, request, queryset):
        res = ''
        for team in queryset:
            for participant in team.participants.all():
                res += f'{participant.firstname}\t{participant.lastname}\t{team.name}\n'
        return HttpResponse(res, content_type='text/plain; charset=utf-8')

    @admin.action(description="Export coachs for badges")
    def export_coachs(self, request, queryset):
        res = ''
        s = set()
        for team in queryset:
            if team.coach:
                coach = team.coach
                s.add(f'{coach.firstname}\t{coach.lastname}\n')

        for coach in s:
            res += coach
        return HttpResponse(res, content_type='text/plain; charset=utf-8')

    @admin.action(description="export participants for registration")
    def export_participants(self, request, queryset):
        res = ''
        for team in queryset:
            res += f'{team.name}\n'
            for part in team.participants.all():
                res += f'{part.lastname} {part.firstname} {part.secondname}, {part.tshirt_size}\n'
        return HttpResponse(res, content_type='text/plain; charset=utf-8')

    @admin.action(description='export for stream')
    def export_stream(self, request, queryset):
        res = ''
        for team in queryset:
            res += f'"{team.system_login}":{{"shortname":"{team.name}"}},\n'
        return HttpResponse(res, content_type='text/plain; charset=utf-8')

    @admin.action(description='export for diploms')
    def export_diploms(self, request, queryset):
        res = ''
        for team in queryset:
            res += f'{team.name}\t'
            for part in team.participants.all():
                res += f'{part.lastname} {part.firstname}\t'
            if team.coach:
                res += f'{team.coach.lastname} {team.coach.firstname}'
            res += '\n'
        return HttpResponse(res, content_type='text/plain; charset=utf-8')

    @admin.action(description='Statistics of countries')
    def count_statistics(self, request, queryset):
        stat = {}
        for team in queryset:
            country = {}
            for part in team.participants.all():
                country[part.country.name] = country.get(
                    part.country.name, 0) + 1
            mx = 0
            c = ''
            for k, v in country.items():
                if v > mx:
                    mx = v
                    c = k
            if c in stat.keys():
                stat[c] += 1
            else:
                stat[c] = 1

        res = ''
        for k, v in stat.items():
            res += f'{k} {v}\n'

        return HttpResponse(res, content_type='text/plain; charset=utf-8')

    @admin.action(description='Reset passwords to Test System')
    def reset(self, request, queryset):
        queryset.update(system_login='', system_password='')

    @admin.action(description='Generate logins and password to teams in Test System')
    def generate_users(self, request, queryset):
        scope = Configuration('configuration.team.scope')
        prefix = Configuration('configuration.team.prefix')
        login = Configuration('configuration.solve.login')
        password = Configuration('configuration.solve.password')
        solve_url = Configuration('configuration.solve.url')

        login_resp = requests.post(
            f'{solve_url}/login',
            json={
                'login': login,
                'password': password
            }
        )

        if login_resp.status_code != 201:
            print('Not authenticated')
            return HttpResponse(
                '{"message": "Cannot authenticate in Solve System"}',
                status=500,
                content_type='application/json; charset=utf-8'
            )
        cookies = login_resp.cookies
        i = 0
        try:
            for team in queryset:
                if len(team.name) < 64:

                    code = uuid4().hex[:6].upper()
                    while Team.objects.filter(system_login=prefix + code).count():
                        code = uuid4().hex[:6].upper()
                    team.system_login = prefix + code

                    generate_resp = requests.post(
                        f'{solve_url}/scopes/{scope}/users/',
                        json={
                            'login': team.system_login,
                            'title': team.name
                        },
                        cookies=cookies,
                        headers={
                            'X-Solve-Sync': 'true'
                        }
                    )
                    team.system_login = f'{scope}/{team.system_login}'
                    team.system_password = generate_resp.json()["password"]
                    team.save()
                    i += 1

        except Exception as e:
            print(e)
            return HttpResponse(
                '{"message": "something went wrong."}',
                status=500,
                content_type='application/json; charset=utf-8'
            )
        finally:
            print(i)

        return HttpResponse('{"message": "OK."}', status=200, content_type='application/json; charset=utf-8')


# admin.site.register(Coach)


@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    search_fields = ['firstname', 'secondname', 'lastname', 'email',]
