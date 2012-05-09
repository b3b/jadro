from django.contrib import admin
from django.contrib.admin.util import flatten_fieldsets, unquote
from django.contrib import messages
from django.template import Context, Template
from django.template.response import TemplateResponse
from django import forms
from django.forms.models import fields_for_model
from django.conf import settings
from models import RawContact, Phone, Photo, GroupMembership, Call

droid = settings.DROID_CONNECTION

class ReadOnlyAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        fields = set(super(ReadOnlyAdmin,self).get_readonly_fields(request, obj))
        if self.declared_fieldsets:
            fields.update(flatten_fieldsets(self.declared_fieldsets))
        else:
            fields.update(fields_for_model(self.model).keys())
        return list(fields)

class ContactAdmin(ReadOnlyAdmin):
    def has_add_permission(self, *args, **kwargs):
        return False

    def has_delete_permission(self, *args, **kwargs):
        return False

    def change_view(self, request, object_id, form_url='', extra_context=None):
        request.method = 'GET'
        return super(ContactAdmin, self).change_view(request, object_id, form_url, extra_context)

class DataInline(admin.StackedInline):
    can_delete = False
    max_num = 0
    extra = 0

class PhoneInline(DataInline):
    model = Phone
    fields = ('data_number', 'phone_type')
    readonly_fields = fields

class PhotoInline(DataInline):
    model = Photo

class GroupMembershipInline(DataInline):
    model = GroupMembership

class AdminActionForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    action = forms.CharField(widget=forms.HiddenInput())
    post = forms.CharField(widget=forms.HiddenInput(), initial='yes')

class SendSmsForm(AdminActionForm):
    message = forms.CharField(widget=forms.Textarea)

class RawContactAdmin(ContactAdmin):
    fields = ['display_name', 'times_contacted', 'last_time_contacted']
    list_display = ['display_name', 'display_phone', 'display_photo']
    list_filter = ['groups', 'last_time_contacted']
    ordering = ['-last_time_contacted']
    search_fields = ['display_name']
    inlines = [ PhoneInline, PhotoInline, GroupMembershipInline ]
    actions = ['call_phone', 'send_sms']

    def change_view(self, request, object_id, form_url='', extra_context=None):
        method = request.method
        request.method = 'GET'
        obj = self.get_object(request, unquote(object_id))
        if method == 'POST' and obj:
            if '_call' in request.POST:
                self.call_phone(request, (obj,))
            elif '_sms' in request.POST:
                return self.send_sms(request, (obj,))
            elif request.POST.get('action', None) == 'send_sms':
                request.method = 'POST'
                self.send_sms(request, (obj,))
        return super(RawContactAdmin, self).change_view(request, object_id, form_url, extra_context)

    def display_photo(self, obj):
        photos = obj.photos
        return photos and photos[0] or ''
    display_photo.short_description = 'photo'
    display_photo.allow_tags = True

    def display_phone(self, obj):
        phones = obj.phones
        return phones and phones[0] or ''
    display_phone.short_description = 'phone'

    def call_phone(modeladmin, request, queryset):
        if droid.startTrackingPhoneState().error:
            messages.error(request, 'Error tracking phone state')
            return
        def _call_phone(contact):
            def _error(msg):
                messages.error(request, 'Error calling %(contact)s: %(msg)s.' % {
                        'contact': contact, 'msg': msg})
            def _wait_for_state(phone_state, wait_count=None):
                state = ''
                while (state != phone_state) and ((wait_count) or (wait_count is None)):
                    r = droid.readPhoneState()
                    if r.error or not r.result.get('state', None):
                        break
                    state = r.result['state']
                    if state != phone_state:
                        r = droid.eventWaitFor('phone', 5 * 1000)
                        if r.error:
                            break
                    if wait_count:
                        wait_count -= 1
                return state
            phone = contact.phones and "%s" % (contact.phones[0])
            if not phone:
                _error('no phone')
                return
            if _wait_for_state('idle') != 'idle':
                _error('error getting phone state')
                return
            r = droid.phoneCallNumber(phone)
            if not r.error:
                messages.info(request, 'Called %(contact)s (%(phone)s).' % {
                        'contact': contact, 'phone': phone})
            else:
                messages.error(request, 'Error calling %(contact)s (%(phone)s).' % {
                        'contact': contact, 'phone': phone})
            _wait_for_state('offhook', 1)
            _wait_for_state('idle')
        map(_call_phone, queryset)
        if droid.stopTrackingPhoneState().error:
            messages.error(request, 'Error stopping tracking phone state')

    def send_sms(modeladmin, request, queryset):
        if not request.POST.get('post'):
            return TemplateResponse(request, 'jadro_contacts/send_sms.html', {
                    'contacts': queryset, 'form': SendSmsForm(initial={
                            'action': 'send_sms',
                            '_selected_action': request.POST.getlist('_selected_action')})})
        message_template = SendSmsForm(request.POST).data['message']
        def _send_sms(contact):
            message = Template(message_template).render(Context({'contact': contact}))
            phones = contact.phones.filter_type(['mobile'])
            phone = phones and "%s" % phones[0]
            if phone:
                result = droid.smsSend(phone, message)
                if not result.error:
                    messages.info(request, 'SMS message sended to %(contact)s (%(phone)s).' % {
                            'contact': contact, 'phone': phone})
                else:
                    messages.error(request, 'Error sending SMS message to %(contact)s (%(phone)s).' % {
                            'contact': contact, 'phone': phone})
            else:
                messages.error(request, 'Error sending SMS message to %(contact)s: no mobile phone.' % {
                        'contact': contact})
        map(_send_sms, queryset)

    def get_actions(self, request):
        actions = super(RawContactAdmin, self).get_actions(request)
        return dict([(k,v) for k,v in actions.items() if k in self.actions])

class CallAdmin(ContactAdmin):
    fields = ['number', 'name', 'date', 'duration', 'data_type', 'acknowledged']
    list_display = fields
    search_fields = ['number', 'name']
    list_filter = ['data_type', 'acknowledged','date']
    actions = None

admin.site.register(RawContact, RawContactAdmin)
admin.site.register(Call, CallAdmin)
