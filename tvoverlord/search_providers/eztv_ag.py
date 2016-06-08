import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import requests
from pprint import pprint as pp

import concurrent.futures
import socket


class Provider():

    name = 'eztv'
    shortname = 'EZ'
    url = ''
    base_url = 'https://eztv.ag/'

    def search(self, search_string, season=False, episode=False):

        if season and episode:
            searches = self.se_ep(search_string, season, episode)
        else:
            searches = [search_string]

        search_data = []
        for search in searches:
            search_tpl = '{}/search/{}'
            search = search.replace(' ', '-')
            search = urllib.parse.quote(search)
            url = search_tpl.format(self.base_url, search)
            print(url)
            try:
                r = requests.get(url)
            except requests.exceptions.ConnectionError:
                # can't connect, go to next url
                continue

            html = r.content
            soup = BeautifulSoup(html, 'html.parser')
            search_results = soup.find_all('tr', class_='forum_header_border')
            if search_results is None:
                continue

            for tr in search_results:

                tds = tr.find_all('td')

                title = tds[1].get_text(strip=True)
                if search_string.lower() not in title.lower():
                    continue

                detail_url = tds[1].a['href']

                magnet = tds[2].a['href']
                if not magnet.startswith('magnet'):
                    continue

                size = tds[3].get_text(strip=True)

                date = tds[4].get_text(strip=True)

                search_data.append([detail_url, title, date, magnet, size])

        # pp(search_data)
        show_data = []

        # async = False
        async = True
        if async:
            ## ASYNCHRONOUS
            # socket.setdefaulttimeout(3.05)
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                res = {
                    executor.submit(self._get_details, torrent): torrent for torrent in search_data
                }
                for future in concurrent.futures.as_completed(res):
                    results = future.result()
                    show_data.append(results)

        else:
            ## SYNCHRONOUS
            for torrent in search_data:
                show_data.append(self._get_details(torrent))

        return show_data


    def _get_details(self, torrent):

        url = '{}{}'.format(self.base_url, torrent[0])

        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError:
            # can't connect, go to next url
            return

        html = r.content
        soup = BeautifulSoup(html, 'html.parser')
        # section = soup.find('div', class_='category-detail')
        # magnet = section.find_all('a')[1]['href']
        seeds = soup.find('span', class_='stat_red').get_text(strip=True)
        seeds = seeds.replace(',', '')
        # date = section.find_all('span')[7].get_text(strip=True)

        # title size date seeds shortname magnet
        data = [torrent[1], torrent[4], torrent[2], seeds, self.shortname, torrent[3]]
        return data


    @staticmethod
    def se_ep(show_title, season, episode):
        season = str(season)
        episode = str(episode)
        search_one = '%s S%sE%s' % (
            show_title,
            season.rjust(2, '0'),
            episode.rjust(2, '0'))

        search_two = '%s %sx%s' % (
            show_title,
            season,
            episode.rjust(2, '0'))

        # eztv doesn't use the search_two style
        # return [search_one, search_two]
        return [search_one]


if __name__ == '__main__':

    p = Provider()
    results = p.search('game of thrones')
    # results = p.search('game of thrones', season=6, episode=6)
    # results = p.search('luther', season=1, episode=5)
    # results = p.search('adf asdf asdf asdf asdf asdf asd f', season=1, episode=5)
    # time: 0:04.74
    pp(results)
    print('>>>len', len(results))
