#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#xiaolei (364350938@qq.com)
#date: 2014-11-25
#update: 2014-11-31
#

import urllib
import requests
from lxml import etree
from lxml.html import soupparser
import re
import random
import chardet
import sys
import chardet
import codecs

reload(sys)
sys.setdefaultencoding('utf-8')


BROWSERS = ['Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3) Gecko/20090913 Firefox/3.5.3',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)',
            'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.1) Gecko/20090718 Firefox/3.5.1',
            'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.1 (KHTML, like Gecko) Chrome/4.0.219.6 Safari/532.1',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; InfoPath.2)',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; SLCC1; .NET CLR 2.0.50727; .NET CLR 1.1.4322; .NET CLR 3.5.30729; .NET CLR 3.0.30729)',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.2; Win64; x64; Trident/4.0)',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; SV1; .NET CLR 2.0.50727; InfoPath.2)Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)',
            'Mozilla/4.0 (compatible; MSIE 6.1; Windows XP)',]

PROXIES = { 'http': 'http://10.192.0.254:8087',
            'https': 'http://10.192.0.254:8087'
            }

class SearchError(Exception):
    """
    Base class for Google Search Exception.
    """

class ParseError(SearchError):
    """
    Parse error in Google results.
    self.msg attribute contains explaination why parsing failed
    self.tag attribute contains BeautifulSoup object with the most relevant tag that failed to parse
    Thorwn only in debug mode
    """
    def __init__(self, msg, tag):
        self.msg = msg
        self.tag = tag

    def __str__(self):
        return self.msg

    def html(self):
        return self.tag.prettify()

#class SearchResult:
#    def __init__(self, title, url, desc):
#        self.title = title
#        self.url = url
#        self.desc = desc
#
#    def __str__(self):
#        return 'Google Search Result: "%s"' % self.title

