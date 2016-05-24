"""
A collection of random utility functions

To see some simple tests, run:
$ python Util.py
"""

import random


class U:
    """Utility class containing useful stuff"""

    __esc = "[%im"

    __blackf = __esc % 30
    __bluef = __esc % 34
    __cyanf = __esc % 36
    __greenf = __esc % 32
    __purplef = __esc % 35
    __redf = __esc % 31
    __whitef = __esc % 37
    __yellowf = __esc % 33

    __blackb = __esc % 40
    __blueb = __esc % 44
    __cyanb = __esc % 46
    __greenb = __esc % 42
    __purpleb = __esc % 45
    __redb = __esc % 41
    __whiteb = __esc % 47
    __yellowb = __esc % 43

    __boldon = __esc % 1
    __boldoff = __esc % 22
    __italicon = __esc % 3
    __italicoff = __esc % 23
    __ulon = __esc % 4
    __uloff = __esc % 24
    __invon = __esc % 7
    __invoff = __esc % 27
    __strikeon = __esc % 9
    __strikeoff = __esc % 29

    __reset = __esc % 0

    @staticmethod
    def fg_color(color, string):
        if color == "black":
            string = U.__blackf + string
        if color == "blue":
            string = U.__bluef + string
        if color == "green":
            string = U.__greenf + string
        if color == "yellow":
            string = U.__yellowf + string
        if color == "purple":
            string = U.__purplef + string
        if color == "red":
            string = U.__redf + string
        if color == 'cyan':
            string = U.__cyanf + string
        if color == 'white':
            string = U.__whitef + string

        return string + U.__reset

    @staticmethod
    def effects(effects, string):
        fmt_str = []
        for effect in effects:
            if effect == 'blackf':
                fmt_str.append(U.__blackf)
            if effect == 'bluef':
                fmt_str.append(U.__bluef)
            if effect == 'cyanf':
                fmt_str.append(U.__cyanf)
            if effect == 'greenf':
                fmt_str.append(U.__greenf)
            if effect == 'purplef':
                fmt_str.append(U.__purplef)
            if effect == 'redf':
                fmt_str.append(U.__redf)
            if effect == 'whitef':
                fmt_str.append(U.__whitef)
            if effect == 'yellowf':
                fmt_str.append(U.__yellowf)
            if effect == 'blackb':
                fmt_str.append(U.__blackb)
            if effect == 'blueb':
                fmt_str.append(U.__blueb)
            if effect == 'cyanb':
                fmt_str.append(U.__cyanb)
            if effect == 'greenb':
                fmt_str.append(U.__greenb)
            if effect == 'purpleb':
                fmt_str.append(U.__purpleb)
            if effect == 'redb':
                fmt_str.append(U.__redb)
            if effect == 'whiteb':
                fmt_str.append(U.__whiteb)
            if effect == 'yellowb':
                fmt_str.append(U.__yellowb)
            if effect == 'boldon':
                fmt_str.append(U.__boldon)
            if effect == 'boldoff':
                fmt_str.append(U.__boldoff)
            if effect == 'italicon':
                fmt_str.append(U.__italicon)
            if effect == 'italicoff':
                fmt_str.append(U.__italicoff)
            if effect == 'ulon':
                fmt_str.append(U.__ulon)
            if effect == 'uloff':
                fmt_str.append(U.__uloff)
            if effect == 'invon':
                fmt_str.append(U.__invon)
            if effect == 'invoff':
                fmt_str.append(U.__invoff)
            if effect == 'strikeon':
                fmt_str.append(U.__strikeon)
            if effect == 'strikeoff':
                fmt_str.append(U.__strikeoff)

        return ''.join(fmt_str) + string + U.__reset

    @staticmethod
    def hi_color(string, foreground=None, background=None):
        # accept a range from 16 to 231
        if foreground and (foreground < 16 or foreground > 231):
            U.error('number less than 16 or more than 231')
        if background and (background < 16 or background > 2310):
            U.error('number less than 16 or more than 231')

        foreground_pat = background_pat = ''
        if foreground:
            foreground_pat = '[38;5;%sm' % foreground
        if background:
            background_pat = '[48;5;%sm' % background
        reset = '[0m'

        ret_str = foreground_pat + background_pat + string + reset
        return ret_str

    @staticmethod
    def is_odd(val):
        return val % 2 and True or False

    @staticmethod
    def snip(text, length):
        # sep = '+'
        # sep = '0xE2 0x80 0xA6'
        sep = "\u2026"

        if len(text) <= length:
            return text

        if U.is_odd(length):
            end_half = 0
        else:
            end_half = 1

        short_mid = int(length / 2)
        start = text[0: short_mid]
        end = text[short_mid + end_half - short_mid * 2: len(text)]
        # color_sep = U.__greenf + U.__boldon + sep + U.__reset
        color_sep = sep

        return start + color_sep + end

    @staticmethod
    def pretty_filesize(file_bytes):
        file_bytes = float(file_bytes)
        if file_bytes >= 1099511627776:
            terabytes = file_bytes / 1099511627776
            size = '%.2f TB' % terabytes
        elif file_bytes >= 1073741824:
            gigabytes = file_bytes / 1073741824
            size = '%.2f GB' % gigabytes
        elif file_bytes >= 1048576:
            megabytes = file_bytes / 1048576
            size = '%.2f MB' % megabytes
        elif file_bytes >= 1024:
            kilobytes = file_bytes / 1024
            size = '%.2f KB' % kilobytes
        else:
            size = '%.2f b' % file_bytes
        return size


if __name__ == '__main__':

    line = "-" * 50

    print("\nTesting U.snip -- U.snip (<text>, <length>)\n", line)

    seq = "abcdefghijklmnopqrstuvwxyz"
    for j in (13, 14):
        for i in range(10, 20):
            print("%s<" % (U.snip(seq[0:i], j).ljust(j)))

    print('\nTesting U.hi_color() -- U.hi_color (<text>, <foreground>, <background>)\n', line)

    k = int(15)
    for i in range(17, 52):
        pad = ''
        for j in range(6):
            k += 1
            if len(str(k)) == 1:
                pad = '   '
            elif len(str(k)) == 2:
                pad = '  '
            elif len(str(k)) == 3:
                pad = ' '

            label = ' ' + str(k) + pad
            print(U.hi_color(label, foreground=16, background=k), end=' ')
        print('')

    print('\nTest effects -- U.effects (<[effect list]>, <text>)\n', line)

    effects = ['blackf', 'bluef', 'cyanf', 'greenf', 'purplef', 'redf',
               'whitef', 'yellowf', 'blackb', 'blueb', 'cyanb', 'greenb',
               'purpleb', 'redb', 'whiteb', 'yellowb', 'boldon',
               'italicon', 'ulon', 'strikeon']

    for eff in effects:
        print(U.effects([eff], eff), end=' ')
    print()
    print()

    print('Combining effects:')
    for e in range(10):
        item1 = random.choice(effects)
        item2 = random.choice(effects)
        item3 = random.choice(effects)
        print(U.effects([item1, item2, item3],
                        '%s %s %s' % (item1, item2, item3)))

    print('')
    print(U.effects(['boldon', 'ulon', 'greenf'],
                    'This text should have bold, underline, and green text'))
