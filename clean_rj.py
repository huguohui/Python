#!/usr/bin/python
# coding=utf-8

import os
import shutil

RJ_DIR = 'C:\\Users\\User\\Downloads\\rj'


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


if __name__ == '__main__':
    clean()
