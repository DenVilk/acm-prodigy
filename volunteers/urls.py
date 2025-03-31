from django.urls import path
from volunteers.views import (
    EventDetailView,
    ParticipationDetailView,
    IndexView,
    LocationsListView,
    SignUpView,
    UserLoginView,
    create_volunteer,
)

urlpatterns = [
    path('', IndexView.as_view(), name='volunteers-index'),
    path('events/<int:id>', EventDetailView.as_view(), name='event-detail'),
    path('participation/<int:id>', ParticipationDetailView.as_view(), name='participation-detail'),
    path('locations', LocationsListView.as_view(), name='locations-list'),
    path('login', UserLoginView.as_view(), name='volunteers-login'),
    path('signup', SignUpView.as_view(), name='volunteers-signup'),
    path('create', create_volunteer, name='create-volunteer'),
]