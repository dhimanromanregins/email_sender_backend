from rest_framework import serializers
from .models import SendEmail,GroupEmails

class SendEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendEmail
        fields = ['email']


class SendEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupEmails
        fields = "__all__"
