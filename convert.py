#!/usr/bin/python
#coding=utf-8

import time, sys, os, subprocess, json

RJ_RAW_DIR = r"C:\Users\User\Downloads\rj\raw"
RJ_CONVERTED_DIR = r"C:\Users\User\Downloads\rj\converted"
RJ_LOW_BIT_RATE_DIR = r"C:\Users\User\Downloads\rj\lowbitrate"
EXCEPTED_BIT_RATE = 320000
FFPROBE = 'ffprobe'
FFMPEG = 'ffmpeg'

def checkBitrate(fullName, name):
	sp = subprocess.Popen([
				FFPROBE, "-loglevel", "quiet", "-print_format", 
				"json", '-show_format', fullName
			], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	
	infoJson = sp.stdout.read()
	info = json.loads(infoJson)
	bitRate = info['format']['bit_rate']
	if bitRate and int(bitRate) >= EXCEPTED_BIT_RATE:
		return True

	return False

def convert(path, name):
	fullName = os.path.join(path, name)
	outputFullName = os.path.join(RJ_CONVERTED_DIR, name)
	cmd = r'ffmpeg -y -threads 10 -i "%s" -ab 192k "%s"' % (fullName, outputFullName)
	sp = subprocess.Popen(cmd, shell=True)
	sp.wait()

if __name__ == '__main__':
	for name in os.listdir(RJ_RAW_DIR):
		fullName = os.path.join(RJ_RAW_DIR, name)
		if checkBitrate(fullName, name):
			convert(RJ_RAW_DIR, name)
		else:
			os.rename(fullName, os.path.join(RJ_LOW_BIT_RATE_DIR, name))

	if len(sys.argv) > 1 and sys.argv[1] == '-s':
		os.system('shutdown /s /f')