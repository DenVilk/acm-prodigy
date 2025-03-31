from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import get_object_or_404, redirect

from volunteers.models import Event, Volunteer


class VolunteerAccessMixin(AccessMixin):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not Volunteer.objects.filter(user=request.user).exists():
            messages.error(request, "У вас нет волонтерского аккаунта.")
            return redirect('volunteers-index')

        return super().dispatch(request, *args, **kwargs)

class VolunteerEventAccessMixin(AccessMixin):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not Volunteer.objects.filter(user=request.user).exists():
            messages.error(request, "У вас нет волонтерского аккаунта.")
            return redirect('volunteers-index')

        event_id = kwargs.get('id')
        event = get_object_or_404(Event, id=event_id)

        if not event.volunteers.filter(volunteer=request.user.volunteer).exists() and \
            not request.user.is_superuser:
            messages.error(request, "Вы не участвуете в мероприятии.")
            return redirect('volunteers-index')

        return super().dispatch(request, *args, **kwargs)