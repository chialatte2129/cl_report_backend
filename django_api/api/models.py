# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models 
from django.core.validators import MinLengthValidator, RegexValidator
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.fields.related import ManyToManyField
from django.db.models.fields import DateTimeField
from django_mysql.models import JSONField

# Create your models here.
class Role(models.Model):
    role_id = models.CharField(max_length=30)
    description = models.CharField(max_length=50)    
    menus_id = models.TextField()
    def __str__(self):
        """String for representing the Model object."""
        return self.description


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    roles_id = models.TextField()
    user_info = models.TextField()
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class DictionarySetting(models.Model):
    keystr = models.CharField(db_column='Keystr', primary_key=True, max_length=50)  # Field name made lowercase.
    category = models.CharField(db_column='Category', max_length=50)  # Field name made lowercase.
    jsonvalue = models.TextField(db_column='JsonValue')  # Field name made lowercase.
    description = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dictionary_setting'
