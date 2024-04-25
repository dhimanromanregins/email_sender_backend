from django.urls import path
from .views import SendEmailList

urlpatterns = [
    path('send-email/', SendEmailList.as_view(), name='send-email-list'),
]
