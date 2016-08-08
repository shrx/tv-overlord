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

    def ips_match(self, ips, parts_to_match=4):
        """If the current ip matches one of the white listed ones.

        If they match, that means we are connected via a VPN.
        """
        if parts_to_match not in [1, 2, 3, 4]:
            sys.exit('parts_to_match not between 1 and 4')

        self.ips = ips
        for ip in ips:
            if not ip:
                raise Exception('IP address cannot be empty')
            part_ip = ip.split('.')
            part_ip = '.'.join(part_ip[:parts_to_match])
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

    def getipintel(self):
        """http://getipintel.net/"""
        contact_email = Config.email

        # if probability from getIPIntel is greater than this value, return 1
        max_probability = 0.99
        timeout = 5.00

        # if you wish to use flags or json format, edit the request below
        url = "http://check.getipintel.net/check.php?ip={}&contact={}"
        url = url.format(self.ip, contact_email)
        result = requests.get(url, timeout=timeout)

        if (result.status_code != 200) or (int(result.content) < 0):
            click.echo('An error occured while querying GetIPIntel')
            click.echo('status code: %s' % result.status_code)
            click.echo('contents:    %s' % result.content)
            click.echo('current ip:  %s' % self.ip)

        if (float(result.content) > max_probability):
            return True  # is VPN
        else:
            return False  # not VPN


if __name__ == '__main__':
    from config import Config
    l = Location(parts_to_match=3)
    print('config ip:', Config.ip)
    print('my real ip:  ', l.ip)
    print('match?', l.ips_match(Config.ip))
