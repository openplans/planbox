import base64
import urlparse


def get_auth_header(client_id, client_secret, username, email=None):
    """
    Get the value of the Authorization header for the OAuth session.
    """
    auth_data = ';'.join([client_id, client_secret, username, email or ''])
    encoded_auth_data = base64.b64encode(auth_data).strip()
    return 'Remote ' + encoded_auth_data


def get_authorization_code(session, host, client_id, auth_header):
    # Call .../authorize to start the process of getting an authorization token.
    # The session started here will be continued in the which will be stored in a
    # next call.
    response = session.post(host + '/api/v2/users/oauth2/authorize',
        data={
            'response_type': 'code',
            'client_id': client_id
        },
        headers={
            'Authorization': auth_header,
            'X-CSRFToken': 'dummycsrftoken',
            'Referer': host
        },
        cookies={
            'csrftoken': 'dummycsrftoken'
        })

    assert response.status_code == 200, 'Failure response from [Shareabouts API]/users/oauth2/authorize: (%s) "%s"' % (response.status_code, response.text)

    # Call .../authorize/confirm with the session from above to retrieve an
    # authorization token.
    response = session.post(host + '/api/v2/users/oauth2/authorize/confirm',
        data={
            'scope': 'read',
            'authorize': 'Authorize'
        },
        headers={'X-CSRFToken': 'dummycsrftoken', 'Referer': host + '/api/v2/users/oauth2/authorize'},
        cookies={'csrftoken': 'dummycsrftoken'})

    assert response.status_code == 200, 'Failure response from [Shareabouts API]/users/oauth2/authorize/confirm: (%s) "%s"' % (response.status_code, response.text)

    # Parse the authorization token out of the resultant URL
    url = response.url
    parts = urlparse.urlparse(url)
    query = urlparse.parse_qs(parts.query)

    assert 'error' not in query, 'Error from [Shareabouts API]/users/oauth2/authorize/confirm: ' + query['error']
    assert 'code' in query, 'No authorization code found in response from [Shareabouts API]/users/oauth2/authorize/confirm'
    assert len(query['code']) >= 1, 'Invalid Authorization code parsed from [Shareabouts API]/users/oauth2/authorize/confirm'

    return query['code'][0]


def get_credentials(session, host, authorization_code, client_id, client_secret):
    # Finally, call .../access_token to get a prize.
    response = session.post(host + '/api/v2/users/oauth2/access_token',
        data={
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'client_id': client_id,
            'client_secret': client_secret
        },
        headers={'X-CSRFToken': 'dummycsrftoken', 'Referer': host + '/api/v2/users/oauth2/authorize/confirm'},
        cookies={'csrftoken': 'dummycsrftoken'})

    assert response.status_code == 200, 'Failure response from [Shareabouts API]/users/oauth2/access_token: (%s) "%s"' % (response.status_code, response.text)

    return response.json()
