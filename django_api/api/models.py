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

class EquipCategories(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    parent_id = models.BigIntegerField(blank=True, null=True)
    whole_name = models.CharField(max_length=45)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'equip_categories'


class EquipHistories(models.Model):
    id = models.BigIntegerField(primary_key=True)
    equip_item = models.ForeignKey('EquipItems', models.DO_NOTHING)
    user = models.ForeignKey(User, models.DO_NOTHING)
    user_name = models.CharField(max_length=255)
    org_status = models.CharField(max_length=45)
    new_status = models.CharField(max_length=45)
    description = models.TextField(blank=True, null=True)
    recorded_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'equip_histories'


class EquipImages(models.Model):
    type = models.CharField(primary_key=True, max_length=45)
    id = models.CharField(max_length=45)
    name = models.CharField(max_length=200)
    file_path = models.CharField(max_length=255, blank=True, null=True)
    file_bytes_str = models.TextField()
    created_at = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'equip_images'
        unique_together = (('type', 'id'),)


class EquipItems(models.Model):
    id = models.CharField(primary_key=True, max_length=45)
    equip = models.ForeignKey('Equipments', models.DO_NOTHING)
    order = models.CharField(max_length=45)
    status = models.CharField(max_length=45)
    buy_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    last_user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)
    last_lend_at = models.DateTimeField(blank=True, null=True)
    last_return_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    is_lend = models.IntegerField(blank=True, null=True)
    is_return = models.IntegerField(blank=True, null=True)
    is_broke = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'equip_items'


class Equipments(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255)
    cate = models.ForeignKey(EquipCategories, models.DO_NOTHING)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    image_name = models.TextField(blank=True, null=True)
    image_full_path = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'equipments'

class MeetingEntries(models.Model):
    id = models.BigAutoField(primary_key=True)
    church_id = models.CharField(unique=True, max_length=100)
    church_name = models.CharField(unique=True, max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'meeting_entries'