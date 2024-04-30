from rest_framework import serializers
from .models import SendEmail,GroupEmails,Products, Emails, EmailList, Profile
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id','username', 'password', 'email']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class SendEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendEmail
        fields = ['email']


class SendEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupEmails
        fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['id', 'name', 'price', 'image']


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emails
        fields = ['emails']

class EmailListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailList
        fields = ['id', 'group_name', 'email']


class GroupEmailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupEmails
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'user', 'full_name', 'profile_image', 'phone_number']

class GroupEmailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupEmails
        fields = '__all__'
