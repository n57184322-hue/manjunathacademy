import os
import re
import shutil

from django.conf import settings
from django.db import connection
from django.utils import timezone

from . import dropbox_utils
from .dropbox_utils import DropboxError

MEDIA_BACKUP_ROOT = '/Manjunath Academy/Media'
DB_BACKUP_ROOT = '/db-backups'
DB_HISTORY_FOLDER = f'{DB_BACKUP_ROOT}/history'
DB_LATEST_PATH = f'{DB_BACKUP_ROOT}/db_latest.sqlite3'

BACKUP_NAME_RE = re.compile(r'^db_(\d{8})_(\d{6})\.sqlite3$')


def _sqlite_path():
    if connection.vendor != 'sqlite':
        return None
    db_path = connection.settings_dict.get('NAME')
    if db_path and os.path.isfile(db_path):
        return str(db_path)
    return None


def run_full_backup(dropbox_settings):
    """Uploads every file under MEDIA_ROOT plus a timestamped copy of the SQLite database to Dropbox."""
    if not dropbox_utils.is_configured():
        return False, 'Dropbox is not configured.'

    uploaded = 0
    errors = []

    media_root = settings.MEDIA_ROOT
    if os.path.isdir(media_root):
        for root, _dirs, files in os.walk(media_root):
            for filename in files:
                local_path = os.path.join(root, filename)
                rel_path = os.path.relpath(local_path, media_root).replace(os.sep, '/')
                dropbox_path = f'{MEDIA_BACKUP_ROOT}/{rel_path}'
                try:
                    dropbox_utils.upload_file(dropbox_path, local_path)
                    uploaded += 1
                except DropboxError as exc:
                    errors.append(str(exc))

    db_backed_up = False
    db_path = _sqlite_path()
    if db_path:
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        try:
            dropbox_utils.upload_file(f'{DB_HISTORY_FOLDER}/db_{timestamp}.sqlite3', db_path)
            dropbox_utils.upload_file(DB_LATEST_PATH, db_path)
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


def list_db_backups():
    """Returns database backups from /db-backups/history, newest first, as
    [{'filename', 'date', 'time'}, ...] parsed from the db_YYYYMMDD_HHMMSS.sqlite3 naming."""
    entries = dropbox_utils.list_folder(DB_HISTORY_FOLDER)
    backups = []
    for entry in entries:
        match = BACKUP_NAME_RE.match(entry['name'])
        if not match:
            continue
        date_part, time_part = match.groups()
        backups.append({
            'filename': entry['name'],
            'date': f'{date_part[0:4]}-{date_part[4:6]}-{date_part[6:8]}',
            'time': f'{time_part[0:2]}:{time_part[2:4]}:{time_part[4:6]}',
        })
    backups.sort(key=lambda b: b['filename'], reverse=True)
    return backups


def restore_database(dropbox_settings, filename=None):
    """Downloads a database backup from Dropbox and restores it, keeping a safety copy of the current file.

    Defaults to the latest backup when `filename` isn't given.
    """
    if not dropbox_utils.is_configured():
        return False, 'Dropbox is not configured.'
    if connection.vendor != 'sqlite':
        return False, 'Restore is only supported when the site is using a SQLite database.'

    dropbox_path = f'{DB_HISTORY_FOLDER}/{filename}' if filename else DB_LATEST_PATH

    db_path = connection.settings_dict.get('NAME')
    tmp_path = f'{db_path}.restore_tmp'

    try:
        dropbox_utils.download_file(dropbox_path, tmp_path)
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
    return True, f'Database restored from {filename or "the latest backup"}. Your previous database was saved as {os.path.basename(safety_path)}. Restart the app for the change to fully take effect.'


def restore_media():
    """Downloads every file under /Manjunath Academy/Media back into MEDIA_ROOT, overwriting local copies."""
    if not dropbox_utils.is_configured():
        return False, 'Dropbox is not configured.'

    try:
        entries = dropbox_utils.list_folder(MEDIA_BACKUP_ROOT, recursive=True)
    except DropboxError as exc:
        return False, str(exc)

    if not entries:
        return False, 'No media backup found on Dropbox yet.'

    media_root = settings.MEDIA_ROOT
    prefix = MEDIA_BACKUP_ROOT.lower() + '/'
    restored = 0
    errors = []
    for entry in entries:
        path_lower = entry['path_display'].lower()
        if not path_lower.startswith(prefix):
            continue
        rel_path = entry['path_display'][len(MEDIA_BACKUP_ROOT) + 1:]
        local_path = os.path.join(media_root, *rel_path.split('/'))
        try:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            dropbox_utils.download_file(entry['path_display'], local_path)
            restored += 1
        except DropboxError as exc:
            errors.append(str(exc))

    if errors:
        return False, f'{restored} file(s) restored, {len(errors)} error(s).'
    return True, f'{restored} media file(s) restored from Dropbox.'


def delete_all_backups():
    """Permanently deletes every database backup (history + latest) from Dropbox. Does not touch media."""
    if not dropbox_utils.is_configured():
        return False, 'Dropbox is not configured.'
    try:
        dropbox_utils.delete_path(DB_BACKUP_ROOT)
    except DropboxError as exc:
        return False, str(exc)
    return True, 'All database backups have been deleted from Dropbox.'


def restore_everything(dropbox_settings, filename=None):
    """Restores the database (latest or a specific backup) and every media file, in one action."""
    db_ok, db_detail = restore_database(dropbox_settings, filename=filename)
    media_ok, media_detail = restore_media()
    ok = db_ok and media_ok
    detail = f'Database: {db_detail} | Media: {media_detail}'
    return ok, detail
