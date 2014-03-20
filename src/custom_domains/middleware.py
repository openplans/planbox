from django.conf import settings
from django.http import Http404
from custom_domains.models import DomainMapping, DefaultDomainMapping


class CustomDomainResolvingMiddleware(object):
    def process_request(self, request):
        # Get the domain. If it's one of our explicitly known domains, then
        # proceed as normal.
        domain = request.META['HTTP_HOST']
        if domain in settings.KNOWN_HOSTS:
            request.domain_mapping = DefaultDomainMapping(domain)
            request.actual_path_info = request.path_info
            return

        # If the domain is implicit, check that it's valid.
        try:
            mapping = DomainMapping.objects.get(domain=domain)
        except DomainMapping.DoesNotExist:
            raise Http404

        # Finally, stick the valid mapping on the request, and reassign the
        # path_info attribute.
        request.domain_mapping = mapping
        request.actual_path_info = request.path_info
        request.path_info = '/'.join([
            mapping.root_path.rstrip('/'),
            request.actual_path_info.lstrip('/')
        ])
        return
