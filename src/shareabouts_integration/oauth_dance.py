import requests
import base64
import urlparse

# Create a new session so that we save cookies as we redirect through the
# OAuth dance.
session = requests.session()


def get_auth_header(client_id, client_secret, username, email=None):
    """
    Get the value of the Authorization header for the OAuth session.
    """
    auth_data = ';'.join([client_id, client_secret, username, email or ''])
    encoded_auth_data = base64.b64encode(auth_data).strip()
    return 'Remote ' + encoded_auth_data


def get_authorization_code(session, host, auth_header):
    # Call .../authorize to start the process of getting an authorization token.
    # The session started here will be continued in the which will be stored in a
    # next call.
    response = session.post(host + '/api/v2/users/oauth2/authorize',
        data={
            'response_type': 'code',
            'client_id': 'd900f3ecc26100eeb852'
        },
        headers={
            'Authorization': auth_header,
            'X-CSRFToken': 'abc123',
            'Referer': host
        },
        cookies={
            'csrftoken': 'abc123'
        })

    assert response.status_code == 200

    # Call .../authorize/confirm with the session from above to retrieve an
    # authorization token.
    response = session.post(host + '/api/v2/users/oauth2/authorize/confirm',
        data={
            'scope': 'read',
            'authorize': 'Authorize'
        },
        headers={'X-CSRFToken': 'abc123', 'Referer': host + '/api/v2/users/oauth2/authorize'},
        cookies={'csrftoken': 'abc123'})

    assert response.status_code == 200, response.text

    # Parse the authorization token out of the resultant URL
    url = response.url
    parts = urlparse.urlparse(url)
    query = urlparse.parse_qs(parts.query)

    assert 'error' not in query, query['error']
    assert 'code' in query
    assert len(query['code']) >= 1

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
        headers={'X-CSRFToken': 'abc123', 'Referer': host + '/api/v2/users/oauth2/authorize/confirm'},
        cookies={'csrftoken': 'abc123'})

    assert response.status_code == 200

    return response.json()
