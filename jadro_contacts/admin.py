from django.contrib import admin
from django.contrib.admin.util import flatten_fieldsets
from django.forms.models import fields_for_model
from models import RawContact, Phone, Photo, GroupMembership

class ReadOnlyAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        fields = set(super(ReadOnlyAdmin,self).get_readonly_fields(request, obj))
        if self.declared_fieldsets:
            fields.update(flatten_fieldsets(self.declared_fieldsets))
        else:
            fields.update(fields_for_model(self.model).keys())
        return list(fields)

class ContactAdmin(ReadOnlyAdmin):
    pass

class DataInline(admin.StackedInline):
    extra = 0

class PhoneInline(DataInline):
    model = Phone
    readonly_fields = ('data_number', 'data_type', 'data_label')

class PhotoInline(DataInline):
    model = Photo

class GroupMembershipInline(DataInline):
    model = GroupMembership

class RawContactAdmin(ContactAdmin):
    fields = ['display_name', 'times_contacted', 'last_time_contacted']
    list_display = ['display_name', 'display_phone', 'display_photo']
    list_filter = ['groups', 'last_time_contacted']
    ordering = ['-last_time_contacted']
    search_fields = ['display_name']
    inlines = [ PhoneInline, PhotoInline, GroupMembershipInline ]

    def display_photo(self, obj):
        photos = obj.photos
        return photos and photos[0] or ''
    display_photo.short_description = 'photo'
    display_photo.allow_tags = True

    def display_phone(self, obj):
        phones = obj.phones
        return phones and phones[0] or ''
    display_phone.short_description = 'phone'
       
admin.site.register(RawContact, RawContactAdmin)

