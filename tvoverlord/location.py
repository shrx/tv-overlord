import sys
import requests


class Location:
    """Compare our current ip with the ip supplied from our ISP

    Location uses ipify.org to get our real ip.  The first 3 octets
    are compared since the last octet is regularaly changed by the ISP.

    """

    def __init__(self):
        url = 'http://api.ipify.org'
        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError:
            sys.exit('\nIP identification services are unavailable: {}'.format(
                url))
        self.ip = r.text

    def ips_match(self, ip):
        part_ip = ip.split('.')
        part_ip = '.'.join(part_ip[:2])
        if self.ip.startswith(part_ip):
            return True
        else:
            return False
