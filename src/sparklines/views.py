from collections import defaultdict
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView


def get_objects(request, app_label, model):
    model_type = ContentType.objects.get(app_label=app_label, model=model)
    Model = model_type.model_class()
    return Model.objects.all()


def count_tsv(request, app_label, model):
    objects = get_objects(request, app_label, model)
    created_field = request.GET.get('createdfield', None)

    cumulative = list()

    if created_field:
        count = 0
        for instance in objects.order_by(created_field):
            count += 1
            dt = getattr(instance, created_field)
            cumulative.append((dt, count))

    return HttpResponse('date\tclose\n' + '\n'.join(['\t'.join([dt.strftime('%Y-%m-%dT%H:%m:%S'), str(count)]) for (dt, count) in cumulative]),
        content_type='text/tab-separated-values',
        status=200)


class CountView (TemplateView):
    template_name = 'admin/count.html'

    def get_context_data(self, **kwargs):
        context = super(CountView, self).get_context_data(**kwargs)
        context['app_label'] = app_label = self.kwargs['app_label']
        context['model'] = model = self.kwargs['model']
        context['objects'] = get_objects(self.request, app_label, model)

        context['created_field'] = self.request.GET.get('createdfield', None)
        return context

    def get(self, request, app_label, model):
        return super(CountView, self).get(request, app_label, model)


count_view = CountView.as_view()