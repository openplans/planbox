import json
import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from shareabouts_integration.oauth_dance import get_auth_header, get_authorization_code, get_credentials


@login_required
def oauth_credentials(request):
    """
    How do we correlate Planbox and Shareabouts users? Username is faulty but
    easy. With normal OAuth we wouldn't have this issue because the user would
    specify their own account.

    But for now, there's only one user to support.
    """
    host = 'https://' + settings.SHAREABOUTS_HOST
    client_id = settings.SHAREABOUTS_CLIENT_ID
    client_secret = settings.SHAREABOUTS_CLIENT_SECRET
    username = settings.SHAREABOUTS_USERNAME

    session = requests.session()

    auth_header = get_auth_header(client_id, client_secret, username)
    authorization_code = get_authorization_code(session, host, auth_header)
    credentials = get_credentials(session, host, authorization_code, client_id, client_secret)

    return HttpResponse(json.dumps(credentials, indent=2, sort_keys=True),
        status=200,
        content_type='application/json')

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
