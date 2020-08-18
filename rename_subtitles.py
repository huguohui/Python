#!/usr/bin/python
# coding=utf-8

import os
import re
import shutil

from pypinyin import lazy_pinyin

DS = '\\'


def lastIndexOf(strings, substr):
    lastIdx = 0
    foundIdx = 0
    while True:
        lastIdx = strings.find(substr, lastIdx)
        if (lastIdx != -1):
            foundIdx = lastIdx
            lastIdx += 1
        else:
            break

    return foundIdx


def backupFile(_dir, name):
    _dir = _dir.rstrip(DS)
    backupDir = _dir + DS + 'backup'
    if (not os.path.isdir(backupDir)):
        os.mkdir(backupDir)

    if (not os.path.isfile(backupDir + DS + name)):
        print('> 备份文件{} => {}'.format(_dir + DS + name, backupDir + DS + name))
        shutil.copyfile(_dir + DS + name, backupDir + DS + name)


def doRename(videoName, subtitleName, vdir, sdir):
    assert len(videoName) != 0
    assert len(subtitleName) != 0

    videoName = videoName[0:lastIndexOf(videoName, '.')]
    subtitleSuffix = subtitleName[lastIndexOf(subtitleName, '.'):]
    sdir = sdir.rstrip(DS)
    vdir = vdir.rstrip(DS)
    # backupFile(sdir, subtitleName)

    print('> 重命名文件{}\n ↓ \n{}'.format(sdir + DS + subtitleName,
                                      vdir + DS + videoName + subtitleSuffix))
    os.rename(sdir + DS + subtitleName, vdir + DS + videoName + subtitleSuffix)


def cutNumsAtStart(chars):
    numChars = ''
    for c in chars:
        if (c.isnumeric()):
            numChars += c

    return numChars


def startsWithNum(chars):
    return chars[0].isnumeric()


def renameSubtitles(videoDir, subtitleDir):
    assert os.path.isdir(videoDir), '视频路径不是文件夹！'
    assert os.path.isdir(subtitleDir), '字幕路径不是文件夹！'

    videoNames = [
        f for f in os.listdir(videoDir)
        if (not os.path.isdir(videoDir.rstrip(DS) + DS + f))
    ]
    subtitleNames = [
        f for f in os.listdir(subtitleDir)
        if (not os.path.isdir(subtitleDir.rstrip(DS) + DS + f))
    ]
    subtitleTypeRe = re.compile('\\.(ass|srt|ssa|smi|sub)$', re.IGNORECASE)

    def cmpFunc(char):
        char = char[0:lastIndexOf(char, '.')]
        for c in char:
            if '\u4e00' <= char <= '\u9fff':
                return '\u007f' + lazy_pinyin(char)[0][0]

        return char

    assert len(videoNames) == len(subtitleNames), '视频字幕数量不一致'

    nNums = [[], []]
    nNotNums = [[], []]
    i = 0
    while i < len(videoNames):
        names = [videoNames[i], subtitleNames[i]]
        for idx, name in enumerate(names):
            if name[0:lastIndexOf(name, '.')].isnumeric() or startsWithNum(name):
                nNums[idx].append(name)
            else:
                nNotNums[idx].append(name)

        i += 1

    for arr in [nNums[0], nNums[1]]:
        arr.sort(key=lambda x: int(cutNumsAtStart(x[0:lastIndexOf(x, '.')])))

    for arr in [nNotNums[0], nNotNums[1]]:
        arr.sort(key=cmpFunc)

    videoNames = nNums[0] + nNotNums[0]
    subtitleNames = nNums[1] + nNotNums[1]
    for idx, name in enumerate(videoNames):
        if not subtitleTypeRe.search(subtitleNames[idx]):
            print("! {}不是一个字幕文件!".format(subtitleNames[idx]))
            break

        # print('{}, {}'.format(idx, name))
        doRename(name, subtitleNames[idx], videoDir, subtitleDir)

    try:
        os.rmdir(subtitleDir)
    except Exception as e:
        pass


def batchRenameSubtitles(directory):
    assert os.path.isdir(directory)

    for name in os.listdir(directory):
        vdir = directory.rstrip(DS) + DS + name
        sdir = directory.rstrip(DS) + DS + name + DS + 'sub'
        if (not os.path.isdir(sdir)):
            continue

        if (len(os.listdir(sdir)) == 0):
            os.rmdir(sdir)
            continue

        print("> 进入文件夹：{}".format(vdir))
        renameSubtitles(vdir, sdir)


#batchRenameSubtitles(input("输入文件夹:"))

renameSubtitles(input("video: "), input("subtitle: "))
