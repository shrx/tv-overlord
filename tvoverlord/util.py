"""
A collection of random utility functions

To see some simple tests, run:
$ python3 Util.py
"""


class U:
    """Utility class containing useful stuff"""

    _esc = "[%im"

    _blackf = _esc % 30
    _redf = _esc % 31
    _greenf = _esc % 32
    _yellowf = _esc % 33
    _bluef = _esc % 34
    _purplef = _esc % 35
    _cyanf = _esc % 36
    _whitef = _esc % 37

    _blackb = _esc % 40
    _blueb = _esc % 44
    _cyanb = _esc % 46
    _greenb = _esc % 42
    _purpleb = _esc % 45
    _redb = _esc % 41
    _whiteb = _esc % 47
    _yellowb = _esc % 43

    _boldon = _esc % 1
    _boldoff = _esc % 22
    _italicon = _esc % 3
    _italicoff = _esc % 23
    _ulon = _esc % 4
    _uloff = _esc % 24
    _invon = _esc % 7
    _invoff = _esc % 27
    _strikeon = _esc % 9
    _strikeoff = _esc % 29

    _reset = _esc % 0

    ansi_colors = ('black', 'red', 'green', 'yellow',
                   'blue', 'magenta', 'cyan', 'white')

    @staticmethod
    def style(text, fg=None, bg=None, bold=None, italic=None, ul=None,
              strike=None, inv=None, reset=True):
        bits = []

        if fg in U.ansi_colors:
            bits.append(U._esc % (U.ansi_colors.index(fg) + 30))
        elif isinstance(fg, int) and 16 <= fg <= 231:
            bits.append('[38;5;%sm' % fg)

        if bg in U.ansi_colors:
            bits.append(U._esc % (U.ansi_colors.index(bg) + 40))
        elif isinstance(bg, int) and 16 <= bg <= 231:
            bits.append('[48;5;%sm' % bg)

        if bold:
            bits.append(U._boldon)

        if italic:
            bits.append(U._italicon)

        if ul:
            bits.append(U._ulon)

        if strike:
            bits.append(U._strikeon)

        if inv:
            bits.append(U._invon)

        bits.append(text)

        # if text has had any effects applied to it, add the reset
        # string, else just return the plain string.
        if reset and len(bits) > 1:
            bits.append(U._reset)

        return ''.join(bits)

    @staticmethod
    def is_odd(val):
        return val % 2 and True or False

    @staticmethod
    def snip(text, length, sep=None):
        if not sep:
            sep = "\u2026"

        if length in (1, 2):
            return text[:length]

        if len(text) <= length:
            return text

        if U.is_odd(length):
            end_half = 0
        else:
            end_half = 1

        short_mid = int(length / 2)
        start = text[0: short_mid]
        end = text[short_mid + end_half - short_mid * 2: len(text)]

        return start + sep + end

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

    import click

    line = "-" * 50

    print("\nTesting U.snip -- U.snip (<text>, <length>)\n", line)

    seq = "abcdefghijklmnopqrstuvwxyz"
    for j in (13, 14):
        for i in range(10, 20):
            click.echo(">%s<" % (U.snip(seq[0:i], j).ljust(j)))

    click.echo(U.snip('abcd', 1))
    click.echo(U.snip('abcd', 2))
    click.echo(U.snip('abcd', 3))

    print('\nTesting U.style()\n', line)

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
            print(U.style(label, fg=16, bg=k), end=' ')
        print('')

    print('\nNamed colors\n', line)

    for eff in U.ansi_colors:
        print(U.style(eff, fg=16, bg=eff), end=' ')
    print()
    print()

    print(U.style('bold', bold=True))
    print(U.style('italic', italic=True))
    print(U.style('underline', ul=True))
    print(U.style('strike out', strike=True))
    print(U.style('inverse', inv=True))

    print('')
    print(U.style('This text should have bold, underline, and green text',
                  bold=True, ul=True, fg='green'))
