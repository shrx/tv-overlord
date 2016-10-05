import sys
import requests
import textwrap
import click
from tvoverlord.tvutil import format_paragraphs
from tvoverlord.config import Config
from tvoverlord.db import DB


class Location:
    """Compare our current ip with the ip supplied from our ISP

    If the ip address stored in the config.ini matches the ip address
    found via ipify then we are not connected through a vpn.

    Location uses ipify.org to get our real ip.  The first 3 octets
    are compared since the last octet is regularly changed by the ISP.
    """

    def __init__(self):
        url = 'http://api.ipify.org'
        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError:
            sys.exit('\nIP identification services are unavailable: {}'.format(
                url))
        self.ip = r.text
        self.db = DB
        self.whitelist = 'ip_whitelist'
        self.ips = self.get_ips()

    def get_ips(self):
        ips = self.db.get_config(self.whitelist)
        if ips:
            return ips
        else:
            return []

    def add_ip(self):
        ips = set(self.ips)
        ips.add(self.ip)
        ips = list(ips)
        self.db.set_config(self.whitelist, ips)

    def ips_match(self, parts_to_match=4):
        """If the current ip matches one of the white listed ones.

        If they match, that means we are connected via a VPN.
        """
        if parts_to_match not in [1, 2, 3, 4]:
            sys.exit('parts_to_match not between 1 and 4')

        ip = self.ip
        part_ip = ip.split('.')
        part_ip = '.'.join(part_ip[:parts_to_match])

        for ip in self.ips:
            if ip.startswith(part_ip):
                return True
        return False

    def message(self):
        ips = ', '.join(self.ips)
        warning = click.style('Warning:', bg='red', fg='white', bold=True)
        msg = """
          {warning} not connected to a VPN

          Your current public ip ({ip}) is not in the good ip list.
          Would you like this ip added to the whitelist? [y/n]""".format(
              warning=warning, ip=self.ip)

        msg = format_paragraphs(msg)
        click.echo()
        click.echo(msg, nl=False)
        c = click.getchar()
        click.echo()
        if c == 'y':
            self.add_ip()
            return True
        return False


if __name__ == '__main__':
    from config import Config
    l = Location(parts_to_match=3)
    print('config ip:', Config.ip)
    print('my real ip:  ', l.ip)
    print('match?', l.ips_match(Config.ip))
