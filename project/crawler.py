# -*- coding: utf-8 -*-

import re;
import os;
import sys;
import time;
from urllib import request;
from selenium import webdriver;
from selenium.webdriver.common.by import By as by;
from selenium.webdriver.common.keys import Keys as keys;
from selenium.webdriver.support import expected_conditions as exp_cond;
from selenium.webdriver.support.wait import WebDriverWait as webdriver_wait;
from selenium.common.exceptions import TimeoutException;
from selenium.webdriver.firefox.options import Options as options;

def search(name):
	url = "https://music.163.com/"
	opt = options();
	opt.headless = False;
	browser = webdriver.Firefox(options = opt);
	browser.get(url);

	time.sleep(2);
	input_search = browser.find_element_by_id("srch");
	input_search.send_keys(name);
	input_search.send_keys(keys.ENTER);
	time.sleep(2);

	browser.switch_to.frame("contentFrame");
	link = browser.find_element_by_xpath('//div[@class="sn"]/div[@class="text"]/a');
	link = link.get_attribute("href");

	browser.get(link);
	time.sleep(2);
#	link = browser.find_element_by_xpath('//a[@class="u-btn2 u-btn2-2 u-btni-addply f-fl"]');
#	print(link);
#	link.click();

	page = browser.page_source;
	result = page;
#	browser.close();
#	result = ""
	return result;

name = "久石让"
result = search(name);
print(result)
