import termios
import fcntl
import sys
import os
import time


def ask_user(question):
    fd = sys.stdin.fileno()

    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)

    oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags & ~os.O_NONBLOCK)

    print(question, end=' ')
    sys.stdout.flush()

    try:
        while 1:
            time.sleep(0.05)
            try:
                c = sys.stdin.read(1)
                # result = repr(c)
                result = c
                break
            except IOError:
                pass
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)

    if repr(result) == "'\\n'":
        result = '[enter]'
    print(result)

    return result


if __name__ == '__main__':
    question = 'Input any character:'
    result = ask_user(question)
    print('The key pressed was:', result)
