from rest_framework import serializers
from .models import SendEmail

class SendEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendEmail
        fields = ['email']
