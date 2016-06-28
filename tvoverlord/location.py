import sys
import requests


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
        for ip in ips:
            if not ip:
                raise Exception('IP address cannot be empty')
            part_ip = ip.split('.')
            part_ip = '.'.join(part_ip[:2])
            if self.ip.startswith(part_ip):
                return True

        return False


if __name__ == '__main__':
    from config import Config
    l = Location()
    print('config ip:', Config.ip)
    print('my config ip:', Config.ip)
    print('my real ip:  ', l.ip)
    print('match?', l.ips_match(Config.ip))
