#!/usr/bin/python
#coding=utf-8
import os, sys, io, re, shutil, subprocess
import urllib.request
from bs4 import BeautifulSoup

SOURCE_DIR = "D:\\Files\\Downloads\\rj\\uncompressed"
DESTINATION_DIR = r"D:\Files\Downloads\rj\raw"
MANUAL_HANDLING_DIR = 'D:\\Files\\Downloads\\rj\\manualhandling'
apiUrl = "https://www.dlsite.com/home/work/=/product_id/{}.html"

audioRE = re.compile('\\.(mp3|wav|flac)$', re.IGNORECASE)

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


def fetchRJCodeTilte(rjCode):
	headers = {'User-Agent': 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

	request = urllib.request.Request(apiUrl.format(rjCode), headers = headers)
	urlConnection = urllib.request.urlopen(request)
	response = urlConnection.read()

	html = BeautifulSoup(response, "html.parser")
	element = html.select('#work_name a')
	return element[0].string


def mergeAudio(dst, path):
	assert os.path.isdir(path)

	ext = ""
	for name in os.listdir(path):
		if (audioRE.search(name)):
			ext = name[lastIndexOf(name, '.') + 1:]
			break;

	if (len(ext) != 0):
		fileName = name
		if (path.lower().startswith("rj")):
			fileName = fetchRJCodeTilte(path)

		sourceSplitedMp3 = '"%s/"*.%s' % (path, ext)
		destinationCombineMp3 = ('%s.%s' % (dst, ext)).replace('\\', '\\\\')
		
		if os.path.isfile(destinationCombineMp3):
			return

		cmd = 'cat %s > "%s"' % (sourceSplitedMp3, destinationCombineMp3)
		os.system(cmd)
		print(cmd)


def findAudio(path):
	assert os.path.isdir(path)
	foundDirs = {}
	count = 1
	for name in os.listdir(path):
		fullPath = os.path.join(path, name)
		if (os.path.isdir(fullPath)):
			p = findAudio(fullPath)
			if (p):
				foundDirs.update(p)

		if (audioRE.search(name)):
			foundDirs[path] = count
			count += 1

	return foundDirs


def isNeedManualHandling(paths):
	_max = 0
	for k, v in paths.items():
		if _max == 0:
			_max = v
			continue

		if (v >= _max):
			return True

	return len(paths) > 2 or False


if __name__	== '__main__': # 命令行
	#解决控制台输出报错问题
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

	for name in os.listdir(SOURCE_DIR):
		fullSourcePath = os.path.join(SOURCE_DIR, name)
		audioPaths = findAudio(fullSourcePath)
		audioPathList = list(audioPaths.keys())
		if not len(audioPathList):
			raise Exception('在"%s"中未发现音频文件！' % (name))

		audioPath = audioPathList[0]
		if (isNeedManualHandling(audioPaths)):
			dstManualDir = os.path.join(MANUAL_HANDLING_DIR, name)
			if os.path.isdir(dstManualDir):
				shutil.rmtree(dstManualDir)

			shutil.move(fullSourcePath, MANUAL_HANDLING_DIR)
		else:
			mergeAudio(os.path.join(DESTINATION_DIR, name), audioPath)