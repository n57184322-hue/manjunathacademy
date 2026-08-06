import json
import urllib.error
import urllib.request

UPLOAD_URL = 'https://content.dropboxapi.com/2/files/upload'
DOWNLOAD_URL = 'https://content.dropboxapi.com/2/files/download'
ACCOUNT_URL = 'https://api.dropboxapi.com/2/users/get_current_account'


class DropboxError(Exception):
    pass


def _http_error_detail(exc):
    try:
        return exc.read().decode('utf-8', errors='ignore')
    except Exception:
        return str(exc)


def test_connection(access_token):
    req = urllib.request.Request(
        ACCOUNT_URL,
        data=b'null',
        headers={'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        raise DropboxError(f'Could not connect to Dropbox: {_http_error_detail(exc)}')
    except Exception as exc:
        raise DropboxError(f'Could not connect to Dropbox: {exc}')


def upload_file(access_token, dropbox_path, local_path):
    with open(local_path, 'rb') as f:
        data = f.read()
    api_arg = json.dumps({'path': dropbox_path, 'mode': 'overwrite', 'autorename': False, 'mute': True})
    req = urllib.request.Request(
        UPLOAD_URL,
        data=data,
        headers={
            'Authorization': f'Bearer {access_token}',
            'Dropbox-API-Arg': api_arg,
            'Content-Type': 'application/octet-stream',
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        raise DropboxError(f'Upload failed for {dropbox_path}: {_http_error_detail(exc)}')


def download_file(access_token, dropbox_path, local_path):
    api_arg = json.dumps({'path': dropbox_path})
    req = urllib.request.Request(
        DOWNLOAD_URL,
        data=b'',
        headers={'Authorization': f'Bearer {access_token}', 'Dropbox-API-Arg': api_arg},
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            content = resp.read()
    except urllib.error.HTTPError as exc:
        raise DropboxError(f'Download failed for {dropbox_path}: {_http_error_detail(exc)}')
    with open(local_path, 'wb') as f:
        f.write(content)
