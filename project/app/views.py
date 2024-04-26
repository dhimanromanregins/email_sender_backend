from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SendEmail,EmailList,GroupEmails, DefaultEmailDetails,TemplateEmail
from .serializers import SendEmailSerializer
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import os
import random
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django
django.setup()


def generate_random_5_digit_number():
    # Generate a random integer between 10000 and 99999 (inclusive)
    return random.randint(10000, 99999)


def send_dynamic_email(email, name=None , price=None, sender_name=None):
    template_name = 'email_template.html'
    random_number = generate_random_5_digit_number()
    print(email, '==============')
    if name is not None and price is not None and sender_name is not None:
        context = {
            'name': name,
            'amount': price,
            'email': email,
            'sender_name': sender_name,
            'invoice':random_number
        }
        rendered_string = render_to_string(template_name, context)
        default_data_email = TemplateEmail.objects.get(type='default')
        email = EmailMultiAlternatives(
            subject=default_data_email.subject,
            body=default_data_email.body,
            from_email=default_data_email.email,
            to=email.split(','),
        )
        email.attach_alternative(rendered_string, "text/html")
        status = email.send()

    else:
        default_data = DefaultEmailDetails.objects.get(type='default')
        context = {
            'name': default_data.name,
            'amount': default_data.price,
            'email':email,
            'sender_name':default_data.sender_name,
            'invoice': random_number
        }
        rendered_string = render_to_string(template_name, context)
        default_data_email = TemplateEmail.objects.get(type='default')
        email = EmailMultiAlternatives(
            subject=default_data_email.subject,
            body="This is the plain text version.",
            from_email=default_data_email.email,
            to=email,
        )
        email.attach_alternative(rendered_string, "text/html")
        status = email.send()



class SendEmailList(APIView):
    def get(self, request, format=None):
        send_emails = SendEmail.objects.all()
        serializer = SendEmailSerializer(send_emails, many=True)
        return Response(serializer.data)

    def post(self, request):
        email = request.data.get('email')
        name = request.data.get('name')
        price = request.data.get('price')
        sender_name = request.data.get('sender_name')
        if name is not None and price is not None and sender_name is not None:
            send_dynamic_email(email, name=name, price=price, sender_name=sender_name)
        else:
            send_dynamic_email(email)
        return Response({'email_sent': True, 'message': 'Email sent successfully'}, status=status.HTTP_201_CREATED)


class SendBulkEmail(APIView):
    def post(self, request):
        send_emails = EmailList.objects.all()
        for send_email in send_emails:
            email = [send_email.email]
            send_dynamic_email(email)
        return Response({'email_sent': True, 'message': 'Bulk email sent successfully'}, status=status.HTTP_201_CREATED)


def send_emails_in_group(group_name, name=None, price=None, sender_name=None):
    try:
        group_emails = GroupEmails.objects.filter(group_name=group_name)
        for group_email in group_emails:
            email = [group_email.email.email]
            if name is not None and price is not None and sender_name is not None:
                send_dynamic_email(email, name=name, price=price, sender_name=sender_name)
            else:
                send_dynamic_email(email)
        return True, "Emails sent successfully to the group '{}'".format(group_name)
    except GroupEmails.DoesNotExist:
        return False, "Group '{}' does not exist".format(group_name)

class SendEmailGroup(APIView):

    def get(self, request, format=None):
        send_emails = GroupEmails.objects.all()
        serializer = SendEmailSerializer(send_emails, many=True)
        return Response(serializer.data)

    def post(self, request):
        group_name = request.data.get('group_name')
        name = request.data.get('name')
        price = request.data.get('price')
        sender_name = request.data.get('sender_name')

        if name is not None and price is not None and sender_name is not None:
            if group_name:
                success, message = send_emails_in_group(group_name, name, price, sender_name)
                if success:
                    return Response({'email_sent': True, 'message': message}, status=status.HTTP_200_OK)
                else:
                    return Response({'email_sent': False, 'message': message}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'email_sent': False, 'message': 'Group name is required'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if group_name:
                success, message = send_emails_in_group(group_name)
                if success:
                    return Response({'email_sent': True, 'message': message}, status=status.HTTP_200_OK)
                else:
                    return Response({'email_sent': False, 'message': message}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'email_sent': False, 'message': 'Group name is required'}, status=status.HTTP_400_BAD_REQUEST)
