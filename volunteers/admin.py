from django.contrib import admin
from volunteers.models import (
    Volunteer,
    VolunteerParticipation,
    VolunteerPositions,
    Locations,
    Event,
)

admin.site.register(Volunteer)
admin.site.register(VolunteerParticipation)
admin.site.register(VolunteerPositions)
admin.site.register(Locations)
admin.site.register(Event)
