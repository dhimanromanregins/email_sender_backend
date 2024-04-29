from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework import status
from .models import SendEmail,EmailList,GroupEmails,Profile, GroupEmails,Products,DefaultEmailDetails,Emails,TemplateEmail
from .serializers import SendEmailSerializer, UserSerializer,ProfileSerializer,GroupEmailsSerializer, EmailListSerializer,ProductSerializer,EmailSerializer
from django.core.mail import send_mail
from rest_framework.authtoken.models import Token
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import os
import random
from rest_framework import generics
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.models import User
from django.http import Http404

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django
django.setup()



class UserLoginAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        print(username, password, '========')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserRegisterAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(username=serializer.data['username'])
            token, created = Token.objects.get_or_create(user=user)  # Modify this line
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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



class ProductList(APIView):
    def get(self, request):
        products = Products.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDetail(APIView):
    def get_object(self, pk):
        try:
            return Products.objects.get(pk=pk)
        except Products.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = self.get_object(pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailCountByGroup(APIView):
    def get(self, request, format=None):
        groups = GroupEmails.objects.all()
        email_counts_by_group = {}
        for group in groups:
            email_count = EmailList.objects.filter(group_name=group).count()
            email_counts_by_group[group.group_name] = email_count

        return Response(email_counts_by_group)



class EmailsList(APIView):
    def get(self, request):
        emails = Emails.objects.all()
        serializer = EmailSerializer(emails, many=True)
        return Response(serializer.data)

    def post(self, request):
        emails = request.data.get('emails', [])  # Extracting the list of emails from request.data
        if not emails:
            return Response({"error": "No emails provided"}, status=status.HTTP_400_BAD_REQUEST)

        saved_emails = []
        errors = []
        print(emails, '==============')

        for email in emails:
            print(email, '=====')
            serializer = EmailSerializer(data={'emails': email})  # Use EmailSerializer here
            if serializer.is_valid():
                serializer.save()
                saved_emails.append(serializer.data)
            else:
                errors.append(serializer.errors)

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"saved_emails": saved_emails}, status=status.HTTP_201_CREATED)

class EmailsDetail(APIView):
    def get_object(self, pk):
        try:
            return Emails.objects.get(pk=pk)
        except Emails.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        email = self.get_object(pk)
        serializer = EmailSerializer(email)
        return Response(serializer.data)

    def put(self, request, pk):
        email = self.get_object(pk)
        serializer = EmailSerializer(email, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        email = self.get_object(pk)
        serializer = EmailSerializer(email, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        email = self.get_object(pk)
        email.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailListView(APIView):
    def get(self, request):
        emails = EmailList.objects.all()
        serializer = EmailListSerializer(emails, many=True)
        return Response(serializer.data)

    def post(self, request):
        group_id = request.data.get("id")
        groupId = GroupEmails.objects.get(group_name=group_id)
        print(groupId.id, '-------------')
        email_list = request.data.get("email", [])
        created_emails = []
        for email in email_list:
            serializer = EmailListSerializer(data={"group_name": groupId.id, "email": email})
            if serializer.is_valid():
                serializer.save()
                created_emails.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(created_emails, status=status.HTTP_201_CREATED)

class EmailDetailView(APIView):
    def get_object(self, pk):
        try:
            return EmailList.objects.get(pk=pk)
        except EmailList.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        email = self.get_object(pk)
        serializer = EmailListSerializer(email)
        return Response(serializer.data)

    def put(self, request, pk):
        email = self.get_object(pk)
        serializer = EmailListSerializer(email, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        email = self.get_object(pk)
        serializer = EmailListSerializer(email, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        email = self.get_object(pk)
        email.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GroupEmailsListAPIView(generics.ListAPIView):
    queryset = GroupEmails.objects.all()
    serializer_class = GroupEmailsSerializer


class ProfileAPIView(APIView):
    def get(self, request, pk=None):
        # If pk is provided, retrieve a specific profile, else retrieve all profiles
        if pk:
            profile = Profile.objects.get(pk=pk)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        else:
            profiles = Profile.objects.all()
            serializer = ProfileSerializer(profiles, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        profile = Profile.objects.get(pk=pk)
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        profile = Profile.objects.get(pk=pk)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        profile = Profile.objects.get(pk=pk)
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)