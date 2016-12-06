# -*- coding: utf-8 -*-
# Wrapper APIs of server to be reported
import requests
import json
import logging

LOG = logging.getLogger()

from config import settings

def __do_get(url):
    try:
        re = requests.get(url)
        ret = {
            'success': True,
            'status': re.status,
            'data': re.json()
        }
    except Exception, e:
        ret = {
            'success': False,
            'data': e
        }
    return ret

def __do_post(url, data):
    try:
        re = requests.post(url, data=json.dumps(data))
        ret = {
            'success': True,
            'status': re.status
        }
    except Exception, e:
        ret = {
            'success': False,
            'data': e
        }
    return ret

def send_report(data):
    if not isinstance(data, dict) and \
            not isinstance(data, list):
        raise ValueError('Bad value, must be dict or list')
    url = settings['report_server_ip'] + '/'
    # return __do_post(url, data)
    LOG.debug("send report:\n%s" % data)
    # print "send report:\n%s" % data
    return True

def send_vm_report(data):
    s_data = {
        'method': '116116',
        'data': data,
        'session_id': 'jkjauifgf-ddaa'
    }

# For metadata type
from common import MyThread
import time

import data_collector as dc

class MetadataChecker(MyThread):
    def __init__(self, delay):
        super(MetadataChecker, self).__init__('MetadataChecker', 2)
        self._delay = delay

    def work(self):
        ret = self._check_watch_list()
        if ret['success']:
            watch_list = ret['data']
            watched = dc.proc_watched()
            LOG.debug(watch_list, watched)
            dc.proc_watch(filter(lambda x: x not in watched, watch_list))
            dc.proc_unwatch(filter(lambda x: x not in watch_list, watched))
        # TODO: If use metadata server, send all alive proc's info in interal
        time.sleep(self._delay)
    
    def _check_watch_list(self):
        url = settings['report_server_ip'] + '/watchlist'
        # return __do_get(url)
        return {
            'success': True,
            'data': [1, 2, 3, 4, 5, 6]
        }

meta_checker = MetadataChecker(3)

