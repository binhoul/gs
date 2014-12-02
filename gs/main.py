#!/usr/bin/python
# -*- coding: utf-8 -*-
# xiaolei (364350938@qq.com)
#Date: 2014-11-26
#update: 2014-11-31
#

import gs
import re
import sys

sys.setdefaultencoding('UTF-8')

def get_query(in_file):
    queries = list()
    try:
        with open(in_file, 'r') as f:
            lines = f.readlines()
    except IOError, e:
        print 'File: %s cannot be opened!' % file
    for line in lines:
        queries.append(line.strip('\n'))
    return queries


if __name__ == '__main__':
    in_file = 'query.txt'
    query_keys = get_query(in_file)
    num = 0
    results_per_page = 10
    proxies = {'http': 'http://127.0.0.1:8087', 'https': 'http://127.0.0.1:8087'}
    max_value = 10
    gser = gs.GoogleSearch(results_per_page)
    gser.set_proxies(proxies)
    for query_key in query_keys:
        print "\n\n****************Google Keyword: {0}********************".format(query_key)
        try:
            gser.get_results(query_key,max_value)
        except KeyboardInterrupt:
            raise