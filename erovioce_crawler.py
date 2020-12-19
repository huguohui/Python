#!/usr/bin/python
#coding=utf-8

import time, sys, os, traceback, re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from multiprocessing import Process


#get直接返回，不再等待界面加载完成
# desired_capabilities = DesiredCapabilities.CHROME
# desired_capabilities["pageLoadStrategy"] = "none"


TEMP_DIR = 'D:\\Files\\log.txt'
RJ_CODES_FILE = 'D:\\Files\\rjCodes.txt'
INVALID_FILE = 'D:\\Files\\invalid.txt'
DRIVER_PATH = 'D:\\Files\\Single Executable\\chromedriver.exe'
DEFAULT_PAGE_NO = 1
PAGE_SIZE = 20
SKIP_NUM = 0
CRAWL_URL = 'http://ww8.erovoice.us/'
curPageNo = DEFAULT_PAGE_NO
jsTpl = 'window.open("{}")'
rjFileName = ''
driver = ''
end = False

downloadedRJs = []
curWindow = None

def switchWindow(wh):
	global curWindow
	window = driver.switch_to.window(wh)
	curWindow = window if window else driver


def openWindow(url, isSwitch = False):
	js = jsTpl.format(url)
	curWindow.execute_script(js)

	if (isSwitch):
		switchWindow(lastWindow())


def windowHandles():
	global driver
	return driver.window_handles


def lastWindow():
	return windowHandles()[-1]


def firstWindow():
	return windowHandles()[0]


def closeWindow(handle):
	switchWindow(handle)
	curWindow.close()
	switchWindow(lastWindow())


def closeWindowExceptFirst():
	for i in range(len(windowHandles()) - 1, 0, -1):
		closeWindow(windowHandles()[i])


APPEAR = 0
DISAPPEAR = 1

def waitUntilStatus(sel, status, interval = 0.2, timeout = 5):
	waitUntil(sel, lambda e : status == APPEAR and e or status == DISAPPEAR and not e, interval, timeout)


def waitUntil(sel, condition, interval = 0.2, timeout=5):
	waitTime = 0
	while True:
		time.sleep(interval)
		ele = None
		try:
			if sel[0] == '/':
				ele = curWindow.find_elements_by_xpath(sel)
			else:
				ele = curWindow.find_element_by_css_selector(sel)
		except Exception as e:
			pass

		waitTime += interval
		if (waitTime >= timeout or ele and condition(ele)):
			break


def waitFor(condition, timeout):
	interval = 0.3
	count = 0
	while True:
		time.sleep(interval)
		count += interval
		if count >= timeout or condition():
			break


def openDetailPage(ele):
	global rjFileName
	openWindow(ele.get_attribute('href'), True)
	divs = curWindow.find_elements_by_xpath('//div[@class="cover"]/div')
	text = ''
	for div in divs:
		if 'File' in div.text:
			text = div.text

	rjFileName = curWindow.title
	aEles = curWindow.find_elements_by_xpath('//div[@class="cover"]//a')

	return text, aEles[len(aEles) - 1]


def findByCssSelector(selector):
	ele = None
	try:
		ele = curWindow.find_element_by_css_selector(selector)
	except Exception as e:
		traceback.print_exc()
	return ele


def downloadShareFile():
	waitUntilStatus('#overlay', APPEAR, timeout = 10)
	curWindow.find_element_by_css_selector('#overlay').click()
	curWindow.find_element_by_css_selector('#btndl').click()
	btn = curWindow.find_element_by_css_selector('.box a')

	if not btn:
		global end
		msgElement = findByCssSelector('.box center')
		if msgElement:
			msgText = msgElement.text

		if 'Error' in msgText:
			if 'has been exceeded' in msgText:
				end = True
			raise Exception(msgText)


	btn.click()


def downloadYuuDriveFile():
	global end
	btn = findByCssSelector('button[data-target="dl"]')
	if not btn:
		raise Exception('')

	btn.click()
	alert = findByCssSelector('div.alert')
	if alert:
		if 'storage was full' in alert.text:
			end = True
		raise Exception(alert.text)


