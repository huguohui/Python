#!/usr/bin/python
# coding=utf-8


import os
import re
import shutil
import subprocess
import sys

UNRAR_EXECUTABLE = 'C:\\Program Files\\WinRAR\\unrar.exe'
COMPRESS_FILE_DIR = "D:\\Files\\Downloads\\rj\\compressed"
UNCOMPRESS_DIR = "D:\\Files\\Downloads\\rj\\uncompressed"
TEMP_DIR = "D:\\temp"

compressFileRE = re.compile('\\.(rar|zip|7z|xz|bz2?|ace|gz)$', re.IGNORECASE)
nonSuffixFileRE = re.compile('[^.]+', re.IGNORECASE)
shutdownAtEnd = False


def setShutdownAtEnd():
    global shutdownAtEnd
    shutdownAtEnd = True


def clean():
    cleanDirs = ['uncompressed', 'raw', 'compressed']
    for _dir in cleanDirs:
        fullSubDir = os.path.join(RJ_DIR, _dir)
        for file in os.listdir(fullSubDir):
            deleteFile = os.path.join(fullSubDir, file)
            if os.path.isdir(deleteFile):
                shutil.rmtree()
            else:
                os.remove(deleteFile)


def uncompress(path, name, dstDir):
    fullName = os.path.join(path, name)
    sp = subprocess.Popen([UNRAR_EXECUTABLE, 'x', '-y', fullName, dstDir])
    sp.wait()


def shutdown():
    os.system('shutdown /s /f')


def execCommand():
    for i, arg in enumerate(sys.argv):
        if i != 0:
            commands[arg]()


commands = {
    '-c': clean,
    '-s': setShutdownAtEnd
}

if __name__ == '__main__':
    execCommand()
    for name in os.listdir(COMPRESS_FILE_DIR):
        uncompress(COMPRESS_FILE_DIR, name, UNCOMPRESS_DIR)

    if shutdownAtEnd:
        shutdown()
