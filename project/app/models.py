from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class SendEmail(models.Model):
    email = models.EmailField()

    def __str__(self):
        return self.email
class EmailList(models.Model):
    email = models.EmailField()

    def __str__(self):
        return self.email

class GroupEmails(models.Model):
    email = models.ForeignKey(EmailList, on_delete=models.CASCADE)
    group_name = models.CharField(max_length=255)

    def __str__(self):
        return self.group_name


class TemplateEmail(models.Model):
    subject = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    body = models.TextField()

    def __str__(self):
        return self.subject
@receiver(post_save, sender=TemplateEmail)
def ensure_single_instance(sender, instance, created, **kwargs):
    if created:
        # Ensure there's only one instance by deleting all other instances
        sender.objects.exclude(pk=instance.pk).delete()

# To update the existing instance or create one if it doesn't exist
def update_or_create_default_email_details(name, email, price):
    instance, created = TemplateEmail.objects.get_or_create(defaults={'subject': name, 'email': email})
    if not created:
        instance.name = name
        instance.email = email
        instance.price = price
        instance.save()
    return instance



class DefaultEmailDetails(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    price = models.IntegerField()
    type = models.CharField(max_length=255)
    sender_name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

@receiver(post_save, sender=DefaultEmailDetails)
def ensure_single_instance(sender, instance, created, **kwargs):
    if created:
        # Ensure there's only one instance by deleting all other instances
        sender.objects.exclude(pk=instance.pk).delete()

# To update the existing instance or create one if it doesn't exist
def update_or_create_default_email_details(name, email, price):
    instance, created = DefaultEmailDetails.objects.get_or_create(defaults={'name': name, 'email': email, 'price': price})
    if not created:
        instance.name = name
        instance.email = email
        instance.price = price
        instance.save()
    return instance

