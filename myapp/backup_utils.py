import os
import shutil

from django.conf import settings
from django.db import connection
from django.utils import timezone

from .dropbox_utils import DropboxError, download_file, upload_file

BACKUP_ROOT = '/Manjunath Academy'


def _sqlite_path():
    if connection.vendor != 'sqlite':
        return None
    db_path = connection.settings_dict.get('NAME')
    if db_path and os.path.isfile(db_path):
        return str(db_path)
    return None


def run_full_backup(dropbox_settings):
    """Uploads every file under MEDIA_ROOT plus the SQLite database (if used) to Dropbox."""
    if not dropbox_settings or not dropbox_settings.is_configured:
        return False, 'Dropbox is not configured.'

    token = dropbox_settings.access_token
    uploaded = 0
    errors = []

    media_root = settings.MEDIA_ROOT
    if os.path.isdir(media_root):
        for root, _dirs, files in os.walk(media_root):
            for filename in files:
                local_path = os.path.join(root, filename)
                rel_path = os.path.relpath(local_path, media_root).replace(os.sep, '/')
                dropbox_path = f'{BACKUP_ROOT}/Media/{rel_path}'
                try:
                    upload_file(token, dropbox_path, local_path)
                    uploaded += 1
                except DropboxError as exc:
                    errors.append(str(exc))

    db_backed_up = False
    db_path = _sqlite_path()
    if db_path:
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        try:
            upload_file(token, f'{BACKUP_ROOT}/Database/db_{timestamp}.sqlite3', db_path)
            upload_file(token, f'{BACKUP_ROOT}/Database/db_latest.sqlite3', db_path)
            db_backed_up = True
        except DropboxError as exc:
            errors.append(str(exc))

    dropbox_settings.last_backup_at = timezone.now()
    if errors:
        dropbox_settings.last_backup_status = (
            f'{uploaded} file(s) uploaded, {len(errors)} error(s). Database backed up: {"yes" if db_backed_up else "no"}.'
        )
    else:
        dropbox_settings.last_backup_status = (
            f'{uploaded} file(s) uploaded successfully. Database backed up: {"yes" if db_backed_up else "no"}.'
        )
    dropbox_settings.save(update_fields=['last_backup_at', 'last_backup_status'])

    return (not errors), dropbox_settings.last_backup_status


def restore_database(dropbox_settings):
    """Downloads the latest database backup from Dropbox and restores it, keeping a safety copy of the current file."""
    if not dropbox_settings or not dropbox_settings.is_configured:
        return False, 'Dropbox is not configured.'
    if connection.vendor != 'sqlite':
        return False, 'Restore is only supported when the site is using a SQLite database.'

    db_path = connection.settings_dict.get('NAME')
    tmp_path = f'{db_path}.restore_tmp'

    try:
        download_file(dropbox_settings.access_token, f'{BACKUP_ROOT}/Database/db_latest.sqlite3', tmp_path)
    except DropboxError as exc:
        return False, str(exc)

    with open(tmp_path, 'rb') as f:
        header = f.read(16)
    if header != b'SQLite format 3\x00':
        os.remove(tmp_path)
        return False, 'The downloaded file is not a valid SQLite database — restore aborted.'

    safety_path = f'{db_path}.before_restore_{timezone.now().strftime("%Y%m%d_%H%M%S")}'
    if os.path.isfile(db_path):
        shutil.copy2(db_path, safety_path)

    shutil.move(tmp_path, db_path)
    return True, f'Database restored from Dropbox. Your previous database was saved as {os.path.basename(safety_path)}. Restart the app for the change to fully take effect.'
