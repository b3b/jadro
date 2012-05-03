import re
from django import forms
from django.middleware import csrf
from django.utils import simplejson as json
from django.http import HttpResponse
from django.views.generic import FormView
from django.views.generic.edit import BaseFormView
from jadro_droid import DummyDroid

class APIForm(forms.Form):
    parameter_js_class = 'par'
    method = forms.CharField()
    method_parameter = forms.CharField(widget=forms.HiddenInput(
            attrs={'class': parameter_js_class}), required=False)

    def __init__(self, *args, **kwargs):
        super(APIForm, self).__init__(*args, **kwargs)
        parameters = self.method_parameters(kwargs.get('data', kwargs['initial']))
        for parameter in parameters:
            self.fields[parameter] = forms.CharField(widget=forms.TextInput(
                    attrs={'class': self.parameter_js_class}), required=False)

    def method_parameters(self, data):
        return sorted(filter(lambda x: re.match(
                    ''.join((self.parameter_js_class, '\d+')), x),
                             data.keys()))

class API(object):
    droid = DummyDroid()
    form_class = APIForm

    def get_initial(self):
        initial = {}
        droid_method = self.kwargs.get('method', None)
        if droid_method:
            initial['method'] = droid_method
        initial.update(self.request.GET.dict())
        return initial

    def form_valid(self, form):
        data = form.cleaned_data
        if 'method' in data:
            parameters = [data[p] for p in form.method_parameters(data)]
            method = getattr(self.droid, data['method'])
            result = method(*parameters)
        else:
            result = None
        return self.render_to_response(self.get_context_data(form=form,
                                                             result=result))

class APIHandler(API, BaseFormView):

    def get_context_data(self, **kwargs):
        return {
            'csrfmiddlewaretoken': csrf.get_token(self.request),
            'result': kwargs.pop('result', None)
            }

    def render_to_response(self, context):
        return HttpResponse(json.dumps(context), mimetype='application/json')

class APIFormView(API, FormView):
    template_name = 'jadro_droid/api_form.html'
