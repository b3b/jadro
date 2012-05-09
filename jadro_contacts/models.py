import base64
import time
import datetime
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import QuerySet
from django.utils.safestring import mark_safe

class Mimetype(models.Model):
    class Meta:
        db_table = u'mimetypes'
    _id = models.IntegerField(primary_key=True)
    mimetype = models.TextField(unique=True)

class Group(models.Model):
    class Meta:
        db_table = u'groups'
    _id = models.IntegerField(primary_key=True)
    title = models.TextField(blank=True)
    title_res = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    system_id = models.TextField(blank=True)
    user_defined_title = models.IntegerField()
    
    def __unicode__(self):
        return u"%s" % (self.title)

class TimestampField(models.DateTimeField):
     __metaclass__ = models.SubfieldBase
     def to_python(self, value):
         return value and datetime.datetime.fromtimestamp(value / 1000) or None
     def get_prep_value(self, value):
         return super(TimestampField, self).to_python(value)
     def get_db_prep_value(self, value, connection, prepared=False):
        if not prepared:
            value = self.get_prep_value(value)
        return time.mktime(value.timetuple()) * 1000

class Call(models.Model):
    call_types_choices = ((1, 'incoming'), (2, 'outgoing'), (3, 'missed'))
    class Meta:
        db_table = u'calls'
        ordering = ['-date']
    _id = models.IntegerField(primary_key=True)
    number = models.TextField(blank=True)
    name = models.TextField(blank=True)
    date = TimestampField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    data_type = models.IntegerField('type', null=True, blank=True, db_column='type', choices=call_types_choices)
    acknowledged = models.NullBooleanField(null=True, blank=True, db_column='new')

class Contact(models.Model):
    class Meta:
        db_table = u'contacts'
    _id = models.IntegerField(primary_key=True)
    name_raw_contact_id = models.IntegerField(null=True, blank=True)
    photo_id = models.IntegerField(null=True, blank=True)
    custom_ringtone = models.TextField(blank=True)
    send_to_voicemail = models.IntegerField()
    times_contacted = models.IntegerField()
    last_time_contacted = models.IntegerField(null=True, blank=True)
    starred = models.IntegerField()
    in_visible_group = models.IntegerField()
    has_phone_number = models.IntegerField()
    has_email_address = models.IntegerField()
    lookup = models.TextField(blank=True)
    status_update_id = models.IntegerField(null=True, blank=True)
    single_is_restricted = models.IntegerField()

class DataManager(models.Manager):
    def __init__(self, mimetype=None, *args, **kwargs):
        self._mimetype = mimetype
        return super(DataManager,self).__init__(*args, **kwargs)
    def get_query_set(self):
        QS = getattr(self, '_queryset_class', QuerySet)
        qs = QS(self.model, using=self._db)
        if self._mimetype:
            qs = qs.filter(mimetype__mimetype=self._mimetype)
        return qs

class PhoneQuerySet(QuerySet):
    def filter_type(self, phone_types=[]):
        def name_index(tname):
            return self.model.phone_types.index(tname)
        phone_types = map(name_index, phone_types)
        return self.filter(data_type__in=phone_types)

class PhoneManager(DataManager):
    _queryset_class = PhoneQuerySet

class Data(models.Model):
    class Meta:
        abstract = True
    id = models.IntegerField(primary_key=True, editable=False, db_column='_id')
    mimetype = models.ForeignKey('Mimetype', editable=False)

class Phone(Data):
    objects = PhoneManager('vnd.android.cursor.item/phone_v2')
    phone_types = ('custom', 'home', 'mobile', 'work',
                   'fax-work', 'fax-home', 'pager', 'other')
    class Meta:
        db_table = u'data'
        managed = False
    data_number = models.TextField('number', db_column='data1')
    data_type = models.IntegerField('type', db_column='data2', choices=enumerate(phone_types))
    data_label = models.TextField('custom type', db_column='data3')
    raw_contact = models.ForeignKey('RawContact', related_name='contact_phones')

    @property
    def phone_type(self):
        return int(self.data_type) and (self.phone_types[int(self.data_type)]) or self.data_label

    def __unicode__(self):
        return u"%s" % self.data_number

class Photo(Data):
    objects = DataManager('vnd.android.cursor.item/photo')
    class Meta:
        db_table = u'data'
        managed = False
    data_thumbnail = models.TextField('photo', db_column='data15')
    raw_contact = models.ForeignKey('RawContact', related_name='contact_photos')

    def __unicode__(self):
        return mark_safe(u"<img src='data:image/png;base64,%s' alt='photo' />" % (
            base64.encodestring(self.data_thumbnail)
            ))

class GroupMembership(Data):
    objects = DataManager('vnd.android.cursor.item/group_membership')
    class Meta:
        db_table = u'data'
        managed = False
    data_group = models.ForeignKey('Group', verbose_name='group', db_column='data1')
    raw_contact = models.ForeignKey('RawContact')

    def __unicode__(self):
        return u"%s" % (self.data_group)

class RawContact(models.Model):
    class Meta:
        db_table = u'raw_contacts'
    _id = models.IntegerField(primary_key=True)
    contact = models.ForeignKey('Contact')
    times_contacted = models.PositiveIntegerField()
    last_time_contacted = TimestampField(null=True, blank=True)
    display_name = models.TextField('name', blank=True)
    groups = models.ManyToManyField('Group', through='GroupMembership')

    def __unicode__(self):
        return u"%s" % (self.display_name)

    @property
    def photos(self):
        return Photo.objects.filter(raw_contact=self)

    @property
    def phones(self):
        return Phone.objects.filter(raw_contact=self)
