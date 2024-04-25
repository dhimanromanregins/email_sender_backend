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



def send_dynamic_email(subject, name, email, price, mobile_number):
    # Construct HTML content with inline CSS
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email Template</title>
        <style>
            /* Your CSS styles here */
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #fff;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #007bff;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Hello, {name}!</h1>
            <p>Your email: {email}</p>
            <p>Price: {price}</p>
            <p>Mobile Number: {mobile_number}</p>
        </div>
    </body>
    </html>
    """

    # Create an EmailMultiAlternatives object to include both plain text and HTML content
    email = EmailMultiAlternatives(
        subject=subject,
        body="This is the plain text version.",
        from_email='sahildhiman98765@gmail.com',
        to=email,
    )

    # Attach the HTML content
    email.attach_alternative(html_content, "text/html")

    # Send email
    status = email.send()

    print(status, '=====')





class SendEmailList(APIView):
    def get(self, request, format=None):
        send_emails = SendEmail.objects.all()
        serializer = SendEmailSerializer(send_emails, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        for data in request.data:
            serializer = SendEmailSerializer(data=data)

            if serializer.is_valid():
                try:
                    serializer.save()
                    data = serializer.validated_data
                    # recipient_list = [data.get('recipient_list')]
                    name = data.get('name')
                    email = [data.get('email')]
                    price = data.get('price')
                    mobile_number = data.get('mobile_number')
                    print(data, '===========')
                    subject = "Test Email"
                    send_dynamic_email(subject, name, email, price, mobile_number)

                    # If email sent successfully, return success response

                except Exception as e:
                    # If an exception occurs during email sending, return error response
                    return Response({'email_sent': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'email_sent': True, 'message': 'Email sent successfully'}, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)