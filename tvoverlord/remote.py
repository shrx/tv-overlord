
import requests
import datetime
import json
import uuid
import click
import base64
from pprint import pprint as pp
from distutils.version import LooseVersion as LV
import platform
from tvoverlord.db import DB
from tvoverlord.config import Config
from tvoverlord.tvutil import format_paragraphs


class VersionCheck:
    def __init__(self, local_version):
        u = b'aHR0cHM6Ly90dm9sLTdjMTY1LmZpcmViYXNlaW8uY29tL21lc3NhZ2UuanNvbg=='
        self.u = base64.decodebytes(u).decode('ascii')
        self.message = None
        self.remote_version = None
        self.local_version = local_version

    def get_version(self, db):
        """Get the version data from the server

        This runs in a separate thread and instantiates its own db
        object because of that.
        """
        try:
            r = requests.get(self.u)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            # print(e)
            return False
        content = r.content.decode('ascii')
        j = json.loads(content)
        message = j['msg']
        remote_version = j['version']

        db.set_config('version_remote', remote_version)
        db.set_config('version_msg', message)

    def new_version(self):
        """
        compare current version with version in db
        """

        self.remote_version = DB.get_config('version_remote')
        self.message = DB.get_config('version_msg')

        if not self.remote_version:
            return False
        elif LV(self.local_version) < LV(self.remote_version):
            return True
        else:
            return False


class Telemetry:
    def ask(self):
        if not DB.get_config('telemetry_asked'):
            question = format_paragraphs("""
                May TV Overlord report anonymous usage statistics?

                This is the single most useful thing a user can do.  This
                data will help decide the features that get the most
                attention and the future direction of TV Overlord.

                More information at:

                https://github.com/8cylinder/tv-overlord/wiki/telemetry-data

            """)
            question = click.style(question, fg='green')
            click.echo()
            telemetry_ok = click.confirm(question, default=True)
            click.echo()

            DB.set_config('telemetry_ok', telemetry_ok)
            DB.set_config('telemetry_asked', True)
            if not DB.get_config('uuid4'):
                DB.set_config('uuid4', str(uuid.uuid4()))
                DB.set_config('uuid1', str(uuid.uuid1()))

    def have_permission(self, db):
        db_permission = db.get_config('telemetry_ok')
        if Config.telemetry_ok:
            permission = True
        elif Config.telemetry_ok is None and db_permission:
            permission = True
        else:
            permission = False
        return permission

    def send(self, db, version=None, cmd=None):
        now = datetime.datetime.now()
        data = {
            'timestamp': str(now),
            'command': cmd,
            'version': version,
            'uuid1': db.get_config('uuid1'),
            'uuid4': db.get_config('uuid4'),
            'showcount': db.get_show_count(),
            'searchtype': Config.search_type,
            'platform': platform.platform(),
            'python_version': platform.python_version(),
        }

        urltimestamp = datetime.datetime.isoformat(now)
        urltimestamp = urltimestamp.replace('.', '_')
        u = b'aHR0cHM6Ly90dm9sLTdjMTY1LmZpcmViYXNlaW8uY29tL3RlbGVtZXRyeS97fS5qc29u'
        u = base64.decodebytes(u).decode('ascii')
        u = u.format(urltimestamp)
        data = json.dumps(data)

        try:
            r = requests.put(u, data=data)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            # print(e)
            return False
        else:
            return True
