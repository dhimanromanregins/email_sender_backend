from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from rest_framework import status
from .models import SendEmail,EmailList,GroupEmails,Profile, GroupEmails,Products,DefaultEmailDetails,Emails,TemplateEmail
from .serializers import SendEmailSerializer, UserSerializer,GroupEmailsSerializer,ProfileSerializer,GroupEmailsSerializer, EmailListSerializer,ProductSerializer,EmailSerializer
from rest_framework.authtoken.models import Token
from django.template.loader import render_to_string
import os
import random
from django.conf import settings
from rest_framework import generics
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User
from django.http import Http404
from email.mime.image import MIMEImage

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

            # Serialize user data
            user_serializer = UserSerializer(user)
            user_data = user_serializer.data

            # Include user data along with the token in the response
            response_data = {
                'token': token.key,
                'user': user_data
            }

            return Response(response_data)
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


def send_dynamic_email(email, name=None, price=None, sender_name=None):
    template_name = 'email_template.html'
    random_number = generate_random_5_digit_number()
    default_email_details = DefaultEmailDetails.objects.get(type='default')
    profile_img_url = default_email_details.image.url if default_email_details.image else None
    if profile_img_url:
        full_image_path = "http://127.0.0.1:8000" + profile_img_url
        print(full_image_path, '===========')
    else:
        print("No default image found.")

    image_attachment = None
    if profile_img_url:
        image_file_path = os.path.join(settings.BASE_DIR, profile_img_url.strip('/'))
        with open(image_file_path, 'rb') as logo_file:
            logo_data = logo_file.read()
            logo_mime = MIMEImage(logo_data, _subtype='jpeg')
            logo_mime.add_header('Content-ID', 'logo')
            image_attachment = logo_mime

    if name is not None and price is not None and sender_name is not None:
        context = {
            'name': name,
            'amount': price,
            'email': email,
            'sender_name': sender_name,
            'invoice': random_number,
            'img': full_image_path
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
        if image_attachment:
            email.attach(image_attachment)
        status = email.send()

    else:
        default_data = DefaultEmailDetails.objects.get(type='default')
        context = {
            'name': default_data.name,
            'amount': default_data.price,
            'email': email,
            'sender_name': default_data.sender_name,
            'invoice': random_number,
            'img': profile_img_url
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
        if image_attachment:
            email.attach(image_attachment)
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
        group_id = GroupEmails.objects.get(group_name=group_name).id
        group_emails = EmailList.objects.filter(group_name=group_id)
        email_list = []
        for group_email in group_emails:
            email_list.append(group_email.email)
        if name is not None and price is not None and sender_name is not None:
            send_dynamic_email(email_list, name=name, price=price, sender_name=sender_name)
        else:
            send_dynamic_email(email_list)

        return True, "Emails sent successfully to the group '{}'".format(group_name)
    except GroupEmails.DoesNotExist:
        return False, "Group '{}' does not exist".format(group_name)

class SendEmailGroup(APIView):
    def get(self, request, format=None):
        send_emails = GroupEmails.objects.all()
        serializer = SendEmailSerializer(send_emails, many=True)
        return Response(serializer.data)

    def post(self, request):
        print(request.data, '==========')
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





class GroupEmailsList(APIView):
    def get(self, request):
        groups = GroupEmails.objects.all()
        data = []
        for grp in groups:
            count = EmailList.objects.filter(group_name=grp.id).count()
            serializer = GroupEmailsSerializer(grp)
            group_data = serializer.data
            group_data['email_count'] = count
            data.append(group_data)

        return Response(data)

    def post(self, request):
        serializer = GroupEmailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GroupEmailsDetail(APIView):
    def get_object(self, pk):
        try:
            return GroupEmails.objects.get(pk=pk)
        except GroupEmails.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        group = self.get_object(pk)
        serializer = GroupEmailsSerializer(group)
        return Response(serializer.data)

    def put(self, request, pk):
        group = self.get_object(pk)
        serializer = GroupEmailsSerializer(group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        group = self.get_object(pk)
        serializer = GroupEmailsSerializer(group, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        group = self.get_object(pk)
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfileAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Get profiles associated with the current user
        profiles = Profile.objects.filter(user=request.user.id)
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        # Assign current user to profile being created
        request.data['user'] = request.user.id
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileDetailAPIView(APIView):
    def get_object(self, user_id):
        return get_object_or_404(Profile, user_id=user_id)

    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        print(user_id, '==========')
        if not user_id:
            return Response({'error': 'User ID parameter is missing.'}, status=status.HTTP_400_BAD_REQUEST)
        profile = self.get_object(user_id)
        print(profile.user.id, '+==')

        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request, user_id, *args, **kwargs):
        profile = self.get_object(user_id)
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, user_id, *args, **kwargs):
        profile = self.get_object(user_id)

        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id, *args, **kwargs):
        profile = self.get_object(user_id)

        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)