from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SendEmail
from .serializers import SendEmailSerializer
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import os
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django
django.setup()



def send_dynamic_email(emails):
    template_name = 'email_template.html'
    rendered_string = render_to_string(template_name)
    email = EmailMultiAlternatives(
        subject="Invoice details",
        body="This is the plain text version.",
        from_email='sahildhiman98765@gmail.com',
        to=emails,
    )

    # Attach the HTML content
    email.attach_alternative(rendered_string, "text/html")

    # Send email
    status = email.send()

    print(status, '=====')





class SendEmailList(APIView):
    def get(self, request, format=None):
        send_emails = SendEmail.objects.all()
        serializer = SendEmailSerializer(send_emails, many=True)
        return Response(serializer.data)

    def post(self, request):
        emails = request.data.get('emails')

        send_dynamic_email(emails)

        return Response({'email_sent': True, 'message': 'Email sent successfully'}, status=status.HTTP_201_CREATED)