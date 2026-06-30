from django.db.models.signals import post_delete, post_save
from django.contrib.auth.models import User

from django.core.mail import send_mail
from django.conf import settings

from .models import Profile


# Create a profile and send an email when new user is created
def createProfile(sender, instance, created, **kwargs):
    if created:
        user = instance
        profile = Profile.objects.create(
            user=user,
            username = user.username,
            email = user.email,
            name = user.first_name,
            )
        
        subject = "Welcome to DevSearch!"
        body = "Congrats! You've successfully signed up on DevSearch. You can go ahead and complete your profile."

        send_mail(
            subject,
            body,
            settings.EMAIL_HOST_USER,
            [profile.email],
            fail_silently=True,
        )


# Update core user details when updated in profile
def updateUser(sender, instance, created, **kwargs):
    profile = instance
    user = profile.user

    if created == False:
        user.email = instance.email
        user.username = profile.username
        user.first_name = profile.name
        user.save()


# Delete a user once the profile is deleted
def deleteUser(sender, instance, **kwargs):
    try:
        user = instance.user
        user.delete()
    except:
        pass


post_save.connect(createProfile, sender=User)
post_save.connect(updateUser, sender=Profile)
post_delete.connect(deleteUser, sender=Profile)