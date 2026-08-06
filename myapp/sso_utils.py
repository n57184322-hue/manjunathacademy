import json
import urllib.parse
import urllib.request

GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'

FACEBOOK_AUTH_URL = 'https://www.facebook.com/v18.0/dialog/oauth'
FACEBOOK_TOKEN_URL = 'https://graph.facebook.com/v18.0/oauth/access_token'
FACEBOOK_USERINFO_URL = 'https://graph.facebook.com/me'


class SSOError(Exception):
    pass


def _http_get(url, params=None):
    if params:
        url = f'{url}?{urllib.parse.urlencode(params)}'
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read().decode('utf-8'))


def _http_post(url, data):
    body = urllib.parse.urlencode(data).encode('utf-8')
    req = urllib.request.Request(url, data=body, method='POST')
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode('utf-8'))


def google_auth_url(settings_obj, redirect_uri, state):
    params = {
        'client_id': settings_obj.google_client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
        'prompt': 'select_account',
    }
    return f'{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}'


def google_fetch_profile(settings_obj, redirect_uri, code):
    try:
        token_data = _http_post(GOOGLE_TOKEN_URL, {
            'code': code,
            'client_id': settings_obj.google_client_id,
            'client_secret': settings_obj.google_client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        })
        access_token = token_data['access_token']
        profile = _http_get(GOOGLE_USERINFO_URL, {'access_token': access_token})
        if not profile.get('email'):
            raise SSOError('Google did not return an email address.')
        return {'email': profile['email'], 'name': profile.get('name') or profile['email'].split('@')[0]}
    except SSOError:
        raise
    except Exception as exc:
        raise SSOError(f'Google sign-in failed: {exc}')


def facebook_auth_url(settings_obj, redirect_uri, state):
    params = {
        'client_id': settings_obj.facebook_app_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'email,public_profile',
        'state': state,
    }
    return f'{FACEBOOK_AUTH_URL}?{urllib.parse.urlencode(params)}'


def facebook_fetch_profile(settings_obj, redirect_uri, code):
    try:
        token_data = _http_get(FACEBOOK_TOKEN_URL, {
            'code': code,
            'client_id': settings_obj.facebook_app_id,
            'client_secret': settings_obj.facebook_app_secret,
            'redirect_uri': redirect_uri,
        })
        access_token = token_data['access_token']
        profile = _http_get(FACEBOOK_USERINFO_URL, {'fields': 'id,name,email', 'access_token': access_token})
        if not profile.get('email'):
            raise SSOError('Facebook did not return an email address for this account. Try Google or email signup instead.')
        return {'email': profile['email'], 'name': profile.get('name') or profile['email'].split('@')[0]}
    except SSOError:
        raise
    except Exception as exc:
        raise SSOError(f'Facebook sign-in failed: {exc}')
