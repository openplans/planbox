import json
import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


@login_required
def create_dataset(request):
    """
    Create a dataset under the account specified in the settings with the
    name provided in the 'dataset_slug' query parameter.
    """
    # We should only be allowed to POST to this view.
    if request.method.upper() != 'POST':
        return HttpResponse('Method not allowed', status=405)

    # Do some simple validation on the slug. We don't allow empty slugs.
    slug = request.POST.get('dataset_slug', '')
    if len(slug) == 0:
        return HttpResponse(
            json.dumps({'errors': [{'dataset_slug': 'This field is required.'}]}),
            content_type='application/json',
            status=400)

    current_origin = request.META.get('HTTP_ORIGIN', '')
    datasets_url = 'http://%s/api/v2/%s/datasets' % (
        settings.SHAREABOUTS_HOST,
        settings.SHAREABOUTS_USERNAME)
    dataset_url = '/'.join([datasets_url, slug])
    origins_url = '/'.join([dataset_url, 'origins'])
    planbox_auth = HTTPBasicAuth(
        settings.SHAREABOUTS_USERNAME,
        settings.SHAREABOUTS_PASSWORD)

    # Try to retrieve the dataset.
    ds_response = requests.get(dataset_url, auth=planbox_auth)

    if ds_response.status_code == 200:
        if current_origin:
            # Check whether the dataset  can write to the dataset from this origin.
            # TODO: Retry request if not 200
            origins_response = requests.get(origins_url, auth=planbox_auth)
            patterns = [origin['pattern'] for origin in origins_response.json()['results']]

            # If not, then register this
            if current_origin not in patterns:
                requests.post(origins_url,
                    data=json.dumps({'pattern': current_origin}),
                    headers={'Content-type': 'application/json'},
                    auth=planbox_auth)

        return HttpResponse(
            json.dumps({'url': ds_response.json()['url']}),
            content_type='application/json')

    elif ds_response.status_code != 404:
        return HttpResponse(
            json.dumps({'errors': 'Upstream problem.'}),
            status=503,
            content_type='application/json')

    # If the dataset did not exist, create it.
    ds_response = requests.post(datasets_url,
        data=json.dumps({'slug': slug, 'display_name': slug}),
        headers={'Content-type': 'application/json'},
        auth=planbox_auth)

    # Check whether we can write to the dataset from this origin.
    if current_origin:
        requests.post(origins_url,
            data=json.dumps({'pattern': current_origin}),
            headers={'Content-type': 'application/json'},
            auth=planbox_auth)

    if ds_response.status_code == 201:
        return HttpResponse(
            json.dumps({'url': ds_response.json()['url']}),
            content_type='application/json')

    elif ds_response.status_code < 500:
        return HttpResponse(ds_response.content,
            status=ds_response.status_code,
            content_type='application/json')

    else:
        return HttpResponse(json.dumps({'errors': 'Upstream problem.'}),
            status=503,
            content_type='application/json')
