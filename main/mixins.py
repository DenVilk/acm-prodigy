from django.shortcuts import render
from main.models import Translation
from volunteers.models import Event, Volunteer


class LanguageMixin:

    def get_user_language(self, request):
        user_language = request.GET.get('lang') or request.session.get('language', 'ru')

        if user_language:
            request.session['language'] = user_language

        return user_language

    def get_translations(self, language):
        translations = Translation.objects.filter(language=language)
        return {
            translation.translation_key.key: translation.translated_text
            for translation in translations
        }

    def __get_events(self, request):
        volunteer_events = set(Event.objects.none())
        if request.user.is_authenticated and \
            Volunteer.objects.filter(user=request.user).exists()\
        :
            volunteer_events = set(
                [
                    application.event
                    for application in request.user.volunteer.applications.all()
                ]
            )

        return volunteer_events | set(Event.objects.filter(is_open=True))

    def render_page(self, request, template_name, context=None):
        if context is None:
            context = {}

        user_language = self.get_user_language(request)
        translations_dict = self.get_translations(user_language)
        events = self.__get_events(request)

        _context = {
            'tr': translations_dict,
            'selected_language': user_language,
            'events': events,
        }

        _context.update(context)
        return render(request, template_name, _context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if context is None:
            context = {}

        user_language = self.get_user_language(self.request)
        translations_dict = self.get_translations(user_language)
        events = self.__get_events(self.request)

        _context = {
            'tr': translations_dict,
            'selected_language': user_language,
            'events': events,
        }

        _context.update(context)
        return _context