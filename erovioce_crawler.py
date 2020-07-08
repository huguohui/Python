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


TEMP_DIR = 'D:\\TEMP\\log.txt'
DRIVER_PATH = 'D:\\Files\\Single Executable\\chromedriver.exe'
DEFAULT_PAGE_NO = 1
PAGE_SIZE = 20
SKIP_NUM = 0
CRAWL_URL = 'http://ww8.erovoice.us/'
curPageNo = DEFAULT_PAGE_NO
jsTpl = 'window.open("{}")'


def switchWindow(wh):
	global driver
	result = driver.switch_to.window(wh)
	if result:
		driver = d

def openWindow(url, isSwitch = False):
	js = jsTpl.format(url)
	driver.execute_script(js)

	if (isSwitch):
		switchWindow(lastWindow())

def windowHandles():
	global driver
	return driver.window_handles

def lastWindow():
	return windowHandles()[-1]

def firstWindow():
	return windowHandles()[0]

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
				ele = driver.find_elements_by_xpath(sel)
			else:
				ele = driver.find_element_by_css_selector(sel)
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
	divs = driver.find_elements_by_xpath('//div[@class="cover"]/div')
	text = ''
	for div in divs:
		if 'File' in div.text:
			text = div.text

	rjFileName = driver.title
	return text, driver.find_elements_by_xpath('//div[@class="cover"]//a')[1]

def openDownloadPage(text, a):
	searched = re.search('(\\d+(?:\\.\\d+)?)\\s*(\\w)', text)
	size = float(searched.group(1))
	unit = searched.group(2)
	if not size or size < 80 and unit == 'M':
		print(' - 跳过小于80M的文件')
		return False

	openWindow(a.get_attribute('href'), True)
	waitUntilStatus('.disabled', DISAPPEAR)
	driver.find_element_by_css_selector('#btn-main').click()

	waitUntilStatus('.disabled', DISAPPEAR)
	driver.find_element_by_css_selector('#btn-main').click()

	waitUntilStatus('#overlay', APPEAR, timeout = 10)
	driver.find_element_by_css_selector('#overlay').click()
	driver.find_element_by_css_selector('#btndl').click()

	try:
		waitUntilStatus('.box a', APPEAR)
		driver.find_element_by_css_selector('.box a').click()
	except Exception as e:
		global end
		msgElement = driver.find_element_by_css_selector('.box center')
		if msgElement:
			msgText = msgElement.text
			print(msgText)

		if 'Error' in driver.page_source:
			if 'File not found' in driver.page_source:
				driver.close()
				return False
			end = True

		raise e

	try:
		WebDriverWait(driver, 5).until(EC.title_contains("Google"))
	except Exception as e:
		pass

	return True

def tryJs(js):
	try:
		driver.execute_script(js)
	except Exception as e:
		return False

	return True

def openAllPage(ele):
	a, b = openDetailPage(ele)
	return openDownloadPage(a, b)

def openListPage(num):
	global driver
	# tpl = 'redirectlabel({})'
	tpl = 'redirectpage({})'
	js = tpl.format(num)
	waitFor(lambda: tryJs(js), 10)
	driver.execute_script(js)
	waitUntil('.pagecurrent', lambda e : int(e.text) == num, 0.5, 6)

def closePage():
	driver.close()
	switchWindow(lastWindow())
	driver.close()
	switchWindow(lastWindow())

def readRecord():
	file = open(TEMP_DIR, 'r', encoding='utf-8')
	file.seek(0)
	line = file.readline()
	a = int(line) if (line) else DEFAULT_PAGE_NO
	line = file.readline()
	b = int(line) if (line and int(line) < PAGE_SIZE) else SKIP_NUM
	file.close()
	return a, b

def writeRecord(records):
	file = open(TEMP_DIR, 'w', encoding='utf-8')
	for record in records:
		file.write(str(record))
		file.write("\n")

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
	global driver
	driver = webdriver.Chrome(DRIVER_PATH, options=getOptions())

def closeBrowser():
	driver.quit()

rjFileName = ''
def fetchPage():
	global curPageNo, rjFileName
	switchWindow(firstWindow())
	curPageNo, nextIdx = readRecord()
	openListPage(curPageNo)
	elements = driver.find_elements_by_xpath("//a[@class='anes']")

	for i, ele in enumerate(elements):
		if (i < nextIdx):
			continue

		switchWindow(firstWindow())
		if openAllPage(ele):
			closePage()
		else:
			driver.close()
		writeRecord([curPageNo, i + 1, rjFileName])

	curPageNo += 1
	writeRecord([curPageNo, 0, rjFileName])
	fetchPage()

def doWork():
	openBrowser()
	try:
		driver.get(CRAWL_URL)
		fetchPage()
	finally:
		closeBrowser()


if __name__ == '__main__':
	driver = ''
	end = False

	while not end:
		try:
			doWork()
		except Exception as e:
			traceback.print_exc()

		time.sleep(1)

	if (sys.argv[1] == '-s' and end):
		os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0') # 睡眠
		# os.system('shutdown /s /f')	