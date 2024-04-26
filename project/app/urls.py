from django.urls import path
from .views import SendEmailList, SendBulkEmail,SendEmailGroup

urlpatterns = [
    path('send-email/', SendEmailList.as_view(), name='send-email-list'),
    path('send-email/', SendEmailList.as_view(), name='send_email'),
    path('send-bulk-email/', SendBulkEmail.as_view(), name='send_bulk_email'),
    path('send-group-email/', SendEmailGroup.as_view(), name='send_group_email'),
]
