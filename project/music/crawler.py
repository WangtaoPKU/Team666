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
import argparse;

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
	list_link = [];
	for i in range(10):
		link = browser.find_element_by_xpath('//div[@class="srchsongst"]/div[%d]/div[@class="td w0"]/div[@class="sn"]/div[@class="text"]/a' % (i + 1));
		link = link.get_attribute("href");
		list_link.append(link);

	list_link = [x.split("=")[-1] for x in list_link];

	browser.close();

	return list_link;

if __name__ == "__main__":
	parser = argparse.ArgumentParser(prog="download", conflict_handler = "resolve");
	parser.add_argument("--key", "-k", type = str, required = True, help = "key word of the music to search");
	args = parser.parse_args();

	#name = "久石让"
	name = args.key;
	result = search(name);
	print(result)
