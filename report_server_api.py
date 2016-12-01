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

