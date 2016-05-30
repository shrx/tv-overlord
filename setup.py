from distutils.core import setup
import os
import sys

if sys.version_info[0] == 2:
    dividers = '!' * 40
    sys.exit("{}\nSorry, TVOverlord does not support python 2.\nUse: 'pip3 install tvoverlord' instead\n{}".format(dividers, dividers))

f = open(os.path.join(os.path.dirname(__file__), 'README.txt'))
long_description = f.read()
f.close()

setup(
    name='tvoverlord',
    packages = ['tvoverlord', 'tvoverlord_util', 'tvoverlord/search_providers'],
    package_data = {
        'tvoverlord': ['config.ini'],
        'tvoverlord_util': ['*'],
    },
    data_files = [
        ('/etc/bash_completion.d', ['tvoverlord_util/tvoverlord-completion.bash']),
    ],
    scripts = ['tvol', 'transmission_done.py', 'deluge_done.py'],
    install_requires = [
        'tvdb_api',
        'beautifulsoup4',
        'feedparser',
        'requests',
        'docopt',
        'python-dateutil',
        'appdirs',
        'psutil',
    ],
    version = '0.9.15',
    description = 'TV Overlord is a command line tool to download and manage TV shows from newsgroups or bittorent',
    long_description = long_description,
    license = 'MIT',
    author = 'Sheldon McGrandle',
    author_email = 'developer@8cylinder.com',
    url = 'https://github.com/8cylinder/tv-overlord',
    keywords = [],
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Topic :: Internet',
        'Topic :: Multimedia :: Video',
        'Natural Language :: English',
        'Development Status :: 4 - Beta',
    ],
)

# python3 setup.py check
# python3 setup.py sdist
# python3 setup.py register sdist upload

# future windows builds:
# python3 setup.py bdist_wininst
# python3 setup.py register sdist bdist_wininst upload
