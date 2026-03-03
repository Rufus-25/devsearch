from django.db.models.signals import post_delete, post_save
from django.contrib.auth.models import User

from .models import Profile


def createProfile(sender, instance, created, **kwargs):
    if created:
        user = instance
        Profile.objects.create(
            user=user,
            username = user.username,
            email = user.email,
            name = user.first_name,
            )


def updateUser(sender, instance, created, **kwargs):
    profile = instance
    user = profile.user

    if created == False:
        user.email = instance.email
        user.username = profile.username
        user.first_name = profile.name
        user.save()


def deleteUser(sender, instance, **kwargs):
    try:
        user = instance.user
        user.delete()
    except:
        pass


post_save.connect(createProfile, sender=User)
post_save.connect(updateUser, sender=Profile)
post_delete.connect(deleteUser, sender=Profile)