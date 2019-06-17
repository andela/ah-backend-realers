from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from authors.apps.core.models import TimestampedModel
class Profile(TimestampedModel):

    gender_choices = [
        ('male', 'Male Person'),
        ('female', 'Female Person'),
        ('other', 'I dont what to specify'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, to_field='username', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, default='')
    last_name = models.CharField(max_length=50, default='')
    image = models.URLField(blank=True)
    gender = models.CharField(max_length=6, choices=gender_choices, default='')
    bio = models.TextField(max_length=300, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    # profiles means profile models and symmetrical prevents default follow back
    following = models.ManyToManyField(
        'self', related_name='followed_by', symmetrical=False)

    def __str__(self):
        """
        Returns a string representation of this `Profile`.

        This string is used when a `Profile` is printed in the console.
        """
        return self.user.username

    def unfollow(self, profile):
        """
        method to unfollow an author
        """
        self.following.remove(profile)

    def follow(self, profile):
        """
        method to follow another author 
        """
        self.following.add(profile)

    def is_following(self, profile):
        return self.following.filter(pk=profile.pk).exists()



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created: # pragma: no cover
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save() # pragma: no cover