SIZE_SKIP = 1
def openDownloadPage(text, a):
	downloadSite = a.text
	searched = re.search('(\\d+(?:\\.\\d+)?)\\s*(\\w)', text)
	size = float(searched.group(1))
	unit = searched.group(2)
	if not size or size < SIZE_SKIP and unit == 'M':
		print(f' - 跳过小于{SIZE_SKIP}M的文件')
		return False

	openWindow(a.get_attribute('href'), True)
	waitUntilStatus('.disabled', DISAPPEAR)
	curWindow.find_element_by_css_selector('#btn-main').click()

	waitUntilStatus('.disabled', DISAPPEAR)
	curWindow.find_element_by_css_selector('#btn-main').click()

	try:
		if 'Sharer' in downloadSite:
			downloadShareFile()
		elif 'YuuDrive' in downloadSite:
			downloadYuuDriveFile()

	except Exception as e:
		traceback.print_exc()
		if size >= 150:
			with open(INVALID_FILE, 'a', encoding='utf-8') as file:
				file.write(rjFileName)
				file.write('\n')

		if end:
			exit(0)
		return False

	WebDriverWait(curWindow, 5).until(EC.title_contains("Google"))
	return True


def tryJs(js):
	try:
		curWindow.execute_script(js)
	except Exception as e:
		return False

	return True


def crawlPage(ele):
	a, b = openDetailPage(ele)
	return openDownloadPage(a, b)


def openListPage(num):
	# tpl = 'redirectlabel({})'
	tpl = 'redirectpage({})'
	js = tpl.format(num)
	waitFor(lambda: tryJs(js), 10)

	curWindow.execute_script(js)
	waitUntil('.pagecurrent', lambda e : int(e.text) == num, 0.5, 6)


def writeRJName(rjName):
	downloadedRJs.extend(rjName)
	with open(RJ_CODES_FILE, 'a', encoding='utf-8') as file:
		file.write(rjName)
		file.write('\n')


def readRJNames():
	global downloadedRJs

	if os.path.isfile(RJ_CODES_FILE):
		with open(RJ_CODES_FILE, 'r', encoding='utf-8') as file:
			while line := file.readline():
				downloadedRJs.extend([line.strip()])


def isDownloadedRJ(rjName):
	return rjName in downloadedRJs


def readCrawlerInfo():
	file = open(TEMP_DIR, 'r', encoding='utf-8')
	file.seek(0)
	line = file.readline()
	a = int(line) if (line) else DEFAULT_PAGE_NO
	line = file.readline()
	b = int(line) if (line and int(line) < PAGE_SIZE) else SKIP_NUM
	file.close()
	return a, b


def writeCrawlerInfo(driver, records):
	file = open(TEMP_DIR, 'w', encoding='utf-8')
	for record in records:
		file.write(str(record))
		file.write("\n")

	file.write(driver.current_url)
	file.flush()
	file.close()


def getOptions():
	options = webdriver.ChromeOptions()
	options.binary_location = r"C:\Users\hgh\AppData\Local\CentBrowser\Application\chrome.exe"
	options.add_argument(r'user-data-dir=C:\Users\hgh\AppData\Local\CentBrowser\User Data')
	options.add_argument('blink-settings=imagesEnabled=false') # 不加载图片
	# options.add_argument('--headless') # 无界面
	# options.add_argument('--disable-gpu')
	return options


def openBrowser():
	global driver, curWindow
	driver = webdriver.Chrome(DRIVER_PATH, options=getOptions())
	curWindow = driver


def closeBrowser():
	driver.quit()


def fetchPage():
	global curPageNo, rjFileName
	switchWindow(firstWindow())

	readRJNames()
	curPageNo, nextIdx = readCrawlerInfo()
	openListPage(curPageNo)
	elements = driver.find_elements_by_xpath("//a[@class='anes']")

	for i, ele in enumerate(elements):
		if i < nextIdx or isDownloadedRJ(ele.text):
			continue

		switchWindow(firstWindow())
		if crawlPage(ele):
			writeRJName(rjFileName)

		closeWindowExceptFirst()
		writeCrawlerInfo(driver, [curPageNo, i + 1, rjFileName])

	curPageNo += 1
	writeCrawlerInfo(driver, [curPageNo, 0, rjFileName])
	fetchPage()


def doWork():
	openBrowser()
	try:
		driver.get(CRAWL_URL)
		fetchPage()
	finally:
		closeBrowser()


if __name__ == '__main__':
	while not end:
		try:
			doWork()
		except Exception as e:
			traceback.print_exc()

		time.sleep(1)

	if (sys.argv[1] == '-s' and end):
		os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0') # 休眠
		# os.system('shutdown /s /f')	