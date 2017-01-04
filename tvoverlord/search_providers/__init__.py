"""
A collection of search providers.  Can be anything that
returns a structured list of found items.

Currently there are two bittorent search providers
and two nzb search providers.
"""

# search providers not to use:
#
# torrentdownloads_me - to many seeds.
# nzbindex_com - rss feed not working.


# torrent search engings
from . import extratorrent
from . import bitsnoop
from . import thepiratebay_sx
from . import onethreethreesevenx_to
from . import rarbg_to
from . import eztv_ag
from . import btstorr_cc

# newsgroup search engines
from . import nzbclub_com
from . import nzb
# from . import nzbindex_com
