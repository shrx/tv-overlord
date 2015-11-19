"""

"""
import requests

class Location:
    def __init__(self):
        url = 'http://api.ipify.org'
        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError:
            print('\nIP identification services are unavailable - http://api.ipify.org')
            exit()

        self.ip = str(r.content)

    def ips_match(self, ip):
        match = False
        part_ip = ip.split('.')
        part_ip = '%s.%s' % (part_ip[0], part_ip[1])
        if self.ip.startswith(part_ip):
            match = True

        return match
