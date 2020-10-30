#! /usr/bin/env python3

import subprocess


def main():
    subprocess.Popen(['git', 'clone', 'https://github.com/Bug18/PiNASv3.git'])
    subprocess.Popen(['cd', 'PiNASv3'])
    subprocess.Popen(['mkdir', 'templates'])
    subprocess.Popen(['mkdir', 'static'])
    subprocess.Popen(['mv', '*.html', 'templates'])
    subprocess.Popen(['mv', '*.jpg', 'static'])
    subprocess.Popen(['nano', 'README.md'])


if __name__ == '__main__':
    main()
