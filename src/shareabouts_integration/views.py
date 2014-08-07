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
            content_type='application/json', status=400)

    datasets_url = 'https://%s/api/v2/%s/datasets' % (
        settings.SHAREABOUTS_HOST,
        settings.SHAREABOUTS_USERNAME)
    dataset_url = '/'.join([datasets_url, slug])
    planbox_auth = HTTPBasicAuth(
        settings.SHAREABOUTS_USERNAME,
        settings.SHAREABOUTS_PASSWORD)

    # Try to retrieve the dataset.
    ds_response = requests.get(dataset_url, auth=planbox_auth)

    # If the dataset exists already; nothing to do, since we assume that a
    # CORS permission profile is already created.
    if ds_response.status_code == 200:
        return HttpResponse(
            json.dumps({'url': ds_response.json()['url']}),
            content_type='application/json')

    # If the dataset was not reported as existing but we didn't get a 404 back
    # then we have some error response and should send a 502 down.
    elif ds_response.status_code != 404:
        return HttpResponse(
            json.dumps({'errors': 'Unknown upstream problem.'}),
            status=502,
            content_type='application/json')

    # If the dataset did not exist, create it.
    ds_response = requests.post(datasets_url,
        data=json.dumps({'slug': slug, 'display_name': slug}),
        headers={'Content-type': 'application/json'},
        auth=planbox_auth)

    # Check that we were successful in creating the dataset.
    if ds_response.status_code == 201:
        return HttpResponse(
            json.dumps({'url': ds_response.json()['url']}),
            content_type='application/json')

    elif ds_response.status_code < 500:
        return HttpResponse(ds_response.content,
            status=ds_response.status_code,
            content_type='application/json')

    else:
        return HttpResponse(json.dumps({'errors': 'Unknown upstream problem.'}),
            status=502,
            content_type='application/json')
