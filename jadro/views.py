from django.views.generic import TemplateView, ListView

class IndexView(TemplateView):
    template_name = 'jadro/index.html'
    urls = []

    def get_context_data(self, **kwargs):
        return {'urls': self.urls}
