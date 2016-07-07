import sys
import requests
import textwrap
import click
from tvoverlord.tvutil import format_paragraphs
from tvoverlord.config import Config


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

    def ips_match(self, ips):
        """If the current ip matches one of the white listed ones.

        If they match, that means we are connected via a VPN.
        """
        self.ips = ips
        for ip in ips:
            if not ip:
                raise Exception('IP address cannot be empty')
            part_ip = ip.split('.')
            part_ip = '.'.join(part_ip[:2])
            if self.ip.startswith(part_ip):
                return True

        return False

    def message(self):
        ips = ', '.join(self.ips)
        warning = click.style('Warning:', bg='red', fg='white', bold=True)
        msg = """
          {warning} not connected to a VPN

          The ip addresses in config.ini ({config_ips}) don't match
          your current ip address which is {current_ip}.

          If you know you are connected to a VPN, add your current ip to the
          config.ini file otherwise don't add it.

          Would you like me to open config.ini in your default editor
          so you can add {current_ip}? [y/n]""".format(
              config_ips=ips, current_ip=self.ip, warning=warning)

        msg = format_paragraphs(msg)
        click.echo(msg)
        c = click.getchar()
        click.echo()
        if c == 'y':
            click.edit(filename=Config.user_config)
        else:
            click.echo('Config is here: %s' % Config.user_config)


if __name__ == '__main__':
    from config import Config
    l = Location()
    click.echo('config ip:', Config.ip)
    click.echo('my config ip:', Config.ip)
    click.echo('my real ip:  ', l.ip)
    click.echo('match?', l.ips_match(Config.ip))
