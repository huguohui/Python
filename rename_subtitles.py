#!/usr/bin/python
# coding=utf-8

import os, sys
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

def cutNumsAtStart(chars):
    numChars = ''
    for c in chars:
        if (c.isnumeric()):
            numChars += c

    return numChars


def startsWithNum(chars):
    return chars[0].isnumeric()


zeroAsciiCode = ord('0')
nineAsciiCode = ord('9')

def findNumber(string, start = 0):
    idx = start
    numStart = -1
    num = ''

    while idx < len(string):
        numAscii = ord(string[idx])
        if numAscii >= zeroAsciiCode and numAscii <= nineAsciiCode:
            if numStart == -1:
                numStart = idx
            num += string[idx]
        elif numStart != -1:
            break

        idx += 1

    return numStart, num


def dumpArray(array):
    for idx, val in enumerate(array):
        print(val)

def strRepeat(str, times):
    newStr = ''
    for i in range(0, times):
        newStr += str

    return newStr


class FileSorter():

    def __init__(self, files):
        self.fileStartWithNum = []
        self.fileContainNum = []
        self.fileNormal = []
        self.groupInfo = {}
        self.prefixInfo = {}
        self.files = files

    def __cmpFunc(self, char):
        if char in self.groupInfo:
            char = self.handleFileNameForSort(char)

        for c in char:
            if '\u4e00' <= char <= '\u9fff':
                char = ''.join(lazy_pinyin(char))
                break;

        return char

    def handleFileNameForSort(self, char):
        info = self.groupInfo[char][0]
        pInfo = self.prefixInfo[info['prefix']]
        oldNum = info['number']
        newNum = strRepeat('0', len(str(pInfo['count'])) - len(oldNum)) + oldNum
        char = char.replace(oldNum, newNum)
        return char


    def extractNumberAndPrefix(self, name, info = None):
        if info == None or len(info) == 0:
            return None

        idx = 0
        foundInfo = []
        infoList = []
        while True:
            infoList = list(info)
            infoList.extend([name[0:info[0]]])
            foundInfo.extend([infoList])
            info = findNumber(name, info[0] + len(info[1]))
            idx += 1
            if info[0] == -1:
                break;

        return { name : foundInfo }


    def countPrefixAndNumber(self, info):
        for name, arr in info.items():
            if not name in self.groupInfo:
                self.groupInfo[name] = []

            print(arr)
            for val in arr:
                prefix = val[2]
                number = val[1]
                self.groupInfo[name].extend([{
                        'prefix' : prefix,
                        'number' : number
                    }])

                if not prefix in self.prefixInfo:
                    self.prefixInfo[prefix] = {
                        'number' : number,
                        'count' : 1,
                        'numberCount' : 0
                    }
                    continue

                self.prefixInfo[prefix]['count'] += 1
                if self.prefixInfo[prefix]['number'] == number:
                    self.prefixInfo[prefix]['numberCount'] += 1


    def removeUselessInfo(self):
        for name, val in self.groupInfo.items():
            for idx, info in enumerate(val):
                pInfo = self.prefixInfo[info['prefix']]
                if pInfo['count'] == pInfo['numberCount']:
                    del self.groupInfo[name][idx]
                    del pInfo[prefix]


    def analyseNames(self, files):
        for idx, name in enumerate(files):
            pureName = name[0:lastIndexOf(name, '.')]
            if pureName.isnumeric() or startsWithNum(pureName):
                self.fileStartWithNum.append(name)
            else:
                info = findNumber(pureName)
                if info[0] != -1:
                    self.countPrefixAndNumber(self.extractNumberAndPrefix(name, info))

                self.fileNormal.append(name)

        self.removeUselessInfo()


    def sort(self):
        self.analyseNames(self.files)
        self.fileStartWithNum.sort(key=lambda x: int(cutNumsAtStart(x[0:lastIndexOf(x, '.')])))
        self.fileNormal.sort(key=self.__cmpFunc)
        self.files.clear()
        self.files.extend(self.fileStartWithNum + self.fileNormal)


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

    print('> 重命名文件{}\n ↓ \n{}'.format(
            sdir + DS + subtitleName, vdir + DS + videoName + subtitleSuffix))
    os.rename(sdir + DS + subtitleName, vdir + DS + videoName + subtitleSuffix)


def renameSubtitles(videoDir, subtitleDir):
    assert os.path.isdir(videoDir), '视频路径不是文件夹！'
    assert os.path.isdir(subtitleDir), '字幕路径不是文件夹！'
    subtitleTypeRe = re.compile('\\.(ass|srt|ssa|smi|sub)$', re.IGNORECASE)

    videoNames = [
        f for f in os.listdir(videoDir)
        if (not os.path.isdir(videoDir.rstrip(DS) + DS + f))
    ]
    
    subtitleNames = [
        f for f in os.listdir(subtitleDir)
        if not os.path.isdir(subtitleDir.rstrip(DS) + DS + f) and subtitleTypeRe.search(f)
    ]

    assert len(videoNames) == len(subtitleNames), '视频字幕数量不一致'

    FileSorter(subtitleNames).sort()
    FileSorter(videoNames).sort()
    # dumpArray(subtitleNames)
    # dumpArray(videoNames)
    
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


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--batch':
        batchRenameSubtitles(input("输入文件夹:"))
    else:
        videoDir = input("video: ")
        renameSubtitles(videoDir, videoDir + '/sub')
