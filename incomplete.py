
from pprint import pprint as pp

from tv.tvconfig import Config
from tv.db import DB


def main():
    sql = '''SELECT show_title, chosen_hash FROM tracking WHERE complete is NULL'''
    db = DB()
    unfinished = db.run_sql(sql)

    debug_command = '''export TR_TORRENT_NAME='%s'; export TR_TORRENT_DIR='%s'; export TR_TORRENT_HASH='%s'; python ~/projects/media-downloader/src/transmission_done.py'''
    for show in unfinished:
        print
        print show[0]
        print '-' * len(show[0])
        command = debug_command % ('', '/home/sm/Shows', show[1])
        print command

if __name__ == '__main__':
    main()