class GoogleSearch(object):
    #SEARCH_URL_0 = "https://www.google.com.hk/#newwindow=1&safe=strict&q=%(query)s&btnG=Google+Search"
    #NEXT_PAGE_0 = "https://www.google.com.hk/#newwindow=1&safe=strict&q=%(query)s&start=%(start)d"
    #SEARCH_URL_1 = "https://www.google.com.hk/#newwindow=1&safe=strict&q=%(query)s&num=%(num)d&btnG=Google+Search"
    #NEXT_PAGE_1 = "https://www.google.com.hk/#newwindow=1&safe=strict&q=%(query)s&num=%(num)d&start=%(start)d"
    BASE_URL = 'https://www.google.com.hk'

    def __init__(self, results_per_page):
        self.query = None
        self.query_unicode = None
        self.results_per_page = results_per_page
        self.browser = Browser(use_random_agent=True)
        self.results_info = None
        self.eor = False
        self.proxies = dict()
        self._page = 0
        self._MAX_VALUE = 10
        
    def reset_init(self):
        self.eor = False
        self._page = 0
        self._MAX_VALUE = 10
        self.results_info = None

    def _get_results_per_page(self):
      return self._results_per_page
        
    def _set_results_per_page(self, rpp):
        self._results_per_page = rpp

    results_per_page = property(_get_results_per_page, _set_results_per_page)
	
    def get_proxies(self):
        return self.proxies

    def set_proxies(self, proxies):
        self.proxies = proxies
        
    

    def get_results(self, query, max_value):
        """get a page of results"""
        self.reset_init()
        predecoding = chardet.detect(query)['encoding']
        self.query = self.browser.convert_encoding(query)
        print chardet.detect(self.query)
        self.query_unicode = self.query.decode(predecoding)
        print self.query_unicode
        self._MAX_VALUE = max_value
        while self.eor is not True:
            page = self._get_results_page()
            self._extract_results(page)
            search_info = {'from': self.results_per_page*self._page,
                           'to': self.results_per_page*(self._page + 1),
                           'total': self._MAX_VALUE}
            if not self.results_info:
                self.results_info = search_info
            if search_info['to'] == search_info['total']:
                self.eor = True
            self._page += 1


    def _get_results_page(self):
        if self._page == 0:
            if self._results_per_page == 10:
                url = '%(base_url)s/search?q=%(query)s&btnG=Google+Search' % {
                    'base_url': GoogleSearch.BASE_URL, 'query': urllib.quote_plus(self.query)}
            else:
                url = '%(base_url)s/search?q=%(query)s&num=%(num)d&btnG=Google+Search' % {
                    'base_url': GoogleSearch.BASE_URL,
                    'num': self._results_per_page,
                    'query': urllib.quote_plus(self.query)}
        else:
            if self._results_per_page == 10:
                url = '%(base_url)s/search?q=%(query)s&start=%(start)d' %{
                    'base_url': GoogleSearch.BASE_URL,
                    'query': urllib.quote_plus(self.query),
                    'start': self._page * self._results_per_page}
            else:
                url = '%(base_url)s/search?q=%(query)s&start=%(start)d&num=%(num)d' % {
                    'base_url': GoogleSearch.BASE_URL,
                    'query': urllib.quote_plus(self.query),
                    'start': self._page * self._results_per_page,
                    'num': self._results_per_page}

        try:
            page = self.browser.get_page(url, proxies=self.proxies)
        except BrowserError, e:
            raise "BrowserError: Failed getting %s: %s" %(e.url, e.error)

        dom = soupparser.fromstring(page)
        return dom


    def _extract_results(self, soup):
        """extract the url of one search-page"""
        #get the link-urls of a page
        preurls = soup.xpath("//h3[@class='r']/a")
        seedurls = list()
        for url in preurls:
            if 'http://' in etree.tostring(url) or 'https://' in etree.tostring(url):
                seedurls.append(re.search('.*(https?://.*?(?!google)\w+.*?)&', etree.tostring(url)).group(1))
        ret_res = []
        for seedurl in seedurls:
            print chardet.detect(seedurl)
            eres = self._filter_result(seedurl)
            if eres:
                ret_res.append(eres)
        return ret_res

    def _filter_result(self, seedurl):
        """open the urls returned by _extract_results() and return the content"""
        filter_meta = dict()
        page_text = ''
        try:
            # 返回encode字符串
            page_text = self.browser.get_page(seedurl, proxies=self.proxies)
            print 'page_text:' + chardet.detect(page_text)['encoding']
            #dom = soupparser.fromstring(page_text)
        except BrowserError, e:
            raise SearchError, "Failed getting %s: %s" %(e.url, e.error)
            return None
        if page_text.startswith('Timeout'):
            print page_text
            return None
        else:
            relist = re.findall(self.query_unicode.encode(chardet.detect(page_text)['encoding']), page_text)
            if len(relist) >= 1:
                #filter_meta['title'] = page_title
                filter_meta['url'] = seedurl
                filter_meta['query_word'] = self.query_unicode
                filter_meta['text'] = page_text
                filter_meta['match_counts'] = len(relist)
            #return filter_meta
                self.write_content(filter_meta)
            
    def write_content(self, result, out_file=None):
        if out_file is not None:
            dest_file = out_file
        else:
            dest_file = u'output\\' + \
                        result['query_word'] + \
                        '_' + str(result['match_counts']) + \
                        '_' + result['url'].split('/')[2] + \
                        u'.txt'
            #print chardet.detect(dest_file)
                        
        with open(dest_file, 'a') as f:
            #f.write('Match Times: %s \n' % result['match_counts'])
            #f.write('Url: %s \n\n\n' % result['url'])
            f.write(result['text'])

class BrowserError(Exception):
    def __init__(self, url, error):
        self.url = url
        self.error = error

class Browser(object):
    def __init__(self, use_random_agent=True):
        self.proxies = {}
        if use_random_agent:
            self.user_agent = self.set_random_user_agent
        self.headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*,q=0.8',
            'Accept-Language': 'en-us,en;q=0.5'
        }

    def get_page(self, url, proxies=None):
        timeout = 6
        try:
            print "Processing URL: \n %s" % url
            if proxies:
				response = requests.get(url, headers=self.headers,
                        proxies=proxies, verify=False, timeout=timeout)
            else:
				response = requests.get(url, headers=self.headers,
						verify=False, timeout=timeout)
            #return self.convert_encoding(response.text)
            return response.content
        except requests.exceptions.Timeout, e:
            return "[Timeout] : open url timeout \n%s\n " %(url)
        except BrowserError as e:
            raise "Error - %s :Failed to requests %s" %(e.error, e.url)

    @property
    def set_random_user_agent(self):
        user_agent = random.choice(BROWSERS)
        return user_agent
    
    def convert_encoding(self, data, new_coding = 'UTF-8'):
        if isinstance(data, unicode):
            return data.encode(new_coding)
        else:
            encoding = chardet.detect(data)['encoding']
            #print encoding
            if new_coding.upper() != encoding.upper():
                data = data.decode(encoding, 'ignore').encode(new_coding)
            return data
