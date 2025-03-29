from django.urls import path
from volunteers.views import (
    IndexView,
    SignUpView,
    UserLoginView,
    create_volunteer,
)

urlpatterns = [
    path('', IndexView.as_view(), name='volunteers-index'),
    path('login', UserLoginView.as_view(), name='volunteers-login'),
    path('signup', SignUpView.as_view(), name='volunteers-signup'),
    path('create', create_volunteer, name='create-volunteer'),
]