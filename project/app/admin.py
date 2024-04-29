from django.contrib import admin
from .models import SendEmail, EmailList, GroupEmails, Emails,TemplateEmail,DefaultEmailDetails, Products
# Register your models here.
admin.site.register(SendEmail)
admin.site.register(EmailList)
admin.site.register(GroupEmails)
admin.site.register(TemplateEmail)
admin.site.register(DefaultEmailDetails)
admin.site.register(Products)
admin.site.register(Emails)