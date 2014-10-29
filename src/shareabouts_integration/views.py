import json
import re
import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.core.signing import Signer
from planbox_data.models import Project
from shareabouts_integration.models import Preauthorization
from shareabouts_integration.oauth_dance import get_auth_header, get_authorization_code, get_credentials

from raven.contrib.django.models import client


def bad_request(errors):
    return HttpResponse(json.dumps(errors), status=400, content_type='application/json')


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

    # Make sure a project ID is specified
    project_id = request.GET.get('project_id')
    try:
        project = Project.objects.all().get(pk=project_id)
    except Project.DoesNotExist:
        return bad_request([{'project_id': 'Project does not exist.'}])

    # Make sure the user has edit permission on the project.
    if not project.editable_by(request.user):
        return HttpResponse('Unauthorized', status=401)

    # Get the preauthorization object for the project.
    try:
        auth = Preauthorization.objects.get(project=project)
    except Preauthorization.DoesNotExist:
        raise Http404
    username = auth.username

    # Get the requested credentials from the Shareabouts API server
    session = requests.session()
    try:
        auth_header = get_auth_header(client_id, client_secret, username)
        authorization_code = get_authorization_code(session, host, client_id, auth_header)
        credentials = get_credentials(session, host, authorization_code, client_id, client_secret)
    except AssertionError:
        if settings.DEBUG: raise
        client.captureException()
        return HttpResponse('Upstream error occurred.',
            status=502,
            content_type='text/plain')

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
        # Return the dataset URL as well as a signature that we'll use later
        # when we authorize the user to access the Shareabouts API as the
        # dataset's owner.
        signer = Signer(salt='shareabouts')
        ds_url = ds_response.json()['url']
        return HttpResponse(
            json.dumps({
                'dataset_url': ds_url,
                'signature': signer.sign(ds_url)
            }),
            content_type='application/json')

    elif ds_response.status_code < 500:
        return HttpResponse(ds_response.content,
            status=ds_response.status_code,
            content_type='application/json')

    else:
        return HttpResponse(json.dumps({'errors': 'Unknown upstream problem.'}),
            status=502,
            content_type='application/json')


@login_required
def authorize_project(request):
    # We should only be allowed to POST to this view.
    if request.method.upper() != 'POST':
        return HttpResponse('Method not allowed', status=405)

    dataset_url = request.POST.get('dataset_url', '')
    signature = request.POST.get('signature', '')
    project_id = request.POST.get('project_id', '')

    # Make sure all fields are present.
    errors = []
    if not dataset_url: errors.append({'dataset_url': 'This field is required.'})
    if not signature: errors.append({'signature': 'This field is required.'})
    if not project_id: errors.append({'project_id': 'This field is required.'})
    if errors:
        return bad_request(errors)

    # Make sure the signature is valid.
    signer = Signer(salt='shareabouts')
    if signature != signer.sign(dataset_url):
        return bad_request([{'signature': 'Invalid signature.'}])

    # Parse out the owner username.
    owner_pattern = '^https://%s/api/v2/([^/]+)/datasets' % (settings.SHAREABOUTS_HOST,)
    match = re.match(owner_pattern, dataset_url)
    if not match:
        return bad_request([{'dataset_url': 'Could not find username.'}])
    owner_username = match.group(1)

    # Query for the project object.
    try:
        project = Project.objects.all().get(pk=project_id)
    except Project.DoesNotExist:
        return bad_request([{'project_id': 'Project does not exist.'}])

    # Make sure the user has edit permission.
    if not project.editable_by(request.user):
        return HttpResponse('Unauthorized', status=401)

    # Ensure that a preauthorization for the project exists.
    auth, _ = Preauthorization.objects.get_or_create(project=project)
    auth.username = owner_username
    auth.save()

    return HttpResponse('', status=204)